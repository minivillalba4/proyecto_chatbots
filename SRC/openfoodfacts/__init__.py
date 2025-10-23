# Paquete openfoodfacts: exportaciones públicas y compatibilidad tras eliminar storage.py

from .main import run, save_products_json  # type: ignore
from .url_collector import collect_product_urls  # opcional: expuesto por conveniencia
from .product_parser import parse_product_html   # opcional: expuesto por conveniencia

__all__ = ["run", "save_products_json", "collect_product_urls", "parse_product_html"]
__version__ = "0.1.0"
