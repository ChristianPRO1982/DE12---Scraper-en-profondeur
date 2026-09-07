from decimal import Decimal

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
    return Decimal(normalized_value)


def parse_rating(class_value: str | None) -> int:
    classes = clean_text(class_value).split()

    for class_name in classes:
        if class_name in RATING_VALUES:
            return RATING_VALUES[class_name]

    raise ValueError(f"Note introuvable dans la classe CSS: {class_value!r}")
