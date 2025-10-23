import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By

# Añadir la ruta de SRC al path para importar utils
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from utils import save_json

# Importar configuración y logger
import config
# --- NEW IMPORT: constants module to hold selectors ---
import constants

def extract_product_info(element, base_url, css_title):
	"""Extrae nombre y URL desde un elemento tipo <a> de producto de forma robusta."""
	url = element.get_attribute('href')
	if url and url.startswith('/'):
		url = base_url.rstrip('/') + url

	nombre = "Nombre no encontrado"
	try:
		title_el = element.find_element(By.CSS_SELECTOR, css_title)
		if getattr(title_el, 'text', '').strip():
			nombre = title_el.text.strip()
	except Exception:
		txt = getattr(element, 'text', '') or ''
		if txt.strip():
			nombre = txt.strip()
		else:
			nombre = "Nombre no encontrado (Fallback)"
	return {"nombre": nombre, "url": url}

def run_scraper():
    """Función principal que ejecuta el proceso de scraping."""
    productos = []
    productos_ya_extraidos = set()
    
    config.logger.info(f"Iniciando Web Scraper de Alcampo. Objetivo: {config.LIMITE_PRODUCTOS} productos.")
    
    try:
        driver = webdriver.Chrome()
    except Exception as e:
        config.logger.error(f"Error al inicializar el WebDriver: {e}")
        return 1

    driver.get(config.URL_ALCAMPO)
    time.sleep(4)

    config.logger.info("Iniciando scroll y guardado dinámico...")
    altura_anterior = driver.execute_script("return document.body.scrollHeight")
    scroll_count = 0
    ultimo_guardado = 0

    while len(productos) < config.LIMITE_PRODUCTOS and scroll_count < config.MAX_SCROLLS:
        scroll_count += 1
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(config.SCROLL_PAUSE_TIME)
        
        try:
            elementos_enlace = driver.find_elements(By.CSS_SELECTOR, constants.CSS_PRODUCTO_LINK)
        except Exception as e:
            config.logger.error(f"Error al buscar elementos con CSS_SELECTOR: {e}")
            elementos_enlace = []

        productos_encontrados_ahora = 0
        for elemento in elementos_enlace:
            if len(productos) >= config.LIMITE_PRODUCTOS:
                break

            info = extract_product_info(elemento, config.BASE_URL, constants.CSS_PRODUCTO_TITULO)
            url_completa = info.get("url")
            
            if url_completa and url_completa not in productos_ya_extraidos:
                nuevo_id = len(productos) + 1
                productos.append({
                    "id": nuevo_id,
                    "nombre": info.get("nombre", "Nombre no encontrado"),
                    "url_productos_alcampo": url_completa
                })
                productos_ya_extraidos.add(url_completa)
                productos_encontrados_ahora += 1
        
        config.logger.info(f"Scroll #{scroll_count}: {productos_encontrados_ahora} nuevos. Total: {len(productos)}")

        if len(productos) >= ultimo_guardado + config.PRODUCTOS_POR_GUARDADO:
            try:
                save_json(productos, config.NOMBRE_ARCHIVO_JSON, indent=4)
                config.logger.info(f"Guardado intermedio con {len(productos)} productos.")
                ultimo_guardado = len(productos)
            except Exception as e:
                config.logger.error(f"Ocurrió un error al escribir el archivo JSON: {e}")
        
        altura_nueva = driver.execute_script("return document.body.scrollHeight")
        if altura_nueva == altura_anterior:
            config.logger.info("Final de la página alcanzado.")
            break
        altura_anterior = altura_nueva

    # Guardado final
    if len(productos) > ultimo_guardado:
        try:
            save_json(productos, config.NOMBRE_ARCHIVO_JSON, indent=4)
        except Exception as e:
            config.logger.error(f"Ocurrió un error al escribir el archivo JSON: {e}")
    
    config.logger.info(f"Proceso FINALIZADO. Productos extraídos: {len(productos)}.")
    driver.quit()
    return 0
