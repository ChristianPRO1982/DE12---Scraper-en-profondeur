import argparse
import json
from collections.abc import Iterable
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urlparse

LIST_EXPORT_PATH = Path("exports/books_list.json")
DETAILS_SAMPLE_EXPORT_PATH = Path("exports/books_details_sample.json")
DETAILS_EXPORT_PATH = Path("exports/books_details.json")
EXPECTED_FULL_COUNT = 1000
MAX_PRINTED_ERRORS = 20

LIST_FIELDS = ("title", "price_list", "rating", "product_url")
DETAIL_FIELDS = (
    "upc",
    "title",
    "product_url",
    "category",
    "rating",
    "price_list",
    "price_excl_tax",
    "price_incl_tax",
    "tax",
    "stock_quantity",
    "availability_text",
    "review_count",
    "description",
    "image_url",
)
PRICE_FIELDS = ("price_list", "price_excl_tax", "price_incl_tax", "tax")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Valide les exports JSON produits par les spiders Scrapy."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--sample", action="store_true", help="Valide l'export echantillon.")
    mode.add_argument("--full", action="store_true", help="Valide l'export final complet.")
    args = parser.parse_args(argv)

    errors = validate_sample() if args.sample else validate_full()
    return 1 if errors else 0


def validate_sample(
    list_path: Path = LIST_EXPORT_PATH,
    details_path: Path = DETAILS_SAMPLE_EXPORT_PATH,
) -> list[str]:
    errors: list[str] = []
    list_books = validate_list_export(list_path, errors)
    details_books = validate_details_export(details_path, errors, expected_count=None)

    compare_titles(list_books, details_books, errors)
    print_summary(list_books, details_books, errors, compare_url_sets=False)
    return errors


def validate_full(
    list_path: Path = LIST_EXPORT_PATH,
    details_path: Path = DETAILS_EXPORT_PATH,
) -> list[str]:
    errors: list[str] = []
    list_books = validate_list_export(list_path, errors)
    details_books = validate_details_export(
        details_path, errors, expected_count=EXPECTED_FULL_COUNT
    )

    compare_url_sets(list_books, details_books, errors)
    compare_titles(list_books, details_books, errors)
    print_summary(list_books, details_books, errors, compare_url_sets=True)
    return errors


def validate_list_export(path: Path, errors: list[str]) -> list[dict]:
    books = load_json_list(path, errors)
    if len(books) != EXPECTED_FULL_COUNT:
        errors.append(f"{path}: {EXPECTED_FULL_COUNT} livres attendus, {len(books)} trouves")

    seen_urls: set[str] = set()
    duplicate_urls = 0
    for index, book in enumerate(books, start=1):
        validate_field_names(path, index, book, LIST_FIELDS, errors)
        validate_required_text(path, index, book, "title", errors)
        validate_rating(path, index, book, errors)
        validate_decimal(path, index, book, "price_list", errors)
        url = validate_absolute_url(path, index, book, "product_url", errors, nullable=False)
        if url and url in seen_urls:
            duplicate_urls += 1
            errors.append(f"{path}: URL produit dupliquee a la ligne {index}: {url}")
        seen_urls.add(url)

    if duplicate_urls:
        errors.append(f"{path}: {duplicate_urls} URL produit dupliquee(s)")
    return books


def validate_details_export(
    path: Path, errors: list[str], expected_count: int | None
) -> list[dict]:
    books = load_json_list(path, errors)
    if expected_count is not None and len(books) != expected_count:
        errors.append(f"{path}: {expected_count} fiches attendues, {len(books)} trouvees")
    if expected_count is None and not books:
        errors.append(f"{path}: l'echantillon ne contient aucune fiche")

    seen_upcs: set[str] = set()
    seen_urls: set[str] = set()
    duplicate_upcs = 0
    duplicate_urls = 0
    for index, book in enumerate(books, start=1):
        validate_field_names(path, index, book, DETAIL_FIELDS, errors)
        upc = validate_required_text(path, index, book, "upc", errors)
        validate_required_text(path, index, book, "title", errors)
        url = validate_absolute_url(path, index, book, "product_url", errors, nullable=False)
        category = validate_required_text(path, index, book, "category", errors)
        validate_category(path, index, category, errors)
        validate_rating(path, index, book, errors)
        validate_stock(path, index, book, errors)
        validate_non_negative_int(path, index, book, "review_count", errors)
        validate_description(path, index, book, errors)
        validate_absolute_url(path, index, book, "image_url", errors, nullable=True)
        for field_name in PRICE_FIELDS:
            validate_decimal(path, index, book, field_name, errors)

        if upc and upc in seen_upcs:
            duplicate_upcs += 1
            errors.append(f"{path}: UPC duplique a la ligne {index}: {upc}")
        seen_upcs.add(upc)
        if url and url in seen_urls:
            duplicate_urls += 1
            errors.append(f"{path}: URL produit dupliquee a la ligne {index}: {url}")
        seen_urls.add(url)

    if duplicate_upcs:
        errors.append(f"{path}: {duplicate_upcs} UPC duplique(s)")
    if duplicate_urls:
        errors.append(f"{path}: {duplicate_urls} URL produit dupliquee(s)")
    return books


def load_json_list(path: Path, errors: list[str]) -> list[dict]:
    try:
        raw_data = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"{path}: fichier introuvable")
        return []
    except UnicodeDecodeError as error:
        errors.append(f"{path}: fichier non lisible en UTF-8 ({error})")
        return []

    try:
        data = json.loads(raw_data)
    except json.JSONDecodeError as error:
        errors.append(f"{path}: JSON invalide ({error})")
        return []

    if not isinstance(data, list):
        errors.append(f"{path}: le JSON doit contenir une liste")
        return []
    if not all(isinstance(item, dict) for item in data):
        errors.append(f"{path}: chaque entree doit etre un objet JSON")
        return []

    return data


def validate_field_names(
    path: Path, index: int, book: dict, expected_fields: tuple[str, ...], errors: list[str]
) -> None:
    fields = tuple(book)
    if fields != expected_fields:
        errors.append(
            f"{path}: schema invalide a la ligne {index}: "
            f"{list(fields)} au lieu de {list(expected_fields)}"
        )


def validate_required_text(
    path: Path, index: int, book: dict, field_name: str, errors: list[str]
) -> str:
    value = book.get(field_name)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path}: champ {field_name!r} vide ou invalide a la ligne {index}")
        return ""
    return value


def validate_category(path: Path, index: int, category: str, errors: list[str]) -> None:
    if category in {"Home", "Books"}:
        errors.append(f"{path}: categorie interdite a la ligne {index}: {category}")


def validate_rating(path: Path, index: int, book: dict, errors: list[str]) -> None:
    rating = book.get("rating")
    if not isinstance(rating, int) or isinstance(rating, bool) or not 1 <= rating <= 5:
        errors.append(f"{path}: rating invalide a la ligne {index}: {rating!r}")


def validate_stock(path: Path, index: int, book: dict, errors: list[str]) -> None:
    validate_non_negative_int(path, index, book, "stock_quantity", errors)
    availability_text = book.get("availability_text")
    if not isinstance(availability_text, str) or not availability_text.strip():
        errors.append(f"{path}: availability_text vide ou invalide a la ligne {index}")
        return

    stock_quantity = book.get("stock_quantity")
    expected_text = f"({stock_quantity} available)"
    if isinstance(stock_quantity, int) and not isinstance(stock_quantity, bool):
        if expected_text not in availability_text:
            errors.append(
                f"{path}: stock_quantity ne correspond pas a availability_text a la ligne {index}"
            )


def validate_non_negative_int(
    path: Path, index: int, book: dict, field_name: str, errors: list[str]
) -> None:
    value = book.get(field_name)
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        errors.append(f"{path}: champ {field_name!r} invalide a la ligne {index}: {value!r}")


def validate_description(path: Path, index: int, book: dict, errors: list[str]) -> None:
    value = book.get("description")
    if value is not None and not isinstance(value, str):
        errors.append(f"{path}: description invalide a la ligne {index}: {value!r}")


def validate_absolute_url(
    path: Path, index: int, book: dict, field_name: str, errors: list[str], nullable: bool
) -> str:
    value = book.get(field_name)
    if nullable and value is None:
        return ""
    if not isinstance(value, str) or not value.strip() or not is_absolute_url(value):
        errors.append(f"{path}: URL invalide pour {field_name!r} a la ligne {index}: {value!r}")
        return ""
    return value


def is_absolute_url(value: str) -> bool:
    parsed_url = urlparse(value)
    return parsed_url.scheme in {"http", "https"} and bool(parsed_url.netloc)


def validate_decimal(
    path: Path, index: int, book: dict, field_name: str, errors: list[str]
) -> None:
    if parse_decimal(book.get(field_name)) is None:
        errors.append(f"{path}: prix invalide pour {field_name!r} a la ligne {index}")


def parse_decimal(value: object) -> Decimal | None:
    if isinstance(value, bool | float) or value is None:
        return None
    try:
        return Decimal(str(value))
    except InvalidOperation:
        return None


def compare_url_sets(list_books: list[dict], details_books: list[dict], errors: list[str]) -> None:
    list_urls = {book.get("product_url") for book in list_books}
    details_urls = {book.get("product_url") for book in details_books}
    missing_urls = sorted(str(url) for url in list_urls - details_urls)
    extra_urls = sorted(str(url) for url in details_urls - list_urls)

    for url in missing_urls:
        errors.append(f"URL manquante dans l'export detaille: {url}")
    for url in extra_urls:
        errors.append(f"URL supplementaire dans l'export detaille: {url}")


def compare_titles(list_books: list[dict], details_books: list[dict], errors: list[str]) -> None:
    list_titles_by_url = {
        book.get("product_url"): book.get("title")
        for book in list_books
        if isinstance(book.get("product_url"), str)
    }
    for book in details_books:
        product_url = book.get("product_url")
        list_title = list_titles_by_url.get(product_url)
        details_title = book.get("title")
        if list_title is not None and list_title != details_title:
            errors.append(
                f"Titre different pour {product_url}: liste={list_title!r}, fiche={details_title!r}"
            )


def print_summary(
    list_books: list[dict],
    details_books: list[dict],
    errors: list[str],
    compare_url_sets: bool,
) -> None:
    price_stats = compute_price_stats(details_books)
    list_urls = collect_values(list_books, "product_url")
    detail_urls = collect_values(details_books, "product_url")
    detail_upcs = collect_values(details_books, "upc")

    summary = [
        f"livres Phase 1 : {len(list_books)}",
        f"URLs Phase 1 uniques : {len(set(list_urls))}",
        f"fiches detaillees : {len(details_books)}",
        f"UPC uniques : {len(set(detail_upcs))}",
        f"URLs detaillees uniques : {len(set(detail_urls))}",
        f"ratings invalides : {count_invalid_ratings(details_books)}",
        f"stocks invalides : {count_invalid_non_negative_int(details_books, 'stock_quantity')}",
        f"reviews invalides : {count_invalid_non_negative_int(details_books, 'review_count')}",
        f"categories absentes : {count_missing_text(details_books, 'category')}",
        f"descriptions absentes : {sum(book.get('description') is None for book in details_books)}",
        f"prix liste = HT : {price_stats['list_equals_excl_tax']}",
        f"prix HT = TTC : {price_stats['excl_tax_equals_incl_tax']}",
        f"taxe = 0 : {price_stats['tax_zero']}",
        f"differences prix observees : {price_stats['price_differences']}",
        f"erreurs : {len(errors)}",
    ]

    if compare_url_sets:
        summary.insert(5, f"URLs manquantes : {len(set(list_urls) - set(detail_urls))}")
        summary.insert(6, f"URLs supplementaires : {len(set(detail_urls) - set(list_urls))}")

    print("\n".join(summary))
    for error in errors[:MAX_PRINTED_ERRORS]:
        print(f"ERREUR: {error}")
    hidden_errors_count = len(errors) - MAX_PRINTED_ERRORS
    if hidden_errors_count > 0:
        print(f"ERREUR: {hidden_errors_count} erreur(s) supplementaire(s) non affichee(s)")


def compute_price_stats(details_books: list[dict]) -> dict[str, int]:
    stats = {
        "list_equals_excl_tax": 0,
        "excl_tax_equals_incl_tax": 0,
        "tax_zero": 0,
        "price_differences": 0,
    }
    for book in details_books:
        price_list = parse_decimal(book.get("price_list"))
        price_excl_tax = parse_decimal(book.get("price_excl_tax"))
        price_incl_tax = parse_decimal(book.get("price_incl_tax"))
        tax = parse_decimal(book.get("tax"))
        if None in {price_list, price_excl_tax, price_incl_tax, tax}:
            continue
        stats["list_equals_excl_tax"] += price_list == price_excl_tax
        stats["excl_tax_equals_incl_tax"] += price_excl_tax == price_incl_tax
        stats["tax_zero"] += tax == Decimal("0")
        stats["price_differences"] += (
            price_list != price_excl_tax or price_excl_tax != price_incl_tax or tax != Decimal("0")
        )
    return stats


def collect_values(books: Iterable[dict], field_name: str) -> list[object]:
    return [book.get(field_name) for book in books if book.get(field_name)]


def count_invalid_ratings(books: list[dict]) -> int:
    return sum(
        not isinstance(book.get("rating"), int)
        or isinstance(book.get("rating"), bool)
        or not 1 <= book["rating"] <= 5
        for book in books
    )


def count_invalid_non_negative_int(books: list[dict], field_name: str) -> int:
    return sum(
        not isinstance(book.get(field_name), int)
        or isinstance(book.get(field_name), bool)
        or book[field_name] < 0
        for book in books
    )


def count_missing_text(books: list[dict], field_name: str) -> int:
    return sum(
        not isinstance(book.get(field_name), str) or not book[field_name].strip() for book in books
    )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
