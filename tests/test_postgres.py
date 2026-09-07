from decimal import Decimal
from pathlib import Path

import pytest

from books_catalog_scraper import postgres


def detail_item() -> dict:
    return {
        "upc": "a897fe39b1053632",
        "title": "A Light in the Attic",
        "product_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
        "category": "Poetry",
        "rating": 3,
        "price_list": Decimal("51.77"),
        "price_excl_tax": "51.77",
        "price_incl_tax": "51.77",
        "tax": "0.00",
        "stock_quantity": 22,
        "availability_text": "In stock (22 available)",
        "review_count": 0,
        "description": None,
        "image_url": "https://books.toscrape.com/media/cache/book.jpg",
    }


class FakeCursor:
    def __init__(self) -> None:
        self.executed_queries = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return None

    def execute(self, query: str, params: object) -> None:
        self.executed_queries.append((query, params))

    def fetchone(self) -> tuple[int]:
        return (42,)


class FakeConnection:
    def __init__(self) -> None:
        self.cursor_instance = FakeCursor()

    def cursor(self) -> FakeCursor:
        return self.cursor_instance


def test_load_env_file_reads_simple_env_values(tmp_path: Path) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text(
        """
        # Commentaire
        POSTGRES_DB=books_scraper
        POSTGRES_USER='books_user'
        POSTGRES_PASSWORD="books_password"
        POSTGRES_HOST=localhost
        POSTGRES_PORT=5433
        INVALID_LINE
        """,
        encoding="utf-8",
    )

    assert postgres.load_env_file(env_path) == {
        "POSTGRES_DB": "books_scraper",
        "POSTGRES_USER": "books_user",
        "POSTGRES_PASSWORD": "books_password",
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5433",
    }


def test_load_env_file_returns_empty_dict_when_file_is_missing(tmp_path: Path) -> None:
    assert postgres.load_env_file(tmp_path / "missing.env") == {}


def test_get_postgres_config_uses_env_and_defaults(tmp_path: Path) -> None:
    config = postgres.get_postgres_config(
        env={
            "POSTGRES_DB": "books_scraper",
            "POSTGRES_USER": "books_user",
            "POSTGRES_PASSWORD": "books_password",
        },
        env_path=tmp_path / "missing.env",
    )

    assert config == postgres.PostgresConfig(
        dbname="books_scraper",
        user="books_user",
        password="books_password",
        host="localhost",
        port=5432,
    )


def test_get_postgres_config_prefers_explicit_env_over_env_file(tmp_path: Path) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text(
        """
        POSTGRES_DB=file_db
        POSTGRES_USER=file_user
        POSTGRES_PASSWORD=file_password
        POSTGRES_HOST=file_host
        POSTGRES_PORT=5434
        """,
        encoding="utf-8",
    )

    config = postgres.get_postgres_config(
        env={
            "POSTGRES_DB": "env_db",
            "POSTGRES_USER": "env_user",
            "POSTGRES_PASSWORD": "env_password",
        },
        env_path=env_path,
    )

    assert config == postgres.PostgresConfig(
        dbname="env_db",
        user="env_user",
        password="env_password",
        host="file_host",
        port=5434,
    )


def test_get_postgres_config_rejects_missing_required_value(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="POSTGRES_PASSWORD"):
        postgres.get_postgres_config(
            env={"POSTGRES_DB": "books_scraper", "POSTGRES_USER": "books_user"},
            env_path=tmp_path / "missing.env",
        )


def test_connect_postgres_uses_psycopg_connect(monkeypatch) -> None:
    calls = []

    def fake_connect(**kwargs):
        calls.append(kwargs)
        return "connection"

    monkeypatch.setattr(postgres.psycopg, "connect", fake_connect)

    connection = postgres.connect_postgres(
        postgres.PostgresConfig(
            dbname="books_scraper",
            user="books_user",
            password="books_password",
            host="localhost",
            port=5432,
        )
    )

    assert connection == "connection"
    assert calls == [
        {
            "dbname": "books_scraper",
            "user": "books_user",
            "password": "books_password",
            "host": "localhost",
            "port": 5432,
        }
    ]


def test_build_book_params_converts_prices_to_decimal() -> None:
    params = postgres.build_book_params(detail_item(), category_id=42)

    assert params["category_id"] == 42
    assert params["price_list"] == Decimal("51.77")
    assert params["price_excl_tax"] == Decimal("51.77")
    assert params["tax"] == Decimal("0.00")


def test_upsert_book_inserts_category_then_book() -> None:
    connection = FakeConnection()

    postgres.upsert_book(connection, detail_item())

    category_query, category_params = connection.cursor_instance.executed_queries[0]
    book_query, book_params = connection.cursor_instance.executed_queries[1]
    assert "INSERT INTO categories" in category_query
    assert category_params == ("Poetry",)
    assert "ON CONFLICT (upc) DO UPDATE" in book_query
    assert book_params["category_id"] == 42
    assert book_params["upc"] == "a897fe39b1053632"
