import json
from pathlib import Path

from books_catalog_scraper import validate_exports


def list_book(index: int, title: str | None = None, product_url: str | None = None) -> dict:
    return {
        "title": title or f"Book {index}",
        "price_list": f"{index}.10",
        "rating": index % 5 + 1,
        "product_url": product_url
        or f"https://books.toscrape.com/catalogue/book-{index}/index.html",
    }


def details_book(
    index: int,
    title: str | None = None,
    product_url: str | None = None,
    description: str | None = "Description source",
    image_url: str | None = None,
) -> dict:
    return {
        "upc": f"upc-{index}",
        "title": title or f"Book {index}",
        "product_url": product_url
        or f"https://books.toscrape.com/catalogue/book-{index}/index.html",
        "category": "Default",
        "rating": index % 5 + 1,
        "price_list": f"{index}.10",
        "price_excl_tax": f"{index}.10",
        "price_incl_tax": f"{index}.10",
        "tax": "0.00",
        "stock_quantity": index,
        "availability_text": f"In stock ({index} available)",
        "review_count": 0,
        "description": description,
        "image_url": image_url,
    }


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def test_validate_sample_accepts_valid_exports(tmp_path: Path, capsys) -> None:
    list_path = tmp_path / "books_list.json"
    details_path = tmp_path / "books_details_sample.json"
    list_books = [list_book(index) for index in range(1, 1001)]
    list_books[1]["title"] = "Special # & é"
    write_json(list_path, list_books)
    write_json(
        details_path,
        [
            details_book(1, description=None),
            details_book(
                2,
                title="Special # & é",
                image_url="https://books.toscrape.com/media/book-2.jpg",
            ),
        ],
    )

    errors = validate_exports.validate_sample(list_path, details_path)

    output = capsys.readouterr().out
    assert errors == []
    assert "livres Phase 1 : 1000" in output
    assert "fiches detaillees : 2" in output
    assert "descriptions absentes : 1" in output
    assert "erreurs : 0" in output


def test_validate_full_accepts_matching_exports(tmp_path: Path, capsys) -> None:
    list_path = tmp_path / "books_list.json"
    details_path = tmp_path / "books_details.json"
    write_json(list_path, [list_book(index) for index in range(1, 1001)])
    write_json(details_path, [details_book(index) for index in range(1, 1001)])

    errors = validate_exports.validate_full(list_path, details_path)

    output = capsys.readouterr().out
    assert errors == []
    assert "fiches detaillees : 1000" in output
    assert "URLs manquantes : 0" in output
    assert "URLs supplementaires : 0" in output
    assert "prix liste = HT : 1000" in output


def test_validate_full_reports_url_and_title_differences(tmp_path: Path, capsys) -> None:
    list_path = tmp_path / "books_list.json"
    details_path = tmp_path / "books_details.json"
    list_books = [list_book(index) for index in range(1, 1001)]
    details_books = [details_book(index) for index in range(1, 1001)]
    details_books[0]["title"] = "Different title"
    details_books[1]["product_url"] = "https://books.toscrape.com/catalogue/extra/index.html"
    write_json(list_path, list_books)
    write_json(details_path, details_books)

    errors = validate_exports.validate_full(list_path, details_path)

    output = capsys.readouterr().out
    assert any("URL manquante" in error for error in errors)
    assert any("URL supplementaire" in error for error in errors)
    assert any("Titre different" in error for error in errors)
    assert "URLs manquantes : 1" in output
    assert "URLs supplementaires : 1" in output


def test_validate_list_export_reports_invalid_values(tmp_path: Path) -> None:
    path = tmp_path / "books_list.json"
    write_json(
        path,
        [
            {
                "title": "",
                "price_list": "not a price",
                "rating": 6,
                "product_url": "not absolute",
                "unexpected": "field",
            },
            {
                "title": "Duplicate",
                "price_list": "10.00",
                "rating": 3,
                "product_url": "https://books.toscrape.com/catalogue/book/index.html",
            },
            {
                "title": "Duplicate again",
                "price_list": "12.00",
                "rating": 4,
                "product_url": "https://books.toscrape.com/catalogue/book/index.html",
            },
        ],
    )
    errors: list[str] = []

    books = validate_exports.validate_list_export(path, errors)

    assert len(books) == 3
    assert any("1000 livres attendus" in error for error in errors)
    assert any("champ 'title' vide" in error for error in errors)
    assert any("rating invalide" in error for error in errors)
    assert any("prix invalide" in error for error in errors)
    assert any("URL invalide" in error for error in errors)
    assert any("URL produit dupliquee" in error for error in errors)


def test_validate_details_export_reports_invalid_values(tmp_path: Path) -> None:
    path = tmp_path / "books_details.json"
    invalid_book = details_book(1)
    invalid_book["upc"] = ""
    invalid_book["product_url"] = "relative/book.html"
    invalid_book["category"] = "Home"
    invalid_book["rating"] = True
    invalid_book["price_list"] = 10.5
    invalid_book["price_excl_tax"] = "not a price"
    invalid_book["price_incl_tax"] = None
    invalid_book["tax"] = False
    invalid_book["stock_quantity"] = -1
    invalid_book["availability_text"] = ""
    invalid_book["review_count"] = -2
    invalid_book["description"] = 42
    invalid_book["image_url"] = "not absolute"
    invalid_stock_book = details_book(4)
    invalid_stock_book["stock_quantity"] = False
    invalid_stock_book["availability_text"] = "In stock (0 available)"
    mismatched_stock_book = details_book(5)
    mismatched_stock_book["stock_quantity"] = 5
    mismatched_stock_book["availability_text"] = "In stock (6 available)"
    duplicate_book = details_book(2)
    duplicate_book["upc"] = "same"
    duplicate_book["product_url"] = "https://books.toscrape.com/catalogue/same/index.html"
    duplicate_again = details_book(3)
    duplicate_again["upc"] = "same"
    duplicate_again["product_url"] = "https://books.toscrape.com/catalogue/same/index.html"
    write_json(
        path,
        [
            invalid_book,
            duplicate_book,
            duplicate_again,
            invalid_stock_book,
            mismatched_stock_book,
        ],
    )
    errors: list[str] = []

    books = validate_exports.validate_details_export(path, errors, expected_count=1000)

    assert len(books) == 5
    assert any("1000 fiches attendues" in error for error in errors)
    assert any("champ 'upc' vide" in error for error in errors)
    assert any("categorie interdite" in error for error in errors)
    assert any("rating invalide" in error for error in errors)
    assert any("stock_quantity" in error for error in errors)
    assert any("availability_text vide" in error for error in errors)
    assert any("review_count" in error for error in errors)
    assert any("stock_quantity ne correspond pas" in error for error in errors)
    assert any("description invalide" in error for error in errors)
    assert sum("prix invalide" in error for error in errors) == 4
    assert any("UPC duplique" in error for error in errors)
    assert any("URL produit dupliquee" in error for error in errors)


def test_validate_details_export_rejects_empty_sample(tmp_path: Path) -> None:
    path = tmp_path / "books_details_sample.json"
    write_json(path, [])
    errors: list[str] = []

    assert validate_exports.validate_details_export(path, errors, expected_count=None) == []
    assert any("echantillon ne contient aucune fiche" in error for error in errors)


def test_load_json_list_reports_reading_errors(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.json"
    invalid_utf8_path = tmp_path / "invalid_utf8.json"
    invalid_json_path = tmp_path / "invalid_json.json"
    not_list_path = tmp_path / "not_list.json"
    not_objects_path = tmp_path / "not_objects.json"
    invalid_utf8_path.write_bytes(b"\xff")
    invalid_json_path.write_text("{", encoding="utf-8")
    write_json(not_list_path, {"book": "value"})
    write_json(not_objects_path, ["not an object"])
    errors: list[str] = []

    assert validate_exports.load_json_list(missing_path, errors) == []
    assert validate_exports.load_json_list(invalid_utf8_path, errors) == []
    assert validate_exports.load_json_list(invalid_json_path, errors) == []
    assert validate_exports.load_json_list(not_list_path, errors) == []
    assert validate_exports.load_json_list(not_objects_path, errors) == []
    assert any("fichier introuvable" in error for error in errors)
    assert any("non lisible en UTF-8" in error for error in errors)
    assert any("JSON invalide" in error for error in errors)
    assert any("doit contenir une liste" in error for error in errors)
    assert any("chaque entree doit etre un objet" in error for error in errors)


def test_main_returns_error_for_missing_default_full_export(capsys) -> None:
    status_code = validate_exports.main(["--full"])

    output = capsys.readouterr().out
    assert status_code == 1
    assert "exports/books_details.json: fichier introuvable" in output


def test_main_returns_success_for_sample_exports(tmp_path: Path, monkeypatch, capsys) -> None:
    list_path = tmp_path / "books_list.json"
    details_path = tmp_path / "books_details_sample.json"
    write_json(list_path, [list_book(index) for index in range(1, 1001)])
    write_json(details_path, [details_book(1), details_book(2)])
    monkeypatch.setattr(validate_exports, "LIST_EXPORT_PATH", list_path)
    monkeypatch.setattr(validate_exports, "DETAILS_SAMPLE_EXPORT_PATH", details_path)

    status_code = validate_exports.main(["--sample"])

    output = capsys.readouterr().out
    assert status_code == 0
    assert "fiches detaillees : 2" in output


def test_compute_price_stats_ignores_invalid_prices() -> None:
    assert validate_exports.compute_price_stats([{"price_list": "bad"}]) == {
        "list_equals_excl_tax": 0,
        "excl_tax_equals_incl_tax": 0,
        "tax_zero": 0,
        "price_differences": 0,
    }
