"""Вспомогательные функции."""

def format_number(value: float, decimals: int = 2) -> str:
    """Форматирует число с разделителями тысяч."""
    return f"{value:,.{decimals}f}"