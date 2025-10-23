import time
import requests
from typing import Dict, List
import os
import sys

# Añadir la ruta de SRC al path para importar utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import save_json, path_join_safe

import config
from url_collector import collect_product_urls
from product_parser import parse_product_html

def save_products_json(products: List[Dict], output_dir_rel: str, filename: str) -> str:
	# Construye la ruta como hacía storage.save_products_json, reutilizando utils
	project_root = path_join_safe(os.path.dirname(__file__), "..", "..")
	out_path = path_join_safe(project_root, output_dir_rel, filename)
	save_json(products, out_path, indent=2)
	return out_path

def run() -> None:
    print("Iniciando scraper de OpenFoodFacts (modular).")

    urls = collect_product_urls(
        base_url=config.LISTING_BASE_URL,
        target_count=config.TARGET_COUNT,
        headers=config.HEADERS,
        timeout=config.REQUEST_TIMEOUT,
        max_pages=config.MAX_PAGES,
    )

    print(f"\nDescargando productos con espera de {config.PRODUCT_DELAY_SECONDS:.1f}s entre cada uno...")
    productos_guardar: List[Dict] = []

    for idx, prod_url in enumerate(urls, start=1):
        print(f"\nProducto {idx}/{len(urls)}: {prod_url}")
        try:
            rp = requests.get(prod_url, headers=config.HEADERS, timeout=config.REQUEST_TIMEOUT)
            print("  Estado:", rp.status_code, "Tamaño:", len(rp.text))
        except Exception as e:
            print("  Error al descargar producto:", e)
            time.sleep(config.ERROR_DELAY_SECONDS)
            continue

        data = parse_product_html(rp.text)
        print("  Título:", data.get("titulo"))
        print("  Nutrición (cruda de tabla):", data.get("valores_nutricionales_100_g") or "no detectada")

        producto_simple = {
            "URL": prod_url,
            **data,
        }

        # --- Nuevo: filtrar productos que no tengan las 3 claves necesarias ---
        required_keys = ("URL", "titulo", "valores_nutricionales_100_g")
        missing = [k for k in required_keys if not producto_simple.get(k)]
        if missing:
            print(f"  Producto descartado: faltan campos requeridos: {', '.join(missing)}")
            # no añadimos el producto a la lista
        else:
            productos_guardar.append(producto_simple)

        time.sleep(config.PRODUCT_DELAY_SECONDS)

    print("\nHecho. Productos procesados:", len(urls))
    
    # Guardar usando el helper unificado
    try:
        path = save_products_json(
            productos_guardar,
            output_dir_rel=config.OUTPUT_DIR_REL,
            filename=config.OUTPUT_FILENAME,
        )
        print(f" Guardado JSON: {path} ( {len(productos_guardar)} items)")
    except Exception as e:
        print(f"Error al guardar el archivo JSON: {e}")

if __name__ == "__main__":
    run()
