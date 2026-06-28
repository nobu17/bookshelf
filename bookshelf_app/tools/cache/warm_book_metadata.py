import argparse

from bookshelf_app.api.book_search.service import BookSearchService


def main() -> None:
    parser = argparse.ArgumentParser(description="Warm publisher book metadata cache.")
    parser.add_argument("--publisher-id", default="oreilly_japan")
    parser.add_argument("--refresh-after-days", type=int, default=14)
    parser.add_argument("--batch-size", type=int, default=40)
    parser.add_argument("--google-delay-seconds", type=float, default=0.2)
    parser.add_argument("--batch-delay-seconds", type=float, default=2.0)
    args = parser.parse_args()

    if args.refresh_after_days < 1:
        parser.error("--refresh-after-days must be at least 1.")
    if args.batch_size < 1 or args.batch_size > 40:
        parser.error("--batch-size must be between 1 and 40.")
    if args.google_delay_seconds < 0 or args.batch_delay_seconds < 0:
        parser.error("Delay values must not be negative.")

    result = BookSearchService().warm_publisher_metadata_cache(
        publisher_id=args.publisher_id,
        refresh_after_days=args.refresh_after_days,
        batch_size=args.batch_size,
        google_delay_seconds=args.google_delay_seconds,
        batch_delay_seconds=args.batch_delay_seconds,
    )
    print(
        "book metadata cache warmup finished: "
        f"catalog={result.catalog_count}, "
        f"candidates={result.candidate_count}, "
        f"refreshed={result.refreshed_count}, "
        f"failed={result.failed_count}"
    )

    if result.failed_count:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
