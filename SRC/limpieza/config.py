"""
Configuración de rutas y parámetros de exportación.
"""
from pathlib import Path

# Directorios
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "Data"

# Entradas
ALCAMPO_JSON = DATA_DIR / "resultado_alcampo.json"
OPENFOOD_JSON = DATA_DIR / "openfood_facts_productos.json"

# Salidas
OUTPUT_JSON_UNIFIED = DATA_DIR / "productos_unificados.json"
OUTPUT_CSV_PATH = DATA_DIR / "clean" / "productos_unificados.csv"  # CSV básico desanidado

# Exportación
ENCODING = "utf-8"
CSV_SEPARATOR = ","
