import json
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


# --------------------------------------------------
# File locations
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "people.json"
SOURCES_FILE = BASE_DIR / "data" / "sources.json"
PHOTOS_FILE = BASE_DIR/ "data"/ "photos.json"

TEMPLATE_DIR = BASE_DIR / "templates"
# Create output folders
OUTPUT_DIR = BASE_DIR / "docs"
PEOPLE_DIR = OUTPUT_DIR / "people"
# Copy static files such as CSS and JavaScript
STATIC_DIR = BASE_DIR / "static"
OUTPUT_STATIC_DIR = OUTPUT_DIR / "static"

if OUTPUT_STATIC_DIR.exists():
    shutil.rmtree(OUTPUT_STATIC_DIR)

shutil.copytree(STATIC_DIR, OUTPUT_STATIC_DIR)

# Copy family photographs
PHOTOS_DIR = BASE_DIR / "photos"
OUTPUT_PHOTOS_DIR = OUTPUT_DIR / "photos"

if OUTPUT_PHOTOS_DIR.exists():
    shutil.rmtree(OUTPUT_PHOTOS_DIR)

shutil.copytree(PHOTOS_DIR, OUTPUT_PHOTOS_DIR)

# Copy historical documents
DOCUMENTS_DIR = BASE_DIR / "documents"
OUTPUT_DOCUMENTS_DIR = OUTPUT_DIR / "documents"

if OUTPUT_DOCUMENTS_DIR.exists():
    shutil.rmtree(OUTPUT_DOCUMENTS_DIR)

shutil.copytree(DOCUMENTS_DIR, OUTPUT_DOCUMENTS_DIR)

# --------------------------------------------------
# Load family data
# --------------------------------------------------

with open(DATA_FILE, "r", encoding="utf-8") as file:
    people = json.load(file)
with open(SOURCES_FILE, "r", encoding="utf-8") as file:
    sources = json.load(file)
with open(PHOTOS_FILE, encoding="utf-8") as file:
    photos = json.load(file)

# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def get_full_name(person):
    first = person["first_name"]
    middle = person.get("middle_name")
    nickname = person.get("nickname")
    last = person["last_name"]
    suffix = person.get("suffix")

    name_parts = [first]

    if middle:
        name_parts.append(middle)

    if nickname:
        name_parts.append(f'"{nickname}"')

    name_parts.append(last)

    name = " ".join(name_parts)

    if suffix:
        name += f" {suffix}"

    return name


def get_years(person):
    birth = person.get("birth_year")
    death = person.get("death_year")
    death_before = person.get("death_before")

    if birth and death:
        return f"{birth}–{death}"

    if birth:
        return f"Born {birth}"

    if death_before:
        return f"Died before {death_before}"

    return ""


def get_children(person_id):
    children = []

    for person in people:
        if (
            person.get("father") == person_id
            or person.get("mother") == person_id
        ):
            children.append(person)

    return children


def get_siblings(person):
    siblings = []

    father_id = person.get("father")
    mother_id = person.get("mother")

    for other_person in people:

        # Don't include the person themself
        if other_person["id"] == person["id"]:
            continue

        same_father = (
            father_id is not None
            and other_person.get("father") == father_id
        )

        same_mother = (
            mother_id is not None
            and other_person.get("mother") == mother_id
        )

        if same_father or same_mother:
            siblings.append(other_person)

    return siblings


def get_sources(person_id):
    person_sources = []

    for source in sources:
        if person_id in source.get("people", []):
            person_sources.append(source)

    person_sources.sort(
        key=lambda source: source.get("date", "9999")
    )

    return person_sources


def get_photos(person_id):
    person_photos = []

    for photo in photos:
        if (
            person_id in photo.get("people", [])
            and photo.get("type") != "grave"
        ):
            person_photos.append(photo)

    return person_photos


def get_grave_photos(person_id):
    grave_photos = []

    for photo in photos:
        if (
            person_id in photo.get("people", [])
            and photo.get("type") == "grave"
        ):
            grave_photos.append(photo)

    return grave_photos


def format_date(date_string):

    if not date_string:
        return None

    year, month, day = date_string.split("-")

    months = {
        "01": "January",
        "02": "February",
        "03": "March",
        "04": "April",
        "05": "May",
        "06": "June",
        "07": "July",
        "08": "August",
        "09": "September",
        "10": "October",
        "11": "November",
        "12": "December"
    }

    month_name = months[month]

    return f"{month_name} {int(day)}, {year}"

# --------------------------------------------------
# Prepare family data
# --------------------------------------------------

people_by_id = {}

for person in people:
    person["display_name"] = get_full_name(person)
    person["years"] = get_years(person)

    person["display_birth_date"] = format_date(person.get("birth_date"))
    person["display_death_date"] = format_date(person.get("death_date"))

    people_by_id[person["id"]] = person


# --------------------------------------------------
# Set up Jinja templates
# --------------------------------------------------

environment = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR)
)

environment.filters["format_date"] = format_date

index_template = environment.get_template("index.html")
person_template = environment.get_template("person.html")
family_template = environment.get_template("family.html")


# --------------------------------------------------
# Create output folders
# --------------------------------------------------

OUTPUT_DIR.mkdir(exist_ok=True)
PEOPLE_DIR.mkdir(exist_ok=True)


# --------------------------------------------------
# Organize people by family line
# --------------------------------------------------

herrin_people = [
    person for person in people
    if "herrin" in person.get("family_lines", [])
]

singletary_people = [
    person for person in people
    if "singletary" in person.get("family_lines", [])
]


# --------------------------------------------------
# Generate index.html
# --------------------------------------------------

html = index_template.render(
    people=people,
    herrin_people=herrin_people,
    singletary_people=singletary_people
)

index_file = OUTPUT_DIR / "index.html"

with open(index_file, "w", encoding="utf-8") as file:
    file.write(html)


# --------------------------------------------------
# Generate family pages
# --------------------------------------------------

family_pages = [
    {
        "family_name": "Herrin",
        "people": herrin_people,
        "filename": "herrin-family.html"
    },
    {
        "family_name": "Singletary",
        "people": singletary_people,
        "filename": "singletary-family.html"
    },
    {
        "family_name": "All",
        "people": people,
        "filename": "all-family.html"
    }
]


for family in family_pages:

    html = family_template.render(
        family_name=family["family_name"],
        family_people=family["people"]
    )

    family_file = OUTPUT_DIR / family["filename"]

    with open(family_file, "w", encoding="utf-8") as file:
        file.write(html)

# --------------------------------------------------
# Generate individual person pages
# --------------------------------------------------

for person in people:

    # Find father
    father = None

    father_id = person.get("father")

    if father_id:
        father = people_by_id.get(father_id)


    # Find mother
    mother = None

    mother_id = person.get("mother")

    if mother_id:
        mother = people_by_id.get(mother_id)


    # Find spouse or spouses
    spouses = []

    for spouse_id in person.get("spouses", []):
        spouse = people_by_id.get(spouse_id)

        if spouse:
            spouses.append(spouse)


    # Find children
    children = get_children(person["id"])
    person_sources = get_sources(person["id"])
    siblings = get_siblings(person)
    person_photos = get_photos(person["id"])
    grave_photos = get_grave_photos(person["id"])

    # Send all of this information to person.html
    html = person_template.render(
        person=person,
        father=father,
        mother=mother,
        spouses=spouses,
        children=children,
        siblings=siblings,
        sources=person_sources,
        photos=person_photos,
        grave_photos=grave_photos,
    )


    # Create the person's HTML file
    output_file = PEOPLE_DIR / f"{person['id']}.html"

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(html)


# --------------------------------------------------
# Finished
# --------------------------------------------------

print()
print("HERRIN FAMILY HISTORY")
print("=====================")
print()
print("Website created successfully.")
print(f"Home page: {index_file}")
print(f"Person pages created: {len(people)}")
