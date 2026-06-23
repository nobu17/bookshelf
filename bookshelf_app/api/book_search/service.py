from dataclasses import dataclass
from datetime import date
from html import unescape
from html.parser import HTMLParser
import json
import re
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from bookshelf_app.config import get_settings


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


class BookSearchService:
    _google: "GoogleBooksProvider"
    _openbd: "OpenBdProvider"

    def __init__(self):
        self._google = GoogleBooksProvider(get_settings().google_books_api_key)
        self._openbd = OpenBdProvider()

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

    if re.fullmatch(r"\d{4}", value):
        return date(int(value), 1, 1)
    if re.fullmatch(r"\d{4}-\d{2}", value):
        year, month = value.split("-")
        return date(int(year), int(month), 1)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        year, month, day = value.split("-")
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
