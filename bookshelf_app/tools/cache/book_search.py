import argparse

from sqlalchemy import delete

from bookshelf_app.api.book_search.service import normalize_isbn
from bookshelf_app.infra.db.book_search import BookMetadataCacheDTO, PublisherCatalogCacheDTO
from bookshelf_app.infra.db.database import get_session


def clear_book_metadata_cache(isbn13: str | None = None) -> int:
    normalized = normalize_isbn(isbn13) if isbn13 else None
    for session in get_session():
        stmt = delete(BookMetadataCacheDTO)
        if normalized:
            stmt = stmt.where(BookMetadataCacheDTO.isbn13 == normalized)
        result = session.execute(stmt)
        session.commit()
        return result.rowcount or 0

    raise RuntimeError("failed to open database session")


def clear_publisher_catalog_cache(source_key: str | None = None) -> int:
    for session in get_session():
        stmt = delete(PublisherCatalogCacheDTO)
        if source_key:
            stmt = stmt.where(PublisherCatalogCacheDTO.source_key == source_key)
        result = session.execute(stmt)
        session.commit()
        return result.rowcount or 0

    raise RuntimeError("failed to open database session")


def main() -> None:
    parser = argparse.ArgumentParser(description="Clear book search cache.")
    parser.add_argument(
        "--metadata",
        action="store_true",
        help="Clear ISBN metadata cache. This is the second cache used for openBD/Google results.",
    )
    parser.add_argument("--isbn13", help="Clear only one ISBN from metadata cache.")
    parser.add_argument("--catalog", action="store_true", help="Clear publisher catalog cache.")
    parser.add_argument("--source-key", help="Clear only one publisher catalog source key.")
    args = parser.parse_args()

    if not args.metadata and not args.catalog:
        parser.error("Specify --metadata or --catalog.")
    if args.isbn13 and not args.metadata:
        parser.error("--isbn13 requires --metadata.")
    if args.source_key and not args.catalog:
        parser.error("--source-key requires --catalog.")

    if args.metadata:
        count = clear_book_metadata_cache(args.isbn13)
        print(f"book metadata cache deleted: {count}")

    if args.catalog:
        count = clear_publisher_catalog_cache(args.source_key)
        print(f"publisher catalog cache deleted: {count}")


if __name__ == "__main__":
    main()
