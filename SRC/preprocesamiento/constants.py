"""
Constantes del módulo de preprocesamiento.
"""

# Parámetros de limpieza
MIN_REQUIRED_NUTRIENTS = 2  # Mínimo de valores nutricionales no nulos requeridos
MISSING_DATA_THRESHOLD = 0.8  # Si un campo tiene >80% nulos, se considera para eliminación
OUTLIER_STD_THRESHOLD = 3  # Desviaciones estándar para detección de outliers

# Campos obligatorios en el CSV
REQUIRED_FIELDS = ["url", "product_name"]

# Campos nutricionales en el CSV (nombres reales de las columnas)
NUTRITIONAL_FIELDS = [
    "energia_kcal",
    "energia_kj",
    "grasas_totales",
    "grasas_saturadas",
    "carbohidratos",
    "azucares",
    "proteinas",
    "sal",
    "fibra"
]

# Rangos válidos para valores nutricionales (por 100g)
# Estos rangos son realistas para alimentos procesados
NUTRITIONAL_RANGES = {
    "energia_kcal": (0, 900),      # Calorías por 100g
    "energia_kj": (0, 3800),       # Kilojulios por 100g
    "grasas_totales": (0, 100),    # Grasas totales en g
    "grasas_saturadas": (0, 100),  # Grasas saturadas en g
    "carbohidratos": (0, 100),     # Carbohidratos en g
    "azucares": (0, 100),          # Azúcares en g
    "proteinas": (0, 100),         # Proteínas en g
    "sal": (0, 50),                # Sal en g
    "fibra": (0, 100)              # Fibra en g
}

# Campos de texto para normalización
TEXT_FIELDS = [
    "product_name",
    "descripcion",
    "country",
    "marcas",
    "tiendas",
    "nombre_operador"
]

# Campos que deben ser numéricos
NUMERIC_FIELDS = [
    "precio_total",
    "precio_por_cantidad",
    "weight_volume_clean",
    "numero_raciones"
] + NUTRITIONAL_FIELDS

# Unidades de peso/volumen válidas
VALID_WEIGHT_UNITS = ["g", "kg", "mg"]
VALID_VOLUME_UNITS = ["ml", "l", "cl", "dl"]
VALID_UNITS = VALID_WEIGHT_UNITS + VALID_VOLUME_UNITS

# Factores de conversión a unidades base (g y ml)
CONVERSION_FACTORS = {
    # Peso (a gramos)
    "g": 1.0,
    "kg": 1000.0,
    "mg": 0.001,
    # Volumen (a mililitros)
    "ml": 1.0,
    "l": 1000.0,
    "cl": 10.0,
    "dl": 100.0
}

# Umbrales para indicadores de salud
THRESHOLD_HIGH_SALT = 1.5        # g por 100g
THRESHOLD_HIGH_SUGAR = 15.0      # g por 100g
THRESHOLD_HIGH_FAT = 17.5        # g por 100g
THRESHOLD_HIGH_SATURATED = 5.0   # g por 100g

# Categorización calórica (kcal por 100g)
CALORIE_CATEGORIES = {
    "bajo": (0, 100),
    "medio": (100, 300),
    "alto": (300, 500),
    "muy_alto": (500, float('inf'))
}

# Factor de conversión energía (1 kcal ≈ 4.184 kJ)
KCAL_TO_KJ_FACTOR = 4.184
ENERGY_TOLERANCE = 0.10  # Tolerancia del 10% en la conversión energética

# ============================================================
# CONSTANTES PARA NORMALIZACIÓN DE TEXTO NLP
# ============================================================

# Campos de texto para normalizar
TEXT_FIELDS_TO_NORMALIZE = [
    "product_name",
    "descripcion",
    "categorias",
    "marcas",
    "tiendas",
    "alergenos",
    "certificaciones",
    "nombre_operador",
    "country"
]

# Campos que tendrán versión normalizada
TEXT_NORMALIZED_SUFFIX = "_normalized"

# Caracteres especiales a eliminar (mantener acentos para español)
SPECIAL_CHARS_TO_REMOVE = r'[^\w\sáéíóúüñÁÉÍÓÚÜÑ]'

# Patrones de texto a limpiar
PATTERNS_TO_CLEAN = {
    r'\s+': ' ',           # Múltiples espacios a uno solo
    r'^\s+|\s+$': '',      # Espacios al inicio/final
    r'\d+\s*(g|kg|ml|l|mg|cl|dl|u|uds?|unidades?)\b': '',  # Cantidades con unidades
    r'\b\d+x\d+\b': '',    # Formato "2x100"
    r'\b\d+\s*%': '',      # Porcentajes
}

# Stopwords adicionales del dominio alimentario (además de las de NLTK)
DOMAIN_STOPWORDS = {
    # Términos genéricos
    'producto', 'productos', 'pack', 'unidad', 'unidades', 'lata', 'bote', 'envase',
    'paquete', 'caja', 'bolsa', 'uds', 'ud',
    # Marcas genéricas de supermercados
    'alcampo', 'auchan',
    # Términos de tamaño/cantidad (ya están en patrones pero refuerzo)
    'gramos', 'litros', 'mililitros', 'kilogramos',
}

# Configuración de tokenización
MIN_TOKEN_LENGTH = 2  # Longitud mínima de tokens a conservar
MAX_TOKEN_LENGTH = 50  # Longitud máxima de tokens válidos

# Configuración de stemming/lemmatización
USE_STEMMING = True  # Usar stemming en lugar de lematización (más rápido)
STEMMER_LANGUAGE = "spanish"

# Campos que requieren procesamiento especial
CATEGORICAL_TEXT_FIELDS = ["categorias", "alergenos", "certificaciones"]
SEPARATOR_FOR_CATEGORIES = ","  # Separador usado en listas
