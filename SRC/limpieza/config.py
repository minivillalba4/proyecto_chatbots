"""
Configuración de rutas y parámetros de exportación.
"""
from pathlib import Path

# Directorios
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "Data"

# Entradas y salida
ALCAMPO_JSON = DATA_DIR / "resultado_alcampo.json"
OPENFOOD_JSON = DATA_DIR / "openfood_facts_productos.json"
OUTPUT_CSV_PATH = DATA_DIR / "productos_unificados.csv"

# Exportación
ENCODING = "utf-8"
CSV_SEPARATOR = ","
