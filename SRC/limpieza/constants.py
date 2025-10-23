"""
Constantes estáticas para el procesamiento de datos nutricionales.
"""

# Esquema nutricional unificado
NUTRITION_COLS = [
    "energia_kcal",
    "energia_kj",
    "grasas_totales",
    "grasas_saturadas",
    "carbohidratos",
    "azucares",
    "proteinas",
    "sal",
    "fibra",
]

# Mapeo para consolidación
NUTRITION_MAPPING = {
    "energia_kcal": ["energia_kcal"],
    "energia_kj": ["energia_kj"],
    "grasas_totales": ["grasas_totales"],
    "grasas_saturadas": ["grasas_saturadas"],
    "carbohidratos": ["carbohidratos"],
    "azucares": ["azucares"],
    "proteinas": ["proteinas"],
    "sal": ["sal"],
    "fibra": ["fibra"],
}

# Número mínimo de columnas nutricionales para ML
MIN_NUTRITION_COLS = 3
