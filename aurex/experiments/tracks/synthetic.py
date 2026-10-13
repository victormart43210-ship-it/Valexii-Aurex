"""Deterministic fixtures used to validate AUREX itself."""

from collections.abc import Callable


def identity_solver() -> Callable[[str], str]:
    return lambda prompt: prompt


def uppercase_solver() -> Callable[[str], str]:
    return lambda prompt: prompt.upper()
