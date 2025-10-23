import re

# URL discovery
PRODUCT_URL_REGEX = re.compile(
    r'https?://(?:es|world-es)\.openfoodfacts\.org/producto/[\w\-\./%]+',
    flags=re.I,
)

# Parsing constants
NUTRITION_TABLE_ARIA_LABEL = "Información nutricional"
TITLE_SELECTORS = ("h2.title-1", "h1")
QUANTITY_SELECTOR = "span#field_quantity_value"

# Nutrition label matching (ordered by priority)
NUTRITION_LABEL_MAP = (
    ("energ", "energia"),
    ("saturad", "grasas_saturadas"),
    ("grasa", "grasas"),
    ("hidratos", "hidratos"),
    ("carbo", "hidratos"),
    ("azuc", "azucares"),
    ("prote", "proteinas"),
    ("fibra", "fibra"),
    ("sal", "sal"),
)

# Units normalization
UNIT_MAP = {
    # weight
    "g": ("g", 1.0),
    "gr": ("g", 1.0),
    "gramo": ("g", 1.0),
    "gramos": ("g", 1.0),
    "kg": ("g", 1000.0),
    "kilo": ("g", 1000.0),
    "kilos": ("g", 1000.0),
    "kilogramo": ("g", 1000.0),
    "kilogramos": ("g", 1000.0),
    # volume
    "ml": ("ml", 1.0),
    "mililitro": ("ml", 1.0),
    "mililitros": ("ml", 1.0),
    "l": ("ml", 1000.0),
    "lt": ("ml", 1000.0),
    "litro": ("ml", 1000.0),
    "litros": ("ml", 1000.0),
}

# Description field selectors and keys
DESCRIPTION_SELECTORS = (
    ("denominación general", "p#field_generic_name span.field_value"),
    ("cantidad", "p#field_quantity"),
    ("envase", "p#field_packaging"),
    ("marcas", "p#field_brands"),
    ("categorias", "p#field_categories"),
    ("sellos, certificados de calidad, premios", "p#field_labels"),
    ("lugares de fabricación o de transformación", "p#field_manufacturing_places"),
    ("código de trazabilidad", "p#field_emb_codes"),
    ("tiendas", "p#field_stores"),
    ("países de venta", "p#field_countries"),
)

# Allergens
ALLERGENS_LABEL_REGEX = re.compile(r"Al[eé]rgenos\s*:\s*([^\n\r]+)", flags=re.I)
ALLERGENS_SPLIT_REGEX = re.compile(r",|;|•|\s+y\s+", flags=re.I)
INGREDIENTS_PANEL_SELECTOR = "div#panel_ingredients_content div.panel_text"
MAIN_CONTENT_SELECTOR = "div.medium-8.small-12.columns"
