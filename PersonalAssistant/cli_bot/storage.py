#cli_bot/storage.py
"""Збереження та завантаження даних персонального помічника."""

import pickle
from pathlib import Path

from .address_book import AddressBook
from .note_book import NoteBook


# Визначаємо кореневу папку проєкту.
BASE_DIR = Path(__file__).resolve().parent.parent

# Папка для зберігання даних усередині проєкту.
DATA_DIR = BASE_DIR / "data"


def _save_file(data, filename: str) -> None:
    """Зберігає об'єкт у файл через тимчасовий файл."""

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    file_path = DATA_DIR / filename
    temp_path = file_path.with_suffix(".tmp")

    with temp_path.open("wb") as file:
        pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)

    # Замінюємо основний файл після успішного запису.
    temp_path.replace(file_path)


def _load_file(filename: str, expected_type):
    """Завантажує об'єкт із файлу."""

    file_path = DATA_DIR / filename

    if not file_path.exists():
        return expected_type()

    try:
        with file_path.open("rb") as file:
            data = pickle.load(file)

        if not isinstance(data, expected_type):
            raise TypeError("Невідповідний формат даних.")

        return data

    except (
        pickle.UnpicklingError,
        EOFError,
        AttributeError,
        ImportError,
        IndexError,
        TypeError,
        OSError,
    ) as error:
        print(
            f"Попередження: не вдалося завантажити "
            f"{filename}: {error}"
        )
        print("Файл збережено. Завантаження розпочато з порожніх даних.")

        return expected_type()


def save_data(book: AddressBook, notes: NoteBook) -> None:
    """Зберігає адресну книгу та нотатки."""

    _save_file(book, "addressbook.pkl")
    _save_file(notes, "notes.pkl")


def load_data() -> tuple[AddressBook, NoteBook]:
    """Завантажує адресну книгу та нотатки."""

    book = _load_file("addressbook.pkl", AddressBook)
    notes = _load_file("notes.pkl", NoteBook)

    return book, notes