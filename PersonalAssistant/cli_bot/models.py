#cli_bot/models.py
"""Моделі даних контактів."""

import re
from datetime import datetime


class Field:
    """Базовий клас для полів запису."""

    def __init__(self, value: str):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class Name(Field):
    """Ім'я контакту."""

    def __init__(self, value: str):
        value = value.strip()

        if not value:
            raise ValueError("Ім'я не може бути порожнім.")

        super().__init__(value)


class Phone(Field):
    """Телефон із перевіркою українського формату."""

    def __init__(self, value: str):
        normalized = self.normalize(value)

        if not self.validate(normalized):
            raise ValueError(
                "Телефон повинен містити 10 цифр, "
                "наприклад 0501234567."
            )

        super().__init__(normalized)

    @staticmethod
    def normalize(phone: str) -> str:
        """Видаляє символи форматування з номера телефону."""

        digits = re.sub(r"\D", "", phone)

        # Перетворюємо міжнародний формат +380XXXXXXXXX
        # на звичайний український формат 0XXXXXXXXX.
        if digits.startswith("380") and len(digits) == 12:
            digits = "0" + digits[3:]

        return digits

    @staticmethod
    def validate(phone: str) -> bool:
        """Перевіряє номер на відповідність формату."""

        return (
            isinstance(phone, str)
            and len(phone) == 10
            and phone.isdigit()
            and phone.startswith("0")
        )


class Email(Field):
    """Email-адреса з перевіркою формату."""

    EMAIL_PATTERN = re.compile(
        r"^[A-Za-z0-9._%+-]+@"
        r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    )

    def __init__(self, value: str):
        value = value.strip()

        if not self.EMAIL_PATTERN.fullmatch(value):
            raise ValueError("Некоректний формат email.")

        super().__init__(value)


class Address(Field):
    """Поштова адреса контакту."""

    def __init__(self, value: str):
        value = " ".join(value.split())

        if not value:
            raise ValueError("Адреса не може бути порожньою.")

        super().__init__(value)


class Birthday(Field):
    """Дата народження контакту."""

    def __init__(self, value: str):
        try:
            birthday = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError(
                "Некоректна дата. Формат: DD.MM.YYYY."
            )

        super().__init__(birthday)

    def __str__(self) -> str:
        return self.value.strftime("%d.%m.%Y")


class Record:
    """Модель одного контакту."""

    def __init__(self, name: str):
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.emails: list[Email] = []
        self.address: Address | None = None
        self.birthday: Birthday | None = None

    def add_phone(self, phone: str) -> None:
        """Додає телефон до контакту."""

        new_phone = Phone(phone)

        if self.find_phone(new_phone.value):
            raise ValueError("Цей телефон вже існує у контакті.")

        self.phones.append(new_phone)

    def find_phone(self, phone: str) -> Phone | None:
        """Шукає телефон у контакті."""

        normalized = Phone.normalize(phone)

        return next(
            (item for item in self.phones if item.value == normalized),
            None,
        )

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        """Змінює телефон контакту."""

        old = self.find_phone(old_phone)

        if old is None:
            raise ValueError("Старий телефон не знайдено.")

        new = Phone(new_phone)

        if self.find_phone(new.value) and old.value != new.value:
            raise ValueError("Новий телефон вже існує у контакті.")

        old.value = new.value

    def remove_phone(self, phone: str) -> None:
        """Видаляє телефон."""

        existing = self.find_phone(phone)

        if existing is None:
            raise ValueError("Телефон не знайдено.")

        self.phones.remove(existing)

    def add_email(self, email: str) -> None:
        """Додає email."""

        new_email = Email(email)

        if self.find_email(new_email.value):
            raise ValueError("Такий email вже існує у контакті.")

        self.emails.append(new_email)

    def find_email(self, email: str) -> Email | None:
        """Шукає email у контакті."""

        email = email.strip().lower()

        return next(
            (item for item in self.emails if item.value.lower() == email),
            None,
        )

    def edit_email(self, old_email: str, new_email: str) -> None:
        """Змінює email."""

        old = self.find_email(old_email)

        if old is None:
            raise ValueError("Старий email не знайдено.")

        new = Email(new_email)

        if self.find_email(new.value) and old.value.lower() != new.value.lower():
            raise ValueError("Новий email вже існує.")

        old.value = new.value

    def add_address(self, address: str) -> None:
        """Додає або змінює адресу."""

        self.address = Address(address)

    def add_birthday(self, birthday: str) -> None:
        """Додає або змінює день народження."""

        self.birthday = Birthday(birthday)

    def change_name(self, new_name: str) -> None:
        """Змінює ім'я контакту."""

        self.name = Name(new_name)

    def __str__(self) -> str:
        """Формує текстове представлення контакту."""

        phones = "; ".join(phone.value for phone in self.phones) or "-"
        emails = "; ".join(email.value for email in self.emails) or "-"
        address = str(self.address) if self.address else "-"
        birthday = str(self.birthday) if self.birthday else "-"

        return (
            f"Ім'я: {self.name}\n"
            f"Телефони: {phones}\n"
            f"Email: {emails}\n"
            f"Адреса: {address}\n"
            f"День народження: {birthday}"
        )