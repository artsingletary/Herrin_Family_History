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
