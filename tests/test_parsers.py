from decimal import Decimal

import pytest

from books_catalog_scraper.parsers import (
    clean_text,
    parse_int,
    parse_price,
    parse_rating,
    parse_stock,
)


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        (None, ""),
        ("", ""),
        ("  A Light   in the Attic\n", "A Light in the Attic"),
    ],
)
def test_clean_text(raw_value: str | None, expected: str) -> None:
    assert clean_text(raw_value) == expected


@pytest.mark.parametrize(
    ("raw_price", "expected"),
    [
        ("£51.77", "51.77"),
        (" £12,30 ", "12.30"),
    ],
)
def test_parse_price(raw_price: str, expected: str) -> None:
    assert parse_price(raw_price) == Decimal(expected)


def test_parse_price_rejects_empty_value() -> None:
    with pytest.raises(ValueError, match="Prix absent"):
        parse_price(None)


def test_parse_price_rejects_invalid_value() -> None:
    with pytest.raises(ValueError, match="Prix invalide"):
        parse_price("not a price")


@pytest.mark.parametrize(
    ("class_value", "expected"),
    [
        ("star-rating One", 1),
        ("star-rating Two", 2),
        ("star-rating Three", 3),
        ("star-rating Four", 4),
        ("star-rating Five", 5),
    ],
)
def test_parse_rating(class_value: str, expected: int) -> None:
    assert parse_rating(class_value) == expected


def test_parse_rating_rejects_unknown_class() -> None:
    with pytest.raises(ValueError, match="Note introuvable"):
        parse_rating("star-rating Unknown")


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        ("0", 0),
        (" 42 ", 42),
    ],
)
def test_parse_int(raw_value: str, expected: int) -> None:
    assert parse_int(raw_value) == expected


def test_parse_int_rejects_empty_value() -> None:
    with pytest.raises(ValueError, match="Entier absent"):
        parse_int("")


@pytest.mark.parametrize(
    ("raw_stock", "expected"),
    [
        ("In stock (22 available)", 22),
        ("\n In stock (1 available) ", 1),
        ("In stock (0 available)", 0),
    ],
)
def test_parse_stock(raw_stock: str, expected: int) -> None:
    assert parse_stock(raw_stock) == expected


def test_parse_stock_rejects_unexpected_text() -> None:
    with pytest.raises(ValueError, match="Stock introuvable"):
        parse_stock("In stock")
