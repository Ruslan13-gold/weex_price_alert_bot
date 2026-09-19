"""Вспомогательные функции."""


def format_number(value: float, decimals: int = 2) -> str:
    return f"{value:,.{decimals}f}"