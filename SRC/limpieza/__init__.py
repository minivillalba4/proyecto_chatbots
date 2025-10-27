"""
Paquete de limpieza para datos nutricionales.
Incluye carga, consolidación, y preparación de datos para ML.

Arquitectura refactorizada v3.0:
- constants.py: Constantes y esquemas del proyecto
- config.py: Configuración de rutas (editable por usuario)
- data_loaders.py: Carga y guardado de archivos
- nutrition_parsers.py: Parseo de valores nutricionales
- field_extractors.py: Extracción de campos específicos
- validators.py: Validación de productos
- transformers.py: Transformación por fuente (Alcampo, OpenFoodFacts)
- dataframe_builder.py: Construcción de DataFrames tabulares
- feature_engineering.py: Features para Machine Learning
- main.py: Orquestación del pipeline
"""

__version__ = '3.0.0'
__author__ = 'Proyecto Chatbots'

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Importaciones públicas - Configuración
from .config import (
    OUTPUT_CSV_PATH,
    OUTPUT_JSON_UNIFIED,
    ALCAMPO_JSON,
    OPENFOOD_JSON,
    ENCODING
)

# Importaciones públicas - Constantes
from .constants import (
    REQUIRED_FIELDS,
    OPTIONAL_FIELDS,
    NUTRITION_KEYS_STANDARD,
    NUTRITION_COLS
)

# Importaciones públicas - Funciones principales
from .data_loaders import load_json_file, save_json_file
from .nutrition_parsers import standardize_nutrition, clean_numeric_value
from .validators import validate_unified_product, create_base_product
from .transformers import (
    transform_alcampo_product,
    transform_openfood_product,
    unify_products_from_sources
)
from .dataframe_builder import flatten_to_dataframe

__all__ = [
    # Configuración
    'OUTPUT_CSV_PATH',
    'OUTPUT_JSON_UNIFIED',
    'ALCAMPO_JSON',
    'OPENFOOD_JSON',
    'ENCODING',
    # Constantes
    'REQUIRED_FIELDS',
    'OPTIONAL_FIELDS',
    'NUTRITION_KEYS_STANDARD',
    'NUTRITION_COLS',
    # Data Loaders
    'load_json_file',
    'save_json_file',
    # Parsers
    'standardize_nutrition',
    'clean_numeric_value',
    # Validators
    'validate_unified_product',
    'create_base_product',
    # Transformers
    'transform_alcampo_product',
    'transform_openfood_product',
    'unify_products_from_sources',
    # DataFrame Builder
    'flatten_to_dataframe',
]
