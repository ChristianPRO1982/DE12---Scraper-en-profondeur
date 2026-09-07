import argparse
from pathlib import Path

from books_catalog_scraper.postgres import connect_postgres, upsert_book
from books_catalog_scraper.validate_exports import DETAILS_EXPORT_PATH, load_json_list
from books_catalog_scraper.validate_exports import validate_details_export as validate_export


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Charge un export detaille Books to Scrape dans PostgreSQL."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DETAILS_EXPORT_PATH,
        help="Chemin de l'export JSON detaille a charger.",
    )
    parser.add_argument(
        "--allow-sample",
        action="store_true",
        help="Autorise un export contenant moins de 1 000 fiches.",
    )
    args = parser.parse_args(argv)

    errors = validate_input(args.input, allow_sample=args.allow_sample)
    if errors:
        print_errors(errors)
        return 1

    books = load_json_list(args.input, [])
    saved_count = load_books(books)
    print(f"{saved_count} livre(s) charge(s) dans PostgreSQL depuis {args.input}")
    return 0


def validate_input(path: Path, allow_sample: bool) -> list[str]:
    errors: list[str] = []
    expected_count = None if allow_sample else 1000
    validate_export(path, errors, expected_count=expected_count)
    return errors


def load_books(books: list[dict]) -> int:
    with connect_postgres() as connection:
        for book in books:
            upsert_book(connection, book)
            connection.commit()
    return len(books)


def print_errors(errors: list[str]) -> None:
    for error in errors:
        print(f"ERREUR: {error}")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
