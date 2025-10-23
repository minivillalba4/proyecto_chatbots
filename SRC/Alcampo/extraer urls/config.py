import logging
import os

# --- CONFIGURACIÓN DE LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# --- VARIABLES CONFIGURABLES ---
URL_ALCAMPO = "https://www.compraonline.alcampo.es/categories?source=navigation"
BASE_URL = "https://www.compraonline.alcampo.es"
SCROLL_PAUSE_TIME = 7
LIMITE_PRODUCTOS = 750
PRODUCTOS_POR_GUARDADO = 20
MAX_SCROLLS = 500

# --- Rutas ancladas al root del proyecto ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
NOMBRE_ARCHIVO_JSON = os.path.join(PROJECT_ROOT, "Data", "productos_alcampo.json")
