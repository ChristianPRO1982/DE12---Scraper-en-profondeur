import re
from decimal import Decimal, InvalidOperation

RATING_VALUES = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


def clean_text(value: str | None) -> str:
    if value is None:
        return ""
    return " ".join(value.split())


def parse_price(value: str | None) -> Decimal:
    cleaned_value = clean_text(value)
    if not cleaned_value:
        raise ValueError("Prix absent")

    normalized_value = cleaned_value.replace("£", "").replace(",", ".")
    try:
        return Decimal(normalized_value)
    except InvalidOperation as error:
        raise ValueError(f"Prix invalide: {value!r}") from error


def parse_rating(class_value: str | None) -> int:
    classes = clean_text(class_value).split()

    for class_name in classes:
        if class_name in RATING_VALUES:
            return RATING_VALUES[class_name]

    raise ValueError(f"Note introuvable dans la classe CSS: {class_value!r}")


def parse_int(value: str | None) -> int:
    cleaned_value = clean_text(value)
    if not cleaned_value:
        raise ValueError("Entier absent")

    return int(cleaned_value)


def parse_stock(value: str | None) -> int:
    cleaned_value = clean_text(value)
    stock_match = re.search(r"\((\d+)\s+available\)", cleaned_value)

    if not stock_match:
        raise ValueError(f"Stock introuvable: {value!r}")

    return int(stock_match.group(1))
