
"""Manage contacts and export, back up, and restore an address book."""

import csv
import hashlib
import json
import logging
import re
from pathlib import Path

contacts = {}


def add_contact(full_name, phone, email="", city="Unknown"):
    """Add a contact if the phone number contains exactly 10 digits."""
    if not re.fullmatch(r"[0-9]{10}", phone):
        print("Invalid phone number for", full_name)
        return False

    contacts[full_name] = {
        "phone": phone,
        "email": email,
        "city": city,
    }
    return True


def contact_id(full_name):
    """Return a short SHA-256-based contact identifier."""
    return hashlib.sha256(full_name.encode("utf-8")).hexdigest()[:12]


def search_contacts(text):
    """Find contacts by name or phone number."""
    found = []
    for name, info in contacts.items():
        if text.lower() in name.lower() or text in info["phone"]:
            found.append(name)
    return found


def update_city(full_name, city):
    """Update a contact's city if the contact exists."""
    if full_name not in contacts:
        logging.warning("No contact named %s", full_name)
        return False

    contacts[full_name]["city"] = city
    return True


def contacts_by_city():
    """Group contact names by city."""
    grouped = {}
    for name, info in contacts.items():
        grouped.setdefault(info["city"], []).append(name)
    return grouped


def print_directory():
    """Print the sorted contact directory."""
    for index, name in enumerate(sorted(contacts), start=1):
        print(index, name, contacts[name]["phone"])


def export_csv(file_name="contacts.csv"):
    """Export contacts to a UTF-8 CSV file."""
    with Path(file_name).open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        for name, info in contacts.items():
            writer.writerow(
                [name, info["phone"], info["email"], info["city"]]
            )


def backup_book(file_name="contacts.json"):
    """Back up contacts as JSON instead of using pickle."""
    with Path(file_name).open("w", encoding="utf-8") as file:
        json.dump(contacts, file, indent=2)


def restore_book(file_name="contacts.json"):
    """Restore contacts from a JSON backup."""
    with Path(file_name).open("r", encoding="utf-8") as file:
        restored = json.load(file)

    if not isinstance(restored, dict):
        raise ValueError("Invalid address book backup format")

    for name, info in restored.items():
        if (
            not isinstance(name, str)
            or not isinstance(info, dict)
            or not isinstance(info.get("phone"), str)
            or not isinstance(info.get("email"), str)
            or not isinstance(info.get("city"), str)
        ):
            raise ValueError("Invalid contact in address book backup")

    return restored


def main():
    """Demonstrate the address book functions."""
    logging.basicConfig(
        level=logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    add_contact("Neha Sharma", "9876543210", "neha@example.com", "Bengaluru")
    add_contact("Rahul Verma", "9123456780", "rahul@example.com", "Mysuru")
    add_contact("Test User", "12345")
    add_contact("Kavya Nair", "9988776655", city="Bengaluru")

    update_city("Rahul Verma", "Chennai")
    update_city("Nobody", "Delhi")

    print_directory()
    print("Search 'ra':", search_contacts("ra"))
    print("By city:", contacts_by_city())
    print("Id for Neha:", contact_id("Neha Sharma"))

    export_csv()
    backup_book()
    restored = restore_book()

    print(
        "Contacts restored:",
        len(restored),
        "| first:",
        sorted(restored)[0],
    )
    print(
        "Restored contacts match the in-memory address book:",
        restored == contacts,
    )


if __name__ == "__main__":
    main()
