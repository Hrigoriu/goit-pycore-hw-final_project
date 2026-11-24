#cli_bot/parser.py
"""Модуль для розбору команд користувача."""

import shlex


def parse_input(user_input: str) -> tuple[str, list[str]]:
    """Розділяє введений рядок на команду та аргументи.

    Підтримує аргументи в лапках для багатослівних імен.
    Приклад: add "John Smith" 0501234567
    """
    try:
        parts = shlex.split(user_input.strip())
    except ValueError:
        return "", []

    if not parts:
        return "", []

    command = parts[0].lower()
    args = parts[1:]

    return command, args