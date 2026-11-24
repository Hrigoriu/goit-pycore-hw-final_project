#cli_bot/address_book.py
"""Адресна книга та робота з контактами."""

from collections import UserDict
from datetime import date, timedelta

from .models import Record


class AddressBook(UserDict):
    """Колекція контактів."""

    def add_record(self, record: Record) -> None:
        """Додає контакт до адресної книги."""

        name = record.name.value

        if name in self.data:
            raise ValueError(f"Контакт '{name}' вже існує.")

        self.data[name] = record

    def find(self, name: str) -> Record | None:
        """Шукає контакт за ім'ям."""

        return self.data.get(name)

    def delete(self, name: str) -> None:
        """Видаляє контакт."""

        if name not in self.data:
            raise ValueError(f"Контакт '{name}' не знайдено.")

        del self.data[name]

    def find_by_phone(self, phone: str) -> Record | None:
        """Шукає контакт за номером телефону."""

        for record in self.data.values():
            if record.find_phone(phone):
                return record

        return None

    def find_by_email(self, email: str) -> Record | None:
        """Шукає контакт за email."""

        for record in self.data.values():
            if record.find_email(email):
                return record

        return None

    def search(self, query: str) -> list[Record]:
        """Шукає контакти за частковим збігом імені."""

        query = query.lower().strip()

        return [
            record
            for record in self.data.values()
            if query in record.name.value.lower()
        ]

    @staticmethod
    def _birthday_in_year(birthday: date, year: int) -> date:
        """Коректно обробляє день народження 29 лютого."""

        try:
            return birthday.replace(year=year)
        except ValueError:
            return date(year, 2, 28)

    def get_upcoming_birthdays(self, days: int = 7) -> list[dict]:
        """Повертає дні народження на заданий період.

        День народження у вихідний переноситься на понеділок.
        """

        if days < 0:
            raise ValueError("Кількість днів не може бути від'ємною.")

        today = date.today()
        last_day = today + timedelta(days=days)
        result = []

        for record in self.data.values():
            if not record.birthday:
                continue

            birthday = record.birthday.value
            next_birthday = self._birthday_in_year(birthday, today.year)

            if next_birthday < today:
                next_birthday = self._birthday_in_year(
                    birthday,
                    today.year + 1,
                )

            congratulation_date = next_birthday

            # Якщо день народження у вихідний,
            # переносимо привітання на понеділок.
            if congratulation_date.weekday() == 5:
                congratulation_date += timedelta(days=2)
            elif congratulation_date.weekday() == 6:
                congratulation_date += timedelta(days=1)

            if today <= next_birthday <= last_day:
                result.append(
                    {
                        "name": record.name.value,
                        "birthday": next_birthday,
                        "congratulation_date": congratulation_date,
                    }
                )

        return sorted(
            result,
            key=lambda item: (
                item["congratulation_date"],
                item["name"].lower(),
            ),
        )

    def birthdays_in(self, days: int) -> list[Record]:
        """Шукає контакти, у яких день народження через N днів."""

        if days < 0:
            raise ValueError("Кількість днів не може бути від'ємною.")

        target_date = date.today() + timedelta(days=days)
        today = date.today()
        result = []

        for record in self.data.values():
            if not record.birthday:
                continue

            birthday = record.birthday.value
            next_birthday = self._birthday_in_year(birthday, today.year)

            if next_birthday < today:
                next_birthday = self._birthday_in_year(
                    birthday,
                    today.year + 1,
                )

            if next_birthday == target_date:
                result.append(record)

        return result

    def __str__(self) -> str:
        """Повертає список контактів."""

        if not self.data:
            return "Адресна книга порожня."

        return "\n\n".join(
            str(record) for record in self.data.values()
        )