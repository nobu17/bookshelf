from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from html import unescape
from html.parser import HTMLParser
import json
import re
from sqlalchemy import delete
from urllib.error import HTTPError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

from bookshelf_app.config import get_settings
from bookshelf_app.infra.db.book_search import BookMetadataCacheDTO, PublisherCatalogCacheDTO
from bookshelf_app.infra.db.database import SessionLocal


PUBLISHER_CATALOG_CACHE_DAYS = 3
PUBLISHER_CATALOG_MAX_ITEMS = 1000
GOOGLE_CATALOG_SUPPLEMENT_MAX_ITEMS = 40
BOOK_METADATA_CACHE_DAYS = 30


class BookSearchRateLimitError(Exception):
    pass


@dataclass(frozen=True)
class BookSearchResultAppModel:
    source: str
    source_id: str
    title: str
    authors: list[str]
    publisher: str
    isbn13: str
    published_at: date
    image_url: str | None
    description: str | None = None


@dataclass(frozen=True)
class PublisherAppModel:
    publisher_id: str
    name: str


@dataclass(frozen=True)
class PublisherCatalogBookAppModel:
    isbn13: str
    title: str
    published_at: date
    price: str | None = None
    source_url: str | None = None


@dataclass(frozen=True)
class PublisherBookPageAppModel:
    books: list[BookSearchResultAppModel]
    page: int
    page_size: int
    total_count: int


class BookSearchService:
    _google: "GoogleBooksProvider"
    _openbd: "OpenBdProvider"
    _publisher_catalogs: "PublisherCatalogService"

    def __init__(self):
        self._google = GoogleBooksProvider(get_settings().google_books_api_key)
        self._openbd = OpenBdProvider()
        self._publisher_catalogs = PublisherCatalogService(self._google, self._openbd)

    def search(self, keyword: str) -> list[BookSearchResultAppModel]:
        keyword = keyword.strip()
        if not keyword:
            return []

        if is_isbn13(keyword):
            result = self.find_by_isbn13(keyword)
            return [result] if result is not None else []

        return self._google.search(keyword)

    def find_by_isbn13(self, isbn13: str) -> BookSearchResultAppModel | None:
        normalized = normalize_isbn(isbn13)
        google_book = self._find_google_by_isbn13(normalized)
        openbd_book = self._openbd.find_by_isbn13(normalized)

        if google_book and openbd_book:
            return merge_book_search_result(google_book, openbd_book)
        return openbd_book or google_book

    def find_description_by_isbn13(self, isbn13: str) -> str | None:
        result = self.find_by_isbn13(isbn13)
        return result.description if result else None

    def list_publishers(self) -> list[PublisherAppModel]:
        return self._publisher_catalogs.list_publishers()

    def search_publisher_books(
        self, publisher_id: str, keyword: str | None = None, page: int = 1, limit: int = 40
    ) -> PublisherBookPageAppModel:
        return self._publisher_catalogs.search_books(publisher_id, keyword, page, limit)

    def clear_publisher_catalog_cache(self) -> int:
        return clear_publisher_catalog_cache()

    def clear_book_metadata_cache(self) -> int:
        return clear_book_metadata_cache()

    def _find_google_by_isbn13(self, isbn13: str) -> BookSearchResultAppModel | None:
        try:
            return self._google.find_by_isbn13(isbn13)
        except BookSearchRateLimitError:
            return None


class GoogleBooksProvider:
    _api_key: str

    def __init__(self, api_key: str):
        self._api_key = api_key

    def search(self, keyword: str) -> list[BookSearchResultAppModel]:
        books: list[BookSearchResultAppModel] = []
        for query in create_google_search_queries(keyword):
            data = fetch_json(
                "https://www.googleapis.com/books/v1/volumes",
                {
                    "q": query,
                    "printType": "books",
                    "langRestrict": "ja",
                    "orderBy": "newest",
                    "maxResults": "40",
                    "key": self._api_key,
                },
            )
            books.extend([book for item in data.get("items", []) if (book := convert_google_volume(item))])

        return unique_books(books)

    def find_by_isbn13(self, isbn13: str) -> BookSearchResultAppModel | None:
        results = self.search(normalize_isbn(isbn13))
        return results[0] if results else None


class OpenBdProvider:
    def find_by_isbn13(self, isbn13: str) -> BookSearchResultAppModel | None:
        data = fetch_json("https://api.openbd.jp/v1/get", {"isbn": normalize_isbn(isbn13)})
        if not isinstance(data, list) or len(data) < 1:
            return None

        item = data[0]
        if not item or not item.get("summary"):
            return None

        summary = item["summary"]
        isbn = normalize_isbn(summary.get("isbn") or isbn13)
        return BookSearchResultAppModel(
            source="openbd",
            source_id=isbn,
            title=summary.get("title") or "タイトル不明",
            authors=split_authors(summary.get("author") or ""),
            publisher=summary.get("publisher") or "不明",
            isbn13=isbn,
            published_at=parse_published_date(summary.get("pubdate")),
            image_url=normalize_cover_url(summary.get("cover")),
            description=extract_openbd_description(item),
        )

    def find_by_isbn13s(self, isbn13s: list[str]) -> dict[str, BookSearchResultAppModel]:
        normalized_isbns = [normalize_isbn(isbn13) for isbn13 in isbn13s if is_isbn13(isbn13)]
        if not normalized_isbns:
            return {}

        data = fetch_json("https://api.openbd.jp/v1/get", {"isbn": ",".join(normalized_isbns)})
        if not isinstance(data, list):
            return {}

        results: dict[str, BookSearchResultAppModel] = {}
        for fallback_isbn, item in zip(normalized_isbns, data):
            book = convert_openbd_item(item, fallback_isbn)
            if book:
                results[book.isbn13] = book
        return results


class PublisherCatalogService:
    _providers: dict[str, "PublisherCatalogProvider"]
    _google: GoogleBooksProvider
    _openbd: OpenBdProvider

    def __init__(self, google: GoogleBooksProvider, openbd: OpenBdProvider):
        self._providers = {"oreilly_japan": OreillyCatalogProvider()}
        self._google = google
        self._openbd = openbd

    def list_publishers(self) -> list[PublisherAppModel]:
        return [PublisherAppModel(provider.publisher_id, provider.publisher_name) for provider in self._providers.values()]

    def search_books(
        self, publisher_id: str, keyword: str | None = None, page: int = 1, limit: int = 40
    ) -> PublisherBookPageAppModel:
        provider = self._providers.get(publisher_id)
        if provider is None:
            return PublisherBookPageAppModel([], page=max(1, page), page_size=limit, total_count=0)

        books = self._get_catalog_books(provider)
        books = filter_catalog_books(books, keyword)
        books = sorted(books, key=lambda book: book.published_at, reverse=True)
        page_size = max(1, min(limit, 100))
        current_page = max(1, page)
        start = (current_page - 1) * page_size
        selected = books[start : start + page_size]
        return PublisherBookPageAppModel(
            books=self._enrich_books(selected, provider.publisher_name),
            page=current_page,
            page_size=page_size,
            total_count=len(books),
        )

    def _get_catalog_books(self, provider: "PublisherCatalogProvider") -> list[PublisherCatalogBookAppModel]:
        cached = self._load_cache(provider.cache_key)
        if cached is not None:
            return cached

        try:
            books = provider.fetch_books()[:PUBLISHER_CATALOG_MAX_ITEMS]
        except Exception:
            stale = self._load_cache(provider.cache_key, allow_expired=True)
            if stale is not None:
                return stale
            raise

        self._save_cache(provider.cache_key, books)
        return books

    def _load_cache(self, source_key: str, allow_expired: bool = False) -> list[PublisherCatalogBookAppModel] | None:
        with SessionLocal() as session:
            dto = session.get(PublisherCatalogCacheDTO, source_key)
            if dto is None:
                return None
            if not allow_expired and is_cache_expired(dto.expires_at):
                return None
            return catalog_books_from_json(dto.payload_json)

    def _save_cache(self, source_key: str, books: list[PublisherCatalogBookAppModel]) -> None:
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=PUBLISHER_CATALOG_CACHE_DAYS)
        payload = catalog_books_to_json(books)
        with SessionLocal() as session:
            dto = session.get(PublisherCatalogCacheDTO, source_key)
            if dto is None:
                dto = PublisherCatalogCacheDTO(
                    source_key=source_key,
                    payload_json=payload,
                    fetched_at=now,
                    expires_at=expires_at,
                    is_deleted=False,
                )
                session.add(dto)
            else:
                dto.payload_json = payload
                dto.fetched_at = now
                dto.expires_at = expires_at
                dto.is_deleted = False
            session.commit()

    def _enrich_books(
        self, books: list[PublisherCatalogBookAppModel], publisher_name: str
    ) -> list[BookSearchResultAppModel]:
        cached_books = self._load_book_metadata_cache([book.isbn13 for book in books])
        complete_cached_books = {
            isbn13: book for isbn13, book in cached_books.items() if book.image_url
        }
        supplement_books = [
            book for book in books if book.isbn13 not in complete_cached_books
        ]
        if not supplement_books:
            return [complete_cached_books[book.isbn13] for book in books if book.isbn13 in complete_cached_books]

        openbd_target_books = [book for book in supplement_books if book.isbn13 not in cached_books]
        openbd_books = self._openbd.find_by_isbn13s([book.isbn13 for book in openbd_target_books])
        fetched_books: dict[str, BookSearchResultAppModel] = {}
        google_call_count = 0
        for book in supplement_books:
            openbd_book = cached_books.get(book.isbn13) or openbd_books.get(book.isbn13)
            google_book = None
            needs_google_supplement = openbd_book is None or not openbd_book.image_url
            if needs_google_supplement and google_call_count < GOOGLE_CATALOG_SUPPLEMENT_MAX_ITEMS:
                google_call_count += 1
                google_book = self._find_google_by_isbn13(book.isbn13)

            if google_book and openbd_book:
                fetched_books[book.isbn13] = merge_book_search_result(google_book, openbd_book)
            elif openbd_book:
                fetched_books[book.isbn13] = openbd_book
            elif google_book:
                fetched_books[book.isbn13] = google_book
            else:
                fetched_books[book.isbn13] = convert_catalog_book(book, publisher_name)

        self._save_book_metadata_cache(list(fetched_books.values()))
        all_books = {**complete_cached_books, **fetched_books}
        return [all_books[book.isbn13] for book in books if book.isbn13 in all_books]

    def _find_google_by_isbn13(self, isbn13: str) -> BookSearchResultAppModel | None:
        try:
            return self._google.find_by_isbn13(isbn13)
        except BookSearchRateLimitError:
            return None

    def _load_book_metadata_cache(self, isbn13s: list[str]) -> dict[str, BookSearchResultAppModel]:
        normalized_isbns = [normalize_isbn(isbn13) for isbn13 in isbn13s if is_isbn13(isbn13)]
        if not normalized_isbns:
            return {}

        results: dict[str, BookSearchResultAppModel] = {}
        with SessionLocal() as session:
            rows = session.query(BookMetadataCacheDTO).filter(BookMetadataCacheDTO.isbn13.in_(normalized_isbns)).all()
            for row in rows:
                if is_cache_expired(row.expires_at):
                    continue
                book = book_search_result_from_json(row.payload_json)
                if book:
                    results[book.isbn13] = book
        return results

    def _save_book_metadata_cache(self, books: list[BookSearchResultAppModel]) -> None:
        if not books:
            return

        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=BOOK_METADATA_CACHE_DAYS)
        with SessionLocal() as session:
            for book in books:
                dto = session.get(BookMetadataCacheDTO, book.isbn13)
                payload = book_search_result_to_json(book)
                if dto is None:
                    dto = BookMetadataCacheDTO(
                        isbn13=book.isbn13,
                        payload_json=payload,
                        fetched_at=now,
                        expires_at=expires_at,
                        is_deleted=False,
                    )
                    session.add(dto)
                else:
                    dto.payload_json = payload
                    dto.fetched_at = now
                    dto.expires_at = expires_at
                    dto.is_deleted = False
            session.commit()


class PublisherCatalogProvider:
    publisher_id: str
    publisher_name: str
    cache_key: str

    def fetch_books(self) -> list[PublisherCatalogBookAppModel]:
        raise NotImplementedError


class OreillyCatalogProvider(PublisherCatalogProvider):
    publisher_id = "oreilly_japan"
    publisher_name = "オライリー・ジャパン"
    cache_key = "oreilly_japan_catalog"
    catalog_url = "https://www.oreilly.co.jp/catalog/"

    def fetch_books(self) -> list[PublisherCatalogBookAppModel]:
        html = fetch_text(self.catalog_url)
        return parse_oreilly_catalog(html, self.catalog_url)


def fetch_json(url: str, params: dict[str, str]) -> dict | list:
    filtered = {key: value for key, value in params.items() if value}
    request = Request(f"{url}?{urlencode(filtered)}", headers={"User-Agent": "bookshelf-app"})
    try:
        with urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        if error.code == 429:
            raise BookSearchRateLimitError() from error
        raise


def fetch_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": "bookshelf-app"})
    with urlopen(request, timeout=10) as response:
        return response.read().decode("utf-8")


def convert_openbd_item(item: dict | None, fallback_isbn13: str) -> BookSearchResultAppModel | None:
    if not item or not item.get("summary"):
        return None

    summary = item["summary"]
    isbn = normalize_isbn(summary.get("isbn") or fallback_isbn13)
    return BookSearchResultAppModel(
        source="openbd",
        source_id=isbn,
        title=summary.get("title") or "タイトル不明",
        authors=split_authors(summary.get("author") or ""),
        publisher=summary.get("publisher") or "不明",
        isbn13=isbn,
        published_at=parse_published_date(summary.get("pubdate")),
        image_url=normalize_cover_url(summary.get("cover")),
        description=extract_openbd_description(item),
    )


def create_google_search_queries(keyword: str) -> list[str]:
    normalized = keyword.strip()
    if is_isbn13(normalized):
        return [f"isbn:{normalize_isbn(normalized)}"]

    return unique_search_queries(
        [
            normalized,
            create_google_field_search_query("intitle", normalized),
            create_google_field_search_query("inpublisher", normalized),
        ]
    )


def create_google_field_search_query(field: str, keyword: str) -> str:
    if re.search(r"\s", keyword):
        return f'{field}:"{keyword}"'
    return f"{field}:{keyword}"


def unique_search_queries(queries: list[str]) -> list[str]:
    results: list[str] = []
    for query in queries:
        if query and query not in results:
            results.append(query)
    return results


def parse_oreilly_catalog(html: str, base_url: str) -> list[PublisherCatalogBookAppModel]:
    parser = _HtmlTableExtractor()
    parser.feed(html)
    parser.close()

    books: list[PublisherCatalogBookAppModel] = []
    for row in parser.rows:
        if len(row.cells) < 4 or not is_isbn13(row.cells[0]):
            continue
        books.append(
            PublisherCatalogBookAppModel(
                isbn13=normalize_isbn(row.cells[0]),
                title=row.cells[1].strip(),
                price=row.cells[2].strip() or None,
                published_at=parse_published_date(row.cells[3]),
                source_url=urljoin(base_url, row.href) if row.href else base_url,
            )
        )

    return unique_catalog_books(books)


@dataclass
class _HtmlTableRow:
    cells: list[str]
    href: str | None


class _HtmlTableExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows: list[_HtmlTableRow] = []
        self._in_row = False
        self._in_cell = False
        self._current_cells: list[str] = []
        self._current_cell_parts: list[str] = []
        self._current_href: str | None = None

    def handle_starttag(self, tag: str, attrs):
        tag = tag.lower()
        if tag == "tr":
            self._in_row = True
            self._current_cells = []
            self._current_href = None
        elif self._in_row and tag in {"td", "th"}:
            self._in_cell = True
            self._current_cell_parts = []
        elif self._in_cell and tag == "a" and self._current_href is None:
            attr_dict = dict(attrs)
            self._current_href = attr_dict.get("href")

    def handle_endtag(self, tag: str):
        tag = tag.lower()
        if self._in_cell and tag in {"td", "th"}:
            self._current_cells.append(normalize_space("".join(self._current_cell_parts)))
            self._current_cell_parts = []
            self._in_cell = False
        elif self._in_row and tag == "tr":
            self.rows.append(_HtmlTableRow(self._current_cells, self._current_href))
            self._current_cells = []
            self._current_href = None
            self._in_row = False

    def handle_data(self, data: str):
        if self._in_cell:
            self._current_cell_parts.append(data)


def filter_catalog_books(
    books: list[PublisherCatalogBookAppModel], keyword: str | None
) -> list[PublisherCatalogBookAppModel]:
    normalized = normalize_space(keyword or "").lower()
    if not normalized:
        return books
    return [
        book
        for book in books
        if normalized in book.title.lower() or normalized in normalize_isbn(book.isbn13).lower()
    ]


def convert_catalog_book(book: PublisherCatalogBookAppModel, publisher_name: str) -> BookSearchResultAppModel:
    return BookSearchResultAppModel(
        source="publisher-catalog",
        source_id=book.source_url or book.isbn13,
        title=book.title or "タイトル不明",
        authors=["著者不明"],
        publisher=publisher_name,
        isbn13=book.isbn13,
        published_at=book.published_at,
        image_url=None,
        description=None,
    )


def unique_catalog_books(books: list[PublisherCatalogBookAppModel]) -> list[PublisherCatalogBookAppModel]:
    by_isbn: dict[str, PublisherCatalogBookAppModel] = {}
    for book in books:
        by_isbn.setdefault(book.isbn13, book)
    return list(by_isbn.values())


def catalog_books_to_json(books: list[PublisherCatalogBookAppModel]) -> str:
    return json.dumps(
        {
            "books": [
                {
                    "isbn13": book.isbn13,
                    "title": book.title,
                    "published_at": book.published_at.isoformat(),
                    "price": book.price,
                    "source_url": book.source_url,
                }
                for book in books
            ]
        },
        ensure_ascii=False,
    )


def catalog_books_from_json(payload_json: str) -> list[PublisherCatalogBookAppModel]:
    payload = json.loads(payload_json)
    return [
        PublisherCatalogBookAppModel(
            isbn13=normalize_isbn(item["isbn13"]),
            title=item["title"],
            published_at=parse_published_date(item["published_at"]),
            price=item.get("price"),
            source_url=item.get("source_url"),
        )
        for item in payload.get("books", [])
        if isinstance(item, dict) and item.get("isbn13") and item.get("title")
    ]


def book_search_result_to_json(book: BookSearchResultAppModel) -> str:
    return json.dumps(
        {
            "source": book.source,
            "source_id": book.source_id,
            "title": book.title,
            "authors": book.authors,
            "publisher": book.publisher,
            "isbn13": book.isbn13,
            "published_at": book.published_at.isoformat(),
            "image_url": book.image_url,
            "description": book.description,
        },
        ensure_ascii=False,
    )


def book_search_result_from_json(payload_json: str) -> BookSearchResultAppModel | None:
    try:
        payload = json.loads(payload_json)
        return BookSearchResultAppModel(
            source=payload["source"],
            source_id=payload["source_id"],
            title=payload["title"],
            authors=payload["authors"],
            publisher=payload["publisher"],
            isbn13=normalize_isbn(payload["isbn13"]),
            published_at=parse_published_date(payload["published_at"]),
            image_url=payload.get("image_url"),
            description=payload.get("description"),
        )
    except (KeyError, TypeError, json.JSONDecodeError):
        return None


def clear_publisher_catalog_cache() -> int:
    for session in get_session_for_cache():
        result = session.execute(delete(PublisherCatalogCacheDTO))
        session.commit()
        return result.rowcount or 0
    raise RuntimeError("failed to open database session")


def clear_book_metadata_cache() -> int:
    for session in get_session_for_cache():
        result = session.execute(delete(BookMetadataCacheDTO))
        session.commit()
        return result.rowcount or 0
    raise RuntimeError("failed to open database session")


def get_session_for_cache():
    with SessionLocal() as session:
        yield session


def is_cache_expired(expires_at: datetime) -> bool:
    now = datetime.now(timezone.utc)
    if expires_at.tzinfo is None:
        return expires_at < now.replace(tzinfo=None)
    return expires_at < now


def convert_google_volume(item: dict) -> BookSearchResultAppModel | None:
    volume_info = item.get("volumeInfo") or {}
    isbn13 = find_google_isbn13(volume_info.get("industryIdentifiers") or [])
    if not isbn13:
        return None

    image_links = volume_info.get("imageLinks") or {}
    image_url = image_links.get("thumbnail") or image_links.get("smallThumbnail")
    return BookSearchResultAppModel(
        source="google-books",
        source_id=item.get("id") or isbn13,
        title=volume_info.get("title") or "タイトル不明",
        authors=volume_info.get("authors") or ["著者不明"],
        publisher=volume_info.get("publisher") or "不明",
        isbn13=isbn13,
        published_at=parse_published_date(volume_info.get("publishedDate")),
        image_url=normalize_cover_url(image_url),
        description=normalize_description(volume_info.get("description")),
    )


def find_google_isbn13(identifiers: list[dict]) -> str | None:
    for identifier in identifiers:
        if identifier.get("type") == "ISBN_13" and identifier.get("identifier"):
            return normalize_isbn(identifier["identifier"])

    for identifier in identifiers:
        if identifier.get("type") == "ISBN_10" and identifier.get("identifier"):
            return convert_isbn10_to_isbn13(identifier["identifier"])

    return None


def merge_book_search_result(
    google_book: BookSearchResultAppModel, openbd_book: BookSearchResultAppModel
) -> BookSearchResultAppModel:
    return BookSearchResultAppModel(
        source="openbd",
        source_id=openbd_book.source_id,
        title=prefer_text(openbd_book.title, google_book.title, ["タイトル不明"]),
        authors=prefer_authors(openbd_book.authors, google_book.authors),
        publisher=prefer_text(openbd_book.publisher, google_book.publisher, ["不明"]),
        isbn13=openbd_book.isbn13,
        published_at=prefer_date(openbd_book.published_at, google_book.published_at),
        image_url=openbd_book.image_url or google_book.image_url,
        description=google_book.description or openbd_book.description,
    )


def extract_openbd_description(item: dict) -> str | None:
    text_contents = (((item.get("onix") or {}).get("CollateralDetail") or {}).get("TextContent") or [])
    if not isinstance(text_contents, list):
        return None

    preferred_codes = ["03", "02"]
    for code in preferred_codes:
        for content in text_contents:
            if not isinstance(content, dict) or content.get("TextTypeCode") != code:
                continue
            text = (content.get("Text") or "").strip()
            if text:
                return normalize_description(text)

    for content in text_contents:
        if not isinstance(content, dict):
            continue
        text = (content.get("Text") or "").strip()
        if text:
            return normalize_description(text)

    return None


def normalize_description(value: str | None) -> str | None:
    if not value:
        return None

    text = strip_html(value)
    text = unescape(text)
    text = re.sub(r"\r\n|\r", "\n", text)
    text = re.sub(r"[ \t\f\v]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = "\n".join(line.strip() for line in text.split("\n"))
    text = text.strip()
    return text or None


class _HtmlTextExtractor(HTMLParser):
    _break_tags = {"br", "p", "div", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6"}

    def __init__(self):
        super().__init__()
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, _attrs):
        if tag.lower() in self._break_tags:
            self.parts.append("\n")

    def handle_endtag(self, tag: str):
        if tag.lower() in self._break_tags:
            self.parts.append("\n")

    def handle_data(self, data: str):
        self.parts.append(data)

    def text(self) -> str:
        return "".join(self.parts)


def strip_html(value: str) -> str:
    parser = _HtmlTextExtractor()
    parser.feed(value)
    parser.close()
    return parser.text()


def normalize_isbn(isbn: str) -> str:
    return re.sub(r"[-\s]", "", isbn).upper()


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def is_isbn13(value: str) -> bool:
    return re.fullmatch(r"\d{13}", normalize_isbn(value)) is not None


def convert_isbn10_to_isbn13(isbn10: str) -> str | None:
    normalized = normalize_isbn(isbn10)
    if re.fullmatch(r"\d{9}[\dX]", normalized) is None:
        return None

    isbn_base = "978" + normalized[:9]
    total = sum(int(num) * (1 if index % 2 == 0 else 3) for index, num in enumerate(isbn_base))
    check_digit = (10 - (total % 10)) % 10
    return isbn_base + str(check_digit)


def parse_published_date(value: str | None) -> date:
    if not value:
        return date(1970, 1, 1)

    value = value.strip()
    if re.fullmatch(r"\d{4}", value):
        return date(int(value), 1, 1)
    if re.fullmatch(r"\d{4}-\d{2}", value):
        year, month = value.split("-")
        return date(int(year), int(month), 1)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        year, month, day = value.split("-")
        return date(int(year), int(month), int(day))
    if re.fullmatch(r"\d{4}/\d{2}/\d{2}", value):
        year, month, day = value.split("/")
        return date(int(year), int(month), int(day))
    if re.fullmatch(r"\d{6}", value):
        return date(int(value[:4]), int(value[4:6]), 1)
    if re.fullmatch(r"\d{8}", value):
        return date(int(value[:4]), int(value[4:6]), int(value[6:8]))

    return date(1970, 1, 1)


def split_authors(author: str) -> list[str]:
    authors = [item.strip() for item in re.split(r"[、,／/]", author) if item.strip()]
    return authors if authors else ["著者不明"]


def normalize_cover_url(cover: str | None) -> str | None:
    if not cover:
        return None
    return cover.replace("http://", "https://", 1)


def unique_books(books: list[BookSearchResultAppModel]) -> list[BookSearchResultAppModel]:
    by_isbn: dict[str, BookSearchResultAppModel] = {}
    for book in books:
        current = by_isbn.get(book.isbn13)
        if current is None or score_book(book) > score_book(current):
            by_isbn[book.isbn13] = book

    same_publish_books = unique_by_key(list(by_isbn.values()), create_same_publish_duplicate_key)
    return unique_by_key(same_publish_books, create_near_duplicate_key)


def unique_by_key(
    books: list[BookSearchResultAppModel],
    key_factory,
) -> list[BookSearchResultAppModel]:
    results: list[BookSearchResultAppModel] = []
    result_indexes: dict[str, int] = {}
    for book in books:
        key = key_factory(book)
        if not key:
            results.append(book)
            continue

        current_index = result_indexes.get(key)
        if current_index is None:
            result_indexes[key] = len(results)
            results.append(book)
            continue

        if score_book(book) > score_book(results[current_index]):
            results[current_index] = book

    return results


def create_same_publish_duplicate_key(book: BookSearchResultAppModel) -> str | None:
    title = book.title.strip()
    publisher = book.publisher.strip()
    if not title or not publisher or publisher == "不明" or book.published_at.year == 1970:
        return None
    return f"{title}:{publisher}:{book.published_at.year}"


def create_near_duplicate_key(book: BookSearchResultAppModel) -> str | None:
    title = normalize_book_title(book.title)
    author = normalize_author(book.authors[0]) if book.authors else ""
    if not title or not author or author == "著者不明":
        return None
    return f"{title}:{author}"


def normalize_book_title(title: str) -> str:
    normalized = title.lower()
    normalized = re.sub(r"[「」『』【】\[\]\(\)（）\s!！?？:：・,，.．――\-]", "", normalized)
    return normalized


def normalize_author(author: str) -> str:
    normalized = author.lower()
    normalized = re.sub(r"\s", "", normalized)
    normalized = re.sub(r"wingsプロジェクト", "", normalized)
    return normalized


def score_book(book: BookSearchResultAppModel) -> int:
    score = 0
    if book.publisher and book.publisher != "不明":
        score += 20
    if book.image_url:
        score += 10
    if book.description:
        score += 5 + min(len(book.description), 1000) // 100
    if book.authors and book.authors != ["著者不明"]:
        score += 10
    if book.published_at.year != 1970:
        score += 5
    return score


def prefer_text(primary: str, fallback: str, invalid_values: list[str]) -> str:
    stripped = primary.strip()
    if not stripped or stripped in invalid_values:
        return fallback
    return stripped


def prefer_authors(primary: list[str], fallback: list[str]) -> list[str]:
    valid = [author for author in primary if author and author != "著者不明"]
    return valid if valid else fallback


def prefer_date(primary: date, fallback: date) -> date:
    if primary.year == 1970:
        return fallback
    return primary
