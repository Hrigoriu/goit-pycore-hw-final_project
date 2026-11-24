#cli_bot/note_book.py
"""Модуль управління нотатками та тегами."""

from collections import UserDict
from datetime import datetime


class Note:
    """Окрема нотатка."""

    def __init__(self, title: str, text: str, tags=None):
        title = title.strip()
        text = text.strip()

        if not title:
            raise ValueError("Назва нотатки не може бути порожньою.")

        if not text:
            raise ValueError("Текст нотатки не може бути порожнім.")

        self.title = title
        self.text = text
        self.created_at = datetime.now()
        self.tags = set(tag.lower() for tag in tags) if tags else set()

    def add_tags(self, tags: list[str]) -> None:
        """Додає теги до нотатки."""

        self.tags.update(tag.lower() for tag in tags if tag.strip())

    def __str__(self) -> str:
        """Формує текстове представлення нотатки."""

        tags = ", ".join(sorted(self.tags)) if self.tags else "немає"
        created = self.created_at.strftime("%d.%m.%Y %H:%M")

        return (
            f"Назва: {self.title}\n"
            f"Текст: {self.text}\n"
            f"Теги: {tags}\n"
            f"Створено: {created}"
        )


class NoteBook(UserDict):
    """Колекція нотаток."""

    def add(self, note: Note) -> None:
        """Додає нотатку, не допускаючи дублювання назви."""

        key = note.title.casefold()

        if key in self.data:
            raise ValueError(
                f"Нотатка '{note.title}' вже існує."
            )

        self.data[key] = note

    def find(self, query: str) -> list[Note]:
        """Шукає нотатки за назвою або текстом."""

        query = query.casefold().strip()

        if not query:
            raise ValueError("Введіть текст для пошуку.")

        return [
            note
            for note in self.data.values()
            if query in note.title.casefold()
            or query in note.text.casefold()
        ]

    def edit(self, title: str, new_text: str) -> None:
        """Редагує текст нотатки."""

        note = self.data.get(title.casefold())

        if note is None:
            raise ValueError(f"Нотатку '{title}' не знайдено.")

        new_text = new_text.strip()

        if not new_text:
            raise ValueError("Новий текст не може бути порожнім.")

        note.text = new_text

    def delete(self, title: str) -> None:
        """Видаляє нотатку."""

        key = title.casefold()

        if key not in self.data:
            raise ValueError(f"Нотатку '{title}' не знайдено.")

        del self.data[key]

    def add_tags(self, title: str, tags: list[str]) -> None:
        """Додає теги до нотатки."""

        note = self.data.get(title.casefold())

        if note is None:
            raise ValueError(f"Нотатку '{title}' не знайдено.")

        valid_tags = [tag.strip() for tag in tags if tag.strip()]

        if not valid_tags:
            raise ValueError("Введіть хоча б один тег.")

        note.add_tags(valid_tags)

    def find_by_tags(self, tags: list[str]) -> list[Note]:
        """Шукає нотатки за одним або декількома тегами."""

        search_tags = {
            tag.lower().strip()
            for tag in tags
            if tag.strip()
        }

        if not search_tags:
            raise ValueError("Введіть теги для пошуку.")

        return [
            note
            for note in self.data.values()
            if note.tags.intersection(search_tags)
        ]

    def sort_by_tags(self) -> list[Note]:
        """Сортує нотатки за тегами.

        Нотатки без тегів розміщуються в кінці.
        """

        return sorted(
            self.data.values(),
            key=lambda note: (
                not bool(note.tags),
                min(note.tags) if note.tags else "",
                note.title.casefold(),
            ),
        )

    def __str__(self) -> str:
        """Повертає список нотаток."""

        if not self.data:
            return "Нотаток поки немає."

        return "\n\n".join(
            str(note) for note in self.data.values()
        )