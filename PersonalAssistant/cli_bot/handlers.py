#cli_bot/handlers.py
"""Обробники команд персонального помічника."""

from .address_book import AddressBook
from .models import Record
from .note_book import Note, NoteBook


def hello():
    """Привітання."""

    return "Вітаю! Чим можу допомогти?"


# -------------------- КОНТАКТИ --------------------


def add_contact(args: list[str], book: AddressBook) -> str:
    """Додає контакт або телефон."""

    if len(args) < 2:
        return 'Формат: add "Ім\'я" телефон'

    name = args[0]
    phone = args[1]

    record = book.find(name)

    if record is None:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return f"Контакт '{name}' додано."

    record.add_phone(phone)
    return f"Телефон додано до контакту '{name}'."


def change_contact(args: list[str], book: AddressBook) -> str:
    """Редагує телефон, ім'я, адресу, email або день народження."""

    if len(args) < 3:
        return (
            "Формат: change <ім'я> "
            "phone|name|address|email|birthday ..."
        )

    name, field, *params = args
    record = book.find(name)

    if record is None:
        return f"Контакт '{name}' не знайдено."

    field = field.lower()

    if field == "phone":
        if len(params) != 2:
            return "Формат: change <ім'я> phone <старий> <новий>"

        record.edit_phone(params[0], params[1])
        return "Телефон змінено."

    if field == "name":
        if len(params) != 1:
            return "Формат: change <ім'я> name <нове_ім'я>"

        new_name = params[0]

        if book.find(new_name):
            return "Контакт із таким ім'ям уже існує."

        record.change_name(new_name)
        book.data.pop(name)
        book.add_record(record)

        return "Ім'я контакту змінено."

    if field == "address":
        if not params:
            return "Введіть нову адресу."

        record.add_address(" ".join(params))
        return "Адресу оновлено."

    if field == "email":
        if len(params) != 2:
            return "Формат: change <ім'я> email <старий> <новий>"

        record.edit_email(params[0], params[1])
        return "Email змінено."

    if field == "birthday":
        if len(params) != 1:
            return "Формат: change <ім'я> birthday DD.MM.YYYY"

        record.add_birthday(params[0])
        return "День народження оновлено."

    return "Невідоме поле. Використовуйте phone, name, address, email, birthday."


def delete_contact(args: list[str], book: AddressBook) -> str:
    """Видаляє контакт."""

    if not args:
        return 'Формат: delete "Ім\'я"'

    name = args[0]
    book.delete(name)

    return f"Контакт '{name}' видалено."


def show_phone(args: list[str], book: AddressBook) -> str:
    """Показує телефони контакту."""

    if not args:
        return 'Формат: phone "Ім\'я"'

    record = book.find(args[0])

    if record is None:
        return "Контакт не знайдено."

    phones = "; ".join(phone.value for phone in record.phones)

    return phones or "Телефони не збережені."


def show_all(book: AddressBook) -> str:
    """Показує всі контакти."""

    return str(book)


def find_contact(args: list[str], book: AddressBook) -> str:
    """Шукає контакти за частиною імені."""

    if not args:
        return "Формат: name <частина_імені>"

    query = " ".join(args)
    results = book.search(query)

    if not results:
        return "Контакти не знайдено."

    return "\n\n".join(str(record) for record in results)


def add_birthday(args: list[str], book: AddressBook) -> str:
    """Додає день народження контакту."""

    if len(args) != 2:
        return 'Формат: add-birthday "Ім\'я" DD.MM.YYYY'

    name, birthday = args
    record = book.find(name)

    if record is None:
        return "Контакт не знайдено."

    record.add_birthday(birthday)

    return "День народження додано."


def show_birthday(args: list[str], book: AddressBook) -> str:
    """Показує день народження."""

    if not args:
        return 'Формат: show-birthday "Ім\'я"'

    record = book.find(args[0])

    if record is None:
        return "Контакт не знайдено."

    if record.birthday is None:
        return "День народження не вказаний."

    return str(record.birthday)


def birthdays(book: AddressBook) -> str:
    """Показує найближчі дні народження."""

    upcoming = book.get_upcoming_birthdays()

    if not upcoming:
        return "Найближчих днів народження немає."

    return "\n".join(
        f"{item['congratulation_date']}: {item['name']}"
        for item in upcoming
    )


def birthdays_in(args: list[str], book: AddressBook) -> str:
    """Показує день народження, який буде через задану кількість днів."""

    if len(args) != 1:
        return "Формат: birthdays-in <кількість_днів>"

    try:
        days = int(args[0])
    except ValueError:
        return "Кількість днів повинна бути цілим числом."

    records = book.birthdays_in(days)

    if not records:
        return f"Через {days} днів днів народження немає."

    names = ", ".join(record.name.value for record in records)

    return f"Через {days} днів день народження у: {names}."


def add_address(args: list[str], book: AddressBook)    -> str:
    """Додає адресу контакту."""

    if len(args) < 2:
        return 'Формат: add-address "Ім\'я" адреса'

    name = args[0]
    address = " ".join(args[1:])

    record = book.find(name)

    if record is None:
        return "Контакт не знайдено."

    record.add_address(address)

    return "Адресу додано."


def add_email(args: list[str], book: AddressBook) -> str:
    """Додає email контакту."""

    if len(args) != 2:
        return 'Формат: add-email "Ім\'я" email'

    name, email = args
    record = book.find(name)

    if record is None:
        return "Контакт не знайдено."

    # Перевіряємо, чи email належить іншому контакту.
    owner = book.find_by_email(email)

    if owner and owner.name.value != name:
        return "Цей email уже використовується іншим контактом."

    record.add_email(email)

    return "Email додано."


def find_by_email(args: list[str], book: AddressBook) -> str:
    """Шукає контакт за email."""

    if not args:
        return "Формат: email <email>"

    record = book.find_by_email(args[0])

    if record is None:
        return "Контакт із таким email не знайдено."

    return str(record)


# -------------------- НОТАТКИ --------------------


def add_note(args: list[str], notes: NoteBook) -> str:
    """Додає нотатку."""

    if len(args) < 2:
        return 'Формат: add-note "Назва" текст'

    title = args[0]
    text = " ".join(args[1:])

    notes.add(Note(title, text))

    return "Нотатку додано."


def find_note(args: list[str], notes: NoteBook) -> str:
    """Шукає нотатку за назвою або текстом."""

    if not args:
        return "Формат: find-note <пошуковий_запит>"

    query = " ".join(args)
    results = notes.find(query)

    if not results:
        return "Нотаток не знайдено."

    return "\n\n".join(str(note) for note in results)


def edit_note(args: list[str], notes: NoteBook) -> str:
    """Редагує нотатку."""

    if len(args) < 2:
        return 'Формат: edit-note "Назва" новий_текст'

    title = args[0]
    text = " ".join(args[1:])

    notes.edit(title, text)

    return "Нотатку оновлено."


def delete_note(args: list[str], notes: NoteBook) -> str:
    """Видаляє нотатку."""

    if not args:
        return 'Формат: delete-note "Назва"'

    notes.delete(args[0])

    return "Нотатку видалено."


def show_notes(notes: NoteBook) -> str:
    """Показує всі нотатки."""

    return str(notes)


def add_tags(args: list[str], notes: NoteBook) -> str:
    """Додає теги до нотатки."""

    if len(args) < 2:
        return 'Формат: add-tags "Назва" тег1 тег2'

    title = args[0]
    tags = args[1:]

    notes.add_tags(title, tags)

    return "Теги додано."


def find_by_tag(args: list[str], notes: NoteBook) -> str:
    """Шукає нотатки за тегами."""

    if not args:
        return "Формат: find-by-tag тег1 тег2"

    results = notes.find_by_tags(args)

    if not results:
        return "Нотаток із такими тегами не знайдено."

    return "\n\n".join(str(note) for note in results)


def sort_notes_by_tag(notes: NoteBook) -> str:
    """Сортує та показує нотатки за тегами."""

    sorted_notes = notes.sort_by_tags()

    if not sorted_notes:
        return "Нотаток поки немає."

    return "\n\n".join(str(note) for note in sorted_notes)