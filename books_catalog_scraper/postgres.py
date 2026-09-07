import os
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

import psycopg

ENV_PATH = Path(".env")

CATEGORY_UPSERT_SQL = """
INSERT INTO categories (name, updated_at)
VALUES (%s, NOW())
ON CONFLICT (name) DO UPDATE
SET updated_at = NOW()
RETURNING id;
"""

BOOK_UPSERT_SQL = """
INSERT INTO books (
    upc,
    title,
    product_url,
    category_id,
    image_url,
    rating,
    price_list,
    price_excl_tax,
    price_incl_tax,
    tax,
    stock_quantity,
    availability_text,
    review_count,
    description,
    scraped_at,
    updated_at
)
VALUES (
    %(upc)s,
    %(title)s,
    %(product_url)s,
    %(category_id)s,
    %(image_url)s,
    %(rating)s,
    %(price_list)s,
    %(price_excl_tax)s,
    %(price_incl_tax)s,
    %(tax)s,
    %(stock_quantity)s,
    %(availability_text)s,
    %(review_count)s,
    %(description)s,
    NOW(),
    NOW()
)
ON CONFLICT (upc) DO UPDATE
SET
    title = EXCLUDED.title,
    product_url = EXCLUDED.product_url,
    category_id = EXCLUDED.category_id,
    image_url = EXCLUDED.image_url,
    rating = EXCLUDED.rating,
    price_list = EXCLUDED.price_list,
    price_excl_tax = EXCLUDED.price_excl_tax,
    price_incl_tax = EXCLUDED.price_incl_tax,
    tax = EXCLUDED.tax,
    stock_quantity = EXCLUDED.stock_quantity,
    availability_text = EXCLUDED.availability_text,
    review_count = EXCLUDED.review_count,
    description = EXCLUDED.description,
    scraped_at = NOW(),
    updated_at = NOW();
"""


@dataclass(frozen=True)
class PostgresConfig:
    dbname: str
    user: str
    password: str
    host: str
    port: int


def load_env_file(path: Path = ENV_PATH) -> dict[str, str]:
    if not path.exists():
        return {}

    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        cleaned_line = line.strip()
        if not cleaned_line or cleaned_line.startswith("#") or "=" not in cleaned_line:
            continue

        key, value = cleaned_line.split("=", maxsplit=1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def get_postgres_config(
    env: Mapping[str, str] | None = None, env_path: Path = ENV_PATH
) -> PostgresConfig:
    values = load_env_file(env_path)
    values.update(os.environ if env is None else env)

    return PostgresConfig(
        dbname=require_env(values, "POSTGRES_DB"),
        user=require_env(values, "POSTGRES_USER"),
        password=require_env(values, "POSTGRES_PASSWORD"),
        host=values.get("POSTGRES_HOST", "localhost"),
        port=int(values.get("POSTGRES_PORT", "5432")),
    )


def require_env(values: Mapping[str, str], key: str) -> str:
    value = values.get(key)
    if not value:
        raise ValueError(f"Variable d'environnement manquante: {key}")
    return value


def connect_postgres(config: PostgresConfig | None = None) -> psycopg.Connection:
    postgres_config = config or get_postgres_config()
    return psycopg.connect(
        dbname=postgres_config.dbname,
        user=postgres_config.user,
        password=postgres_config.password,
        host=postgres_config.host,
        port=postgres_config.port,
    )


def upsert_book(connection: psycopg.Connection, item: dict) -> None:
    with connection.cursor() as cursor:
        cursor.execute(CATEGORY_UPSERT_SQL, (item["category"],))
        category_id = cursor.fetchone()[0]
        cursor.execute(BOOK_UPSERT_SQL, build_book_params(item, category_id))


def fetch_existing_product_urls(connection: psycopg.Connection) -> set[str]:
    with connection.cursor() as cursor:
        cursor.execute("SELECT product_url FROM books;")
        return {row[0] for row in cursor.fetchall()}


def build_book_params(item: dict, category_id: int) -> dict:
    return {
        "upc": item["upc"],
        "title": item["title"],
        "product_url": item["product_url"],
        "category_id": category_id,
        "image_url": item["image_url"],
        "rating": item["rating"],
        "price_list": as_decimal(item["price_list"]),
        "price_excl_tax": as_decimal(item["price_excl_tax"]),
        "price_incl_tax": as_decimal(item["price_incl_tax"]),
        "tax": as_decimal(item["tax"]),
        "stock_quantity": item["stock_quantity"],
        "availability_text": item["availability_text"],
        "review_count": item["review_count"],
        "description": item["description"],
    }


def as_decimal(value: Decimal | str) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(value)
