"""
Configuración de rutas del módulo de preprocesamiento.
"""

from pathlib import Path

# Rutas base
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "Data"
CLEAN_DIR = DATA_DIR / "clean"
SRC_DIR = BASE_DIR / "SRC"

# Rutas de archivos de entrada (CSV ya desanidado)
INPUT_CSV = CLEAN_DIR / "productos_unificados.csv"

# Rutas de archivos de salida
OUTPUT_CSV = CLEAN_DIR / "productos_unificados_clean.csv"

# Archivos de logs
LOG_FILE = CLEAN_DIR / "preprocessing.log"

# Configuración de exportación
ENCODING = "utf-8-sig"  # UTF-8 con BOM para compatibilidad con Excel
CSV_SEPARATOR = ","

# Asegurar que los directorios existen
CLEAN_DIR.mkdir(parents=True, exist_ok=True)
