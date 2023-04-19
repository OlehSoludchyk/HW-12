import pickle
import re
from collections import UserDict
from datetime import date


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            print('There isn\'t contact with this name or number.')
        except ValueError:
            print('''Please enter the correct format of name and phone number.
            Correct format:
            1. The length of the nunber must be only 12 digits.
            2. Birthday format: YYYY-MM-DD.
            2. Use a gap between name, number and birthday.''')
    return wrapper

class Field:
    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, new_value):
        self._value = new_value
    
    def __str__(self):
        return self.value

class Name(Field):
    def __init__(self, value):
      if not value:
        raise ValueError('Name cannot be empty')
      super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if value:
            if not isinstance(value, str):
                raise TypeError('Phone must be a string')
            if not value.isdigit():
                raise ValueError('Phone must be a combination of digits')
            if len(value) != 12:
                raise ValueError('Phone number must have a 12 digits')
        super().__init__(value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if new_value and not isinstance(new_value, str):
            raise TypeError('Phone must be a string')
        elif new_value and len(new_value) != 12:
            raise ValueError('Phone must be a string of length 12')
        self._value = new_value

class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if new_value and not isinstance(new_value, date):
            raise ValueError('Birthday must have a format yyyy-mm-dd')
        self._value = new_value

    def replace(self, year):
        if self._value:
            self._value = date(self._value.year, self._value.month, self._value.day)

class Record:
    def __init__(self, name, phone=None, birthday=None):
        self.name = name
        self.phones = []
        if phone:
            self.add_phone(phone)
        if birthday:
            self.birthday = birthday
        else:
            self.birthday = None

    def add_phone(self, phone):
        self.phones.append(phone)

    def remove_phone(self, phone):
        if phone in self.phones:
            self.phones.remove(phone)

    def edit_phone(self, old_phone, new_phone):
        for i, phone in enumerate(self.phones):
            if phone.value == old_phone.value:
                self.phones[i] = new_phone

    def change_phone(self, old_phone, new_phone):
        if self.edit_phone(old_phone, new_phone):
            print('Phone number was changed.')

    def days_to_birthday(self):
        if not self.birthday:
            return None
        today = date.today()
        next_birthday = self.birthday.replace(year=today.year)
        if next_birthday and next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
            if next_birthday.year - today.year > 1:
                return None
        if next_birthday:
            days_to_birthday = (next_birthday - today).days
            return days_to_birthday
    
    def __str__(self):
        return f"{self.name} : {','.join([str(p) for p in self.phones])} {str(self.birthday) if self.birthday else ''}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record
        return f"Record with name {str(record.name)} add"

    def save(self, file_path):
        with open(file_path, 'wb') as file:
            pickle.dump(self.data, file)

    @classmethod
    def load(cls, file_path):
        with open(file_path, 'rb') as file:
            data = pickle.load(file)
        address_book = cls()
        address_book.data = data
        return address_book

    def remove_record(self, name):
        if name in self.data:
            del self.data[name]
            return True
        return False
    
    def find(self, param):
        result = []
        for rec in self.data.values():
            if param.lower() in str(rec).lower():
                result.append(rec)
        if result:
            return '\n'.join([str(r) for r in result])
        return f"No contact found with param {param}"
    
    # def find_records_by_name(self, name):
    #     found_records = []
    #     for record_name in self.data.keys():
    #         if record_name.lower() == name.lower():
    #             found_records.append(self.data[record_name])
    #     return found_records

    # def find_records_by_phone(self, phone):
    #     found_records = []
    #     for record in self.data.values():
    #         for record_phone in record.phones:
    #             if record_phone.value == phone:
    #                 found_records.append(record)
    #     return found_records

    def iterator(self, n=2):
        num_items = len(self.data)
        i = 0
        while i < num_items:
            result = []
            for key, value in list(self.items())[i:i + n]:
                result.append(f"{key}: {', '.join([phone.value for phone in value.phones])}")
            yield result
            i += n
        if len(result) < n:
            yield []
    
    def __str__(self):
        if self.data:
            return "\n".join([str(r) for r in self.data.values()])
        return "No contacts yet"

@input_error
def add_contact(user_input, address_book):
    match = re.match(r'add (\w+) (\d{12}) ?(\d{4}-\d{2}-\d{2})?', user_input)
    if match:
        name = match.group(1)
        phone = match.group(2)
        birthday = match.group(3)
        record_name = Name(name)
        if birthday:
            record_birthday = Birthday(date.fromisoformat(birthday))
        else:
            record_birthday = None
        record = Record(record_name, Phone(phone), record_birthday)
        return address_book.add_record(record)
    else:
      raise ValueError

def show_all_contacts(address_book):
    return str(address_book)
    # if address_book:
    #     for name, record in address_book.items():
    #         phone_numbers = ', '.join([phone.value for phone in record.phones])
    #         birthday = record.birthday.value.strftime('%Y-%m-%d') if record.birthday else ''
    #         days_to_birthday = record.days_to_birthday()
    #         if days_to_birthday:
    #             print(f'{name}: {phone_numbers}  {birthday} \
    #                    {days_to_birthday} days until birthday')
    #         else:
    #             print(f'{name}: {phone_numbers} {birthday}')
    # else:
    #     print('There are no contacts.')

def remove_contact(user_input, address_book):
    match = re.match(r'remove (\w+)', user_input)
    if match:
        name = match.group(1)
        if address_book.remove_record(name):
            print(f'Contact {name} has been removed.')
        else:
            print(f'There is no contact with name "{name}".')

@input_error
def find_contacts(user_input, address_book):
    if len(user_input) < 3:
        return "Find param must bu greater the three symbols"
    return address_book.find(user_input)
    # match = re.match(r'find (\w+)', user_input)
    # if match:
    #     name_or_phone = match.group(1)
    #     records_by_name = address_book.find_records_by_name(name_or_phone)
    #     records_by_phone = address_book.find_records_by_phone(name_or_phone)
    #     if records_by_name or records_by_phone:
    #         print('Contacts found:')
    #         for record in records_by_name + records_by_phone:
    #             for phone in record.phones:
    #                 if record.birthday:
    #                     print(f"{record.name.value} - {phone.value}")
    #                     print(f"{record.name.value}'s birthday - "
    #                           f"{record.birthday.value.strftime('%Y-%m-%d')}")
    #                 else:
    #                     print(f"{record.name.value} - {phone.value}")
    #     else:
    #         print('No contacts were found.')
    # else:
    #     raise KeyError
    
def search_contacts(user_input, address_book):
    match = re.match(r'search (\w+)', user_input)
    if match:
        search_string = match.group(1)
        found_contacts = {}
        for name, record in address_book.items():
            if (search_string in name or 
                any(search_string in phone.value for phone in record.phones)):
                found_contacts[name] = record
        if found_contacts:
            for name, record in found_contacts.items():
                phone_numbers = ', '.join([phone.value for phone in record.phones])
                birthday = record.birthday.value.strftime('%Y-%m-%d') if record.birthday else ''
                days_to_birthday = record.days_to_birthday()
                if days_to_birthday:
                    print(f'{name}: {phone_numbers}  {birthday} '
                          f'{days_to_birthday} days until birthday')
                else:
                    print(f'{name}: {phone_numbers} {birthday}')
        else:
            print(f'No contacts found for "{search_string}"')

def show_contact_book(address_book):
    iterator = address_book.iterator()
    while True:
        result = next(iterator, None)
        if result is None:
            break
        print('\n'.join(result))
        input('Press any key to continue...')

def change_phone(user_input, address_book):
    match = re.match(r'change (\w+) (\d{12}) (\d{12})', user_input)
    if match:
        name = match.group(1)
        old_phone = match.group(2)
        new_phone = match.group(3)
        if name in address_book.data:
            record = address_book.data[name]
            old_phone = Phone(old_phone)
            new_phone = Phone(new_phone)
            record.change_phone(old_phone, new_phone)

def main():
    print('''What can this bot do?
    1. Save the contact (name, phone number and birthday). 
    Please, remember: number - only 12 digits. Birthday format: YYYY-MM-DD.
    Use command: add [name] [number] [birthday].
    2. Change the phone number of the recorded contact. Please, remember: number - only 12 digits.
    Use command: change [name] [old_number] [new_number]
    3. Show all previously saved contacts with their names, phones and birthdays.
    Use command: show all.
    4. If your adress book contain a lots of contacts, you can see the parts of your book. 2 contacts at a time.
    Use command: show in parts. And then press 'Enter' to see the next page. 
    5. Remove the contact.
    Use command: remove [name]
    6. Find the contact by name or by phone.
    Use command: find [name] or [phone]
    7. Search the contact by the part of phone or name.
    Use command: search [part of user's name or phone]
    Have a nice day!''')
    
    file_path = 'address_book.pickle'

    try:
        address_book = AddressBook.load(file_path)
    except FileNotFoundError:
        address_book = AddressBook()

    while True:
        user_input = input('Enter a command >>> ')
        if user_input.lower() == 'hello':
            print('How can I help you?')
        elif user_input.lower().startswith('add'):
            print(add_contact(user_input, address_book))
        elif user_input.lower() == 'show all':
            print(show_all_contacts(address_book))
        elif user_input.lower().startswith('remove'):
            remove_contact(user_input, address_book)
        elif user_input.lower().startswith('find'):
            data = user_input.removeprefix('find').strip()
            print(find_contacts(data, address_book))
        elif user_input.lower().startswith('search'):
            search_contacts(user_input, address_book)
        elif user_input.lower() == 'show in parts':
            show_contact_book(address_book)
        elif user_input.lower().startswith('change'):
            change_phone(user_input, address_book)
        elif user_input.lower() in ['exit', 'close', 'good bye']:
            address_book.save(file_path)
            print('Good bye!')
            raise SystemExit
        else:
            print('Sorry, I don\'t understand you. Use the available command.')


if __name__ == '__main__':
    main()