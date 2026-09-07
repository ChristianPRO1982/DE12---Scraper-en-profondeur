from books_catalog_scraper.error_policy import (
    DEFAULT_MAX_ERRORS,
    has_exceeded_error_limit,
    parse_max_errors,
)


def test_parse_max_errors_uses_default_for_empty_value() -> None:
    assert parse_max_errors(None) == DEFAULT_MAX_ERRORS
    assert parse_max_errors("") == DEFAULT_MAX_ERRORS


def test_parse_max_errors_accepts_zero() -> None:
    assert parse_max_errors("0") == 0
    assert parse_max_errors(0) == 0


def test_parse_max_errors_rejects_negative_value() -> None:
    try:
        parse_max_errors("-1")
    except ValueError as error:
        assert "positif ou nul" in str(error)
    else:
        raise AssertionError("ValueError attendu")


def test_has_exceeded_error_limit() -> None:
    assert has_exceeded_error_limit(1, 0)
    assert not has_exceeded_error_limit(1, 1)
