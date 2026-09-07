import json
from pathlib import Path

from scripts import load_books


def details_book(index: int) -> dict:
    return {
        "upc": f"upc-{index}",
        "title": f"Book {index}",
        "product_url": f"https://books.toscrape.com/catalogue/book-{index}/index.html",
        "category": "Default",
        "rating": 3,
        "price_list": "10.00",
        "price_excl_tax": "10.00",
        "price_incl_tax": "10.00",
        "tax": "0.00",
        "stock_quantity": index,
        "availability_text": f"In stock ({index} available)",
        "review_count": 0,
        "description": None,
        "image_url": None,
    }


class FakeConnection:
    def __init__(self) -> None:
        self.commits = 0
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.closed = True

    def commit(self) -> None:
        self.commits += 1


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def test_validate_input_accepts_sample_when_allowed(tmp_path: Path) -> None:
    path = tmp_path / "books_details_sample.json"
    write_json(path, [details_book(1)])

    assert load_books.validate_input(path, allow_sample=True) == []


def test_validate_input_rejects_sample_when_not_allowed(tmp_path: Path) -> None:
    path = tmp_path / "books_details_sample.json"
    write_json(path, [details_book(1)])

    errors = load_books.validate_input(path, allow_sample=False)

    assert any("1000 fiches attendues" in error for error in errors)


def test_load_books_upserts_and_commits_each_book(monkeypatch) -> None:
    connection = FakeConnection()
    upserted = []

    def fake_connect_postgres():
        return connection

    def fake_upsert_book(received_connection, book):
        upserted.append((received_connection, book))

    monkeypatch.setattr(load_books, "connect_postgres", fake_connect_postgres)
    monkeypatch.setattr(load_books, "upsert_book", fake_upsert_book)
    books = [details_book(1), details_book(2)]

    assert load_books.load_books(books) == 2

    assert upserted == [(connection, books[0]), (connection, books[1])]
    assert connection.commits == 2
    assert connection.closed


def test_main_loads_valid_sample(monkeypatch, tmp_path: Path, capsys) -> None:
    path = tmp_path / "books_details_sample.json"
    write_json(path, [details_book(1)])
    loaded_books = []

    def fake_load_books(books):
        loaded_books.extend(books)
        return len(books)

    monkeypatch.setattr(load_books, "load_books", fake_load_books)

    status_code = load_books.main(["--input", str(path), "--allow-sample"])

    output = capsys.readouterr().out
    assert status_code == 0
    assert len(loaded_books) == 1
    assert "1 livre(s) charge(s)" in output


def test_main_returns_error_for_invalid_input(tmp_path: Path, capsys) -> None:
    path = tmp_path / "invalid.json"
    write_json(path, [{"upc": ""}])

    status_code = load_books.main(["--input", str(path), "--allow-sample"])

    output = capsys.readouterr().out
    assert status_code == 1
    assert "ERREUR:" in output
