"""
Paquete de limpieza para datos nutricionales.
Incluye carga, consolidación, y preparación de datos para ML.
"""

__version__ = '2.1.0'
__author__ = 'Proyecto Chatbots'

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Importaciones públicas
from .config import OUTPUT_CSV_PATH, ALCAMPO_JSON, OPENFOOD_JSON

__all__ = [
    'OUTPUT_CSV_PATH',
    'ALCAMPO_JSON',
    'OPENFOOD_JSON',
]
