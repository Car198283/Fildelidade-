def normalize_cnpj(value: str | None) -> str | None:
    if value is None:
        return None

    digits = "".join(char for char in str(value) if char.isdigit())
    return digits or None


def validate_cnpj_digits(value: str | None) -> str:
    digits = normalize_cnpj(value)
    if not digits or len(digits) != 14:
        raise ValueError("CNPJ deve conter 14 numeros")
    return digits
