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
STORIES_FILE = BASE_DIR / "data" / "stories.json"

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
with open(STORIES_FILE, "r", encoding="utf-8") as file:
    stories = json.load(file)

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

        # Only compare actual parent IDs
        same_father = (
            bool(father_id)
            and other_person.get("father") == father_id
        )

        same_mother = (
            bool(mother_id)
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
        key=lambda source: source.get("date") or "9999"
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
gallery_template = environment.get_template("photos.html")
documents_template = environment.get_template("documents.html")
stories_template = environment.get_template("stories.html")
story_template = environment.get_template("story.html")

# --------------------------------------------------
# Create output folders
# --------------------------------------------------

OUTPUT_DIR.mkdir(exist_ok=True)
PEOPLE_DIR.mkdir(exist_ok=True)

# --------------------------------------------------
# Sort people alphabetically by last name
# --------------------------------------------------

def sort_people_by_name(people_list):
    return sorted(
        people_list,
        key=lambda person: (
            (person.get("last_name") or "").strip().casefold(),
            (person.get("first_name") or "").strip().casefold(),
            person.get("birth_year") if person.get("birth_year") is not None else 9999
        )
    )


# --------------------------------------------------
# Organize people by family line
# --------------------------------------------------

# Sort all family members alphabetically
all_people_sorted = sort_people_by_name(people)

# Herrin family
herrin_people = sort_people_by_name([
    person for person in people
    if "herrin" in person.get("family_lines", [])
])

# Singletary family
singletary_people = sort_people_by_name([
    person for person in people
    if "singletary" in person.get("family_lines", [])
])


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
        "people": all_people_sorted,
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
# Generate Family Photo Gallery
# --------------------------------------------------

gallery_photos = []

for photo in photos:
    gallery_photo = photo.copy()

    # Identify people associated with the photograph
    photo_people = [
        people_by_id[person_id]
        for person_id in photo.get("people", [])
        if person_id in people_by_id
    ]

    gallery_photo["people_details"] = photo_people

    # Determine which family lines the photo belongs to
    family_lines = set()

    for person in photo_people:
        family_lines.update(person.get("family_lines", []))

    gallery_photo["family_lines"] = sorted(family_lines)

    gallery_photos.append(gallery_photo)


# --------------------------------------------------
# Sort gallery photographs
# Regular photographs first, gravestones last
# --------------------------------------------------

gallery_photos.sort(
    key=lambda photo: (
        photo.get("type") == "grave",
        (photo.get("title") or "").casefold()
    )
)


# Render the gallery page
html = gallery_template.render(
    gallery_photos=gallery_photos
)

gallery_file = OUTPUT_DIR / "photos.html"

with open(gallery_file, "w", encoding="utf-8") as file:
    file.write(html)


# --------------------------------------------------
# Generate Historical Documents Page
# --------------------------------------------------

document_sources = []

for source in sources:

    # Only include records with attached document files
    if not source.get("documents"):
        continue

    document_source = source.copy()

    # Find family members associated with this source
    source_people = [
        people_by_id[person_id]
        for person_id in source.get("people", [])
        if person_id in people_by_id
    ]

    document_source["people_details"] = source_people

    document_source["people_names"] = [
        person["display_name"]
        for person in source_people
    ]

    document_sources.append(document_source)


# Sort documents by date, then title
document_sources.sort(
    key=lambda source: (
        source.get("date") or "9999",
        (source.get("title") or "").casefold()
    )
)



# Standardize document categories for filtering

def get_document_category(source_type):
    value = (source_type or "").strip().lower()
    value = value.replace("_", " ").replace("-", " ")

    if "census" in value:
        return "Census"
    elif "birth" in value or "stillbirth" in value:
        return "Birth Records"
    elif "death" in value or "cemetery" in value:
        return "Death & Burial"
    elif "marriage" in value:
        return "Marriage Records"
    elif "draft" in value or "military" in value:
        return "Military Records"
    elif "obituary" in value or "newspaper" in value:
        return "Newspapers & Obituaries"
    elif "city directory" in value:
        return "City Directories"
    elif "land" in value:
        return "Land Records"
    elif "pension" in value:
        return "Pension Records"
    elif "voter" in value:
        return "Voter Registration"
    elif "published" in value:
        return "Published Histories"

    return "Other Records"


for source in document_sources:
    source["category"] = get_document_category(
        source.get("type")
    )


document_types = sorted({
    source["category"]
    for source in document_sources
})



# Render the Documents page
html = documents_template.render(
    document_sources=document_sources,
    document_types=document_types
)

documents_file = OUTPUT_DIR / "documents.html"

with open(documents_file, "w", encoding="utf-8") as file:
    file.write(html)


# --------------------------------------------------
# Generate Family Stories Page
# --------------------------------------------------

# Only show stories that are ready for publication
published_stories = [
    story for story in stories
    if story.get("status", "").lower() == "published"
]

# Sort published stories alphabetically by title
published_stories.sort(
    key=lambda story: story.get("title", "").casefold()
)

# Generate the Stories landing page
html = stories_template.render(
    stories=published_stories
)

stories_file = OUTPUT_DIR / "stories.html"

with open(stories_file, "w", encoding="utf-8") as file:
    file.write(html)


# --------------------------------------------------
# Generate Individual Story Pages
# --------------------------------------------------

# Create the folder for individual stories
STORIES_OUTPUT_DIR = OUTPUT_DIR / "stories"

# Remove previously generated story pages
if STORIES_OUTPUT_DIR.exists():
    shutil.rmtree(STORIES_OUTPUT_DIR)

# Recreate the folder for published stories
STORIES_OUTPUT_DIR.mkdir(exist_ok=True)

# Generate a page for each published story
for story in published_stories:

    # Identify family members associated with the story
    story_people = [
        people_by_id[person_id]
        for person_id in story.get("people", [])
        if person_id in people_by_id
    ]

    # Create a copy so we don't modify stories.json data
    story_data = story.copy()
    story_data["people_details"] = story_people

    # Render the individual story
    html = story_template.render(
        story=story_data
    )

    # Save the HTML file
    story_file = STORIES_OUTPUT_DIR / f"{story['id']}.html"

    with open(story_file, "w", encoding="utf-8") as file:
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
