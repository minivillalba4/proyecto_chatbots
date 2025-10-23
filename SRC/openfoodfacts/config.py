import os

# HTTP config
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
}
REQUEST_TIMEOUT = 30

# Crawling config
LISTING_BASE_URL = "https://es.openfoodfacts.org/"
TARGET_COUNT = 525  # Cambia la cantidad de productos que se parsean por página
MAX_PAGES = 10000
PRODUCT_DELAY_SECONDS = 1.25
ERROR_DELAY_SECONDS = 1.5

# Output config
# guardar en la carpeta Data del proyecto (main.py compone la ruta desde el root)
OUTPUT_DIR_REL = "Data"
OUTPUT_FILENAME = "openfood_facts_productos.json"
