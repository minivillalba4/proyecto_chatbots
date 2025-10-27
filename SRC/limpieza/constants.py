"""
Constantes del módulo de limpieza de datos nutricionales.
Define esquemas, mapeos y valores por defecto.
"""

# ============================================================================
# ESQUEMA DE PRODUCTO UNIFICADO
# ============================================================================

REQUIRED_FIELDS = ['url', 'titulo', 'valores_nutricionales_100_g']

OPTIONAL_FIELDS = [
    'descripcion',
    'categorias',
    'precio_total',
    'precio_por_cantidad',
    'peso_volumen',
    'alergenos',
    'origen',
    'direccion_manufactura',
    'marcas',
    'tiendas',
    'certificaciones',
    'numero_raciones',
    'nombre_operador'
]

# ============================================================================
# VALORES NUTRICIONALES ESTÁNDAR
# ============================================================================

NUTRITION_KEYS_STANDARD = [
    'energia_kj',
    'energia_kcal',
    'grasas_g',
    'grasas_saturadas_g',
    'hidratos_g',
    'azucares_g',
    'fibra_g',
    'proteinas_g',
    'sal_g'
]

# Mapeo de campos nutricionales: Alcampo → Estándar
ALCAMPO_NUTRITION_MAP = {
    'valor_energetico_kj': 'energia_kj',
    'valor_energetico_kcal': 'energia_kcal',
    'grasas_g': 'grasas_g',
    'grasas_saturadas_g': 'grasas_saturadas_g',
    'hidratos_g': 'hidratos_g',
    'azucares_g': 'azucares_g',
    'proteinas_g': 'proteinas_g',
    'sal_g': 'sal_g'
}

# Mapeo de campos nutricionales: OpenFoodFacts → Estándar
OPENFOOD_NUTRITION_MAP = {
    'grasas': 'grasas_g',
    'grasas_saturadas': 'grasas_saturadas_g',
    'hidratos': 'hidratos_g',
    'azucares': 'azucares_g',
    'fibra': 'fibra_g',
    'proteinas': 'proteinas_g',
    'sal': 'sal_g'
}

# ============================================================================
# COLUMNAS PARA MACHINE LEARNING
# ============================================================================

NUTRITION_COLS = [
    'energia_kcal',
    'energia_kj',
    'grasas_totales',
    'grasas_saturadas',
    'carbohidratos',
    'azucares',
    'proteinas',
    'sal',
    'fibra'
]

MIN_NUTRITION_COLS = 3

# ============================================================================
# UNIDADES Y TOKENS PARA LIMPIEZA NUMÉRICA
# ============================================================================

NUMERIC_CLEAN_TOKENS = [
    'kcal', 'kj', 'cal', 'g', 'mg', 'kg', 'l', 'ml', 'cl', '€', '%', 'x'
]

# ============================================================================
# VALORES POR DEFECTO
# ============================================================================

DEFAULT_NUTRITION = {key: None for key in NUTRITION_KEYS_STANDARD}
