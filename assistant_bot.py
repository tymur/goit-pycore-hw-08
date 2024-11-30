import pickle
from collections import UserDict
from datetime import datetime, timedelta


# Декоратор для обробки помилок
def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f"Error: {e}"
        except KeyError:
            return "Error: Contact not found."
        except IndexError:
            return "Error: Invalid input. Please provide correct arguments."
    return wrapper


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if self.is_valid(value):
            super().__init__(value)
        else:
            raise ValueError("Name must be a non-empty string.")

    @staticmethod
    def is_valid(value):
        return isinstance(value, str) and len(value.strip()) > 0


class Phone(Field):
    def __init__(self, value):
        if self.is_valid(value):
            super().__init__(value)
        else:
            raise ValueError("Phone number must be 10 digits.")

    @staticmethod
    def is_valid(value):
        return isinstance(value, str) and value.isdigit() and len(value) == 10


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        if isinstance(phone, Phone):
            self.phones.append(phone)
        else:
            raise ValueError("Invalid phone type.")

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        self.remove_phone(old_phone)
        self.add_phone(Phone(new_phone))

    def add_birthday(self, birthday):
        if isinstance(birthday, Birthday):
            self.birthday = birthday
        else:
            raise ValueError("Invalid birthday type.")

    def days_to_birthday(self):
        if not self.birthday:
            return None
        today = datetime.today().date()
        next_birthday = self.birthday.value.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return (next_birthday - today).days

    def __str__(self):
        phones = ", ".join([str(phone) for phone in self.phones])
        birthday = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "N/A"
        return f"{self.name.value}: Phones: [{phones}], Birthday: {birthday}"


class AddressBook(UserDict):
    def add_record(self, record):
        if isinstance(record, Record):
            self.data[record.name.value] = record
        else:
            raise ValueError("Invalid record type.")

    def find_record(self, name):
        return self.data.get(name)

    def get_upcoming_birthdays(self, days=7):
        today = datetime.today().date()
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                next_birthday = record.birthday.value.replace(year=today.year)
                if next_birthday < today:
                    next_birthday = next_birthday.replace(year=today.year + 1)
                if 0 <= (next_birthday - today).days <= days:
                    upcoming_birthdays.append(record)
        return upcoming_birthdays

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())


# Функції серіалізації та десеріалізації
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


# Функції-обробники
@input_error
def add_contact(args, book):
    name, phone, *rest = args
    birthday = rest[0] if rest else None
    record = book.find_record(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(Phone(phone))
    if birthday:
        record.add_birthday(Birthday(birthday))
    return message


@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find_record(name)
    if not record:
        raise KeyError
    record.edit_phone(old_phone, new_phone)
    return f"Contact {name} updated."


@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find_record(name)
    if not record:
        raise KeyError
    phones = ", ".join([str(phone) for phone in record.phones])
    return f"{name}: {phones}"


@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find_record(name)
    if not record:
        raise KeyError
    record.add_birthday(Birthday(birthday))
    return f"Birthday added for {name}."


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find_record(name)
    if not record or not record.birthday:
        raise KeyError
    return f"{name}'s birthday is {record.birthday.value.strftime('%d.%m.%Y')}."


@input_error
def upcoming_birthdays(_, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays."
    return "\n".join(str(record) for record in upcoming)


def show_all(book):
    return str(book)


# Основна програма
def main():
    book = load_data()  # Завантаження адресної книги з файлу
    print("Welcome to the assistant bot!")
    
    while True:
        user_input = input("Enter a command: ").strip()
        command, *args = user_input.split()

        if command in ["close", "exit"]:
            print("Saving data...")
            save_data(book)  # Збереження даних перед виходом
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(upcoming_birthdays(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
