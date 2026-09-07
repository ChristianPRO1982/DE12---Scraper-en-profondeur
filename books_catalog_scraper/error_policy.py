DEFAULT_MAX_ERRORS = 50


def parse_max_errors(value: str | int | None) -> int:
    if value in {None, ""}:
        return DEFAULT_MAX_ERRORS

    max_errors = int(value)
    if max_errors < 0:
        raise ValueError("Le parametre max_errors doit etre un entier positif ou nul")

    return max_errors


def has_exceeded_error_limit(error_count: int, max_errors: int) -> bool:
    return error_count > max_errors
