import json
import argparse
from pathlib import Path
from shutil import copy2

# File locations
PEOPLE_FILE = Path("data/people.json")
BACKUP_FILE = Path("data/people_backup.json")


def sort_by_name(person):
    """Sort by last name, first name, then birth year."""
    return (
        (person.get("last_name") or "").casefold(),
        (person.get("first_name") or "").casefold(),
        person.get("birth_year") or 9999,
    )


def sort_by_birth_year(person):
    """Sort by birth year, then last and first name."""
    return (
        person.get("birth_year") or 9999,
        (person.get("last_name") or "").casefold(),
        (person.get("first_name") or "").casefold(),
    )


def main():
    parser = argparse.ArgumentParser(
        description="Sort people.json records."
    )

    parser.add_argument(
        "--by",
        choices=["name", "year"],
        default="name",
        help="Sort by name (default) or birth year",
    )

    args = parser.parse_args()

    if not PEOPLE_FILE.exists():
        print(f"File not found: {PEOPLE_FILE}")
        return

    # Read existing people
    with PEOPLE_FILE.open("r", encoding="utf-8") as file:
        people = json.load(file)

    if not isinstance(people, list):
        print("Error: people.json must contain a list.")
        return

    if not all(isinstance(person, dict) for person in people):
        print("Error: Every person must be a JSON object.")
        return

    # Select sorting method
    if args.by == "year":
        people.sort(key=sort_by_birth_year)
    else:
        people.sort(key=sort_by_name)

    # Back up original file
    copy2(PEOPLE_FILE, BACKUP_FILE)

    # Write sorted records
    with PEOPLE_FILE.open("w", encoding="utf-8") as file:
        json.dump(people, file, indent=2, ensure_ascii=False)
        file.write("\n")

    print(f"Successfully sorted {len(people)} people by {args.by}.")
    print(f"Backup saved to: {BACKUP_FILE}")


if __name__ == "__main__":
    main()