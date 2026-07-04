from __future__ import annotations

from typing import Iterable


def fmt_pct(v) -> str:
    if v is None:
        return "n/a"
    return f"{float(v):.2f}%"


def fmt_num(v, decimals: int = 2) -> str:
    if v is None:
        return "n/a"
    return f"{float(v):,.{decimals}f}"


def fmt_currency(v) -> str:
    if v is None:
        return "n/a"
    return f"${float(v):,.2f}"


def section(title: str, body: str) -> str:
    return f"## {title}\n\n{body}\n"


def bullet_list(items: Iterable[str]) -> str:
    items = [str(item) for item in items if item]
    return "\n".join(f"- {item}" for item in items)
