#cli_bot/main.py
"""Головний модуль персонального помічника."""

from difflib import get_close_matches

from colorama import Fore, Style, init

from . import handlers
from .help_text import help_text
from .parser import parse_input
from .storage import load_data, save_data

init(autoreset=True)

WELCOME_BANNER = r"""
 _____                _                 _    ______         _
/  __ \              | |               | |   | ___ \       | |
| /  \/  ___   _ __  | |_   __ _   ___ | |_  | |_/ /  ___  | |_
| |     / _ \ | '_ \ | __| / _` | / __|| __| | ___ \ / _ \ | __|
| \__/\| (_) || | | || |_ | (_| || (__ | |_  | |_/ /| (_) || |_
 \____/ \___/ |_| |_| \__| \__,_| \___| \__| \____/  \___/  \__|
"""

COMMANDS = [
    "hello",
    "add",
    "change",
    "phone",
    "all",
    "name",
    "delete",
    "add-address",
    "add-email",
    "email",
    "add-birthday",
    "show-birthday",
    "birthdays",
    "birthdays-in",
    "add-note",
    "find-note",
    "show-notes",
    "edit-note",
    "delete-note",
    "add-tags",
    "find-by-tag",
    "sort-notes-by-tag",
    "help",
    "close",
    "exit",
]


def suggest_command(command: str) -> str | None:
    """Повертає найбільш схожу команду."""

    matches = get_close_matches(
        command,
        COMMANDS,
        n=1,
        cutoff=0.6,
    )

    return matches[0] if matches else None


def execute_command(command: str, args: list[str], book, notes):
    """Виконує команду користувача."""

    command_handlers = {
        "hello": lambda: handlers.hello(),
        "add": lambda: handlers.add_contact(args, book),
        "change": lambda: handlers.change_contact(args, book),
        "phone": lambda: handlers.show_phone(args, book),
        "all": lambda: handlers.show_all(book),
        "name": lambda: handlers.find_contact(args, book),
        "delete": lambda: handlers.delete_contact(args, book),
        "add-address": lambda: handlers.add_address(args, book),
        "add-email": lambda: handlers.add_email(args, book),
        "email": lambda: handlers.find_by_email(args, book),
        "add-birthday": lambda: handlers.add_birthday(args, book),
        "show-birthday": lambda: handlers.show_birthday(args, book),
        "birthdays": lambda: handlers.birthdays(book),
        "birthdays-in": lambda: handlers.birthdays_in(args, book),
        "add-note": lambda: handlers.add_note(args, notes),
        "find-note": lambda: handlers.find_note(args, notes),
        "show-notes": lambda: handlers.show_notes(notes),
        "edit-note": lambda: handlers.edit_note(args, notes),
        "delete-note": lambda: handlers.delete_note(args, notes),
        "add-tags": lambda: handlers.add_tags(args, notes),
        "find-by-tag": lambda: handlers.find_by_tag(args, notes),
        "sort-notes-by-tag": lambda: handlers.sort_notes_by_tag(notes),
        "help": lambda: help_text(),
    }

    handler = command_handlers.get(command)

    if handler is None:
        return None

    return handler()


def main():
    """Запускає CLI та керує його робочим циклом."""

    book, notes = load_data()

    print(Fore.GREEN + "=" * 50)
    print(f"{Fore.CYAN}{WELCOME_BANNER}")
    print(Fore.GREEN + "Персональний помічник")
    print(Fore.GREEN + "Введіть help для списку команд.")
    print(Fore.GREEN + "=" * 50)

    try:
        while True:
            user_input = input(
                Fore.CYAN + "\nВведіть команду: " + Style.RESET_ALL
            )

            command, args = parse_input(user_input)

            if not command:
                continue

            if command in ("close", "exit"):
                print(Fore.GREEN + "Завершення роботи.")
                break

            try:
                result = execute_command(command, args, book, notes)

                if result is not None:
                    print(Fore.GREEN + str(result))
                    continue

                # Якщо команда невідома, пропонуємо схожу.
                suggestion = suggest_command(command)

                if suggestion:
                    answer = input(
                        f"Можливо, ви мали на увазі '{suggestion}'? (y/n): "
                    ).strip().lower()

                    if answer in ("y", "yes", "так", "т"):
                        result = execute_command(
                            suggestion,
                            args,
                            book,
                            notes,
                        )

                        if result is not None:
                            print(Fore.GREEN + str(result))
                    else:
                        print(Fore.RED + "Команда не знайдена.")

                else:
                    print(
                        Fore.RED
                        + "Невідома команда. Введіть help."
                    )

            except (ValueError, KeyError, IndexError) as error:
                print(Fore.RED + f"Помилка: {error}")

    except (KeyboardInterrupt, EOFError):
        print(Fore.YELLOW + "\nРоботу перервано користувачем.")

    finally:
        try:
            save_data(book, notes)
            print(Fore.GREEN + "Дані збережено.")
        except OSError as error:
            print(Fore.RED + f"Не вдалося зберегти дані: {error}")


if __name__ == "__main__":
    main()