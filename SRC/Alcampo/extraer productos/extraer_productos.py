import re
import time
import requests
import logging
import os
import sys
from typing import List, Dict
from bs4 import BeautifulSoup
import config
import constants

# permitir importar utils desde SRC
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from utils import save_json, path_join_safe

logger = logging.getLogger(__name__)

# intervalo de guardado incremental (puedes cambiarlo en config si lo prefieres)
SAVE_INTERVAL = 25

def normalize_text(s: str) -> str:
	return None if s is None else s.replace('\xa0', ' ').strip()

def _prune_nones(obj):
	# Elimina claves con None de forma recursiva
	if isinstance(obj, dict):
		clean = {}
		for k, v in obj.items():
			if isinstance(v, dict):
				p = _prune_nones(v)
				if p:  # solo si el dict no queda vacío
					clean[k] = p
			elif v is not None:
				clean[k] = v
		return clean
	return obj

def parse_nutrition_table(soup: BeautifulSoup, box_selector: str, default_nut: Dict) -> Dict[str, str]:
	nut = default_nut.copy()
	# Buscar el div que contiene "Datos nutricionales"
	nutrition_divs = soup.select(box_selector)
	table = None
	for box in nutrition_divs:
		h2 = box.find('h2')
		if h2 and 'datos nutricionales' in h2.get_text().lower():
			t = box.find('table')
			if t:
				table = t
				break
	
	if not table:
		return nut
	
	for tr in table.find_all('tr'):
		cells = tr.find_all(['td', 'th'])
		if len(cells) < 2:
			continue
		label = normalize_text(cells[0].get_text() or "").lower()
		value = normalize_text(cells[1].get_text() or "")
		if not label or not value:
			continue
		
		if 'valor energético' in label or 'valor energetico' in label:
			if 'kj' in value.lower():
				nut["valor_energetico_kj"] = value
			elif 'kcal' in value.lower():
				nut["valor_energetico_kcal"] = value
		elif 'grasas saturadas' in label or 'saturadas' in label:
			nut["grasas_saturadas_g"] = value
		elif 'grasas' in label:
			nut["grasas_g"] = value
		elif 'hidratos' in label or 'carbohidrato' in label:
			nut["hidratos_g"] = value
		elif 'azúcar' in label or 'azucar' in label:
			nut["azucares_g"] = value
		elif 'prote' in label:
			nut["proteinas_g"] = value
		elif 'sal' in label and 'grasa' not in label:
			nut["sal_g"] = value
	
	return nut

def parse_characteristics_table(soup: BeautifulSoup, box_selector: str, default_chars: Dict) -> Dict[str, str]:
	chars = default_chars.copy()
	char_divs = soup.select(box_selector)
	table = None
	for box in char_divs:
		h2 = box.find('h2')
		if h2 and 'características' in h2.get_text().lower():
			t = box.find('table')
			if t:
				table = t
				break
	
	if not table:
		return chars
	
	for tr in table.find_all('tr'):
		cells = tr.find_all(['td', 'th'])
		if len(cells) < 2:
			continue
		label = normalize_text(cells[0].get_text() or "").lower()
		value = normalize_text(cells[1].get_text() or "")
		if not label or not value:
			continue
		
		if 'nombre del operador' in label or 'nombre operador' in label:
			chars["nombre_operador"] = value
		elif 'dirección del operador' in label or 'direccion operador' in label:
			chars["direccion_operador"] = value
		elif 'país de origen' in label or 'pais de origen' in label:
			chars["pais_origen"] = value
		elif 'lugar de procedencia' in label:
			chars["lugar_procedencia"] = value
		elif 'denominación legal' in label or 'denominacion legal' in label:
			chars["denominacion_legal"] = value
		elif 'formato' in label:
			chars["formato"] = value
		elif 'peso neto' in label:
			chars["peso_neto"] = value
		elif 'sabor' in label:
			chars["sabor"] = value
		elif 'agrupación' in label or 'agrupacion' in label:
			chars["agrupacion"] = value
		elif 'capacidad' in label:
			chars["capacidad"] = value
		elif 'número de raciones' in label or 'numero de raciones' in label:
			chars["numero_raciones"] = value
		elif 'cantidad neta disgregada' in label:
			chars["cantidad_neta_disgregada"] = value
		elif 'signo de estimación' in label or 'signo de estimacion' in label:
			chars["signo_estimacion"] = value
	
	return chars

def extract_from_page(html: str, selectors: dict, default_nut: Dict, default_chars: Dict) -> Dict[str, str]:
	soup = BeautifulSoup(html, "html.parser")
	name_el = soup.select_one(selectors.get("name_selector"))
	price_el = soup.select_one(selectors.get("price_selector"))

	unidad = None
	precio_por_unidad = None
	# patrón ampliado para unidades: mg, g, kg, ml, cl, l (acepta sin espacio como "100g" o con espacio "100 g")
	unit_pattern = re.compile(r'\b\d[\d\s.,]*\s*(mg|g|kg|ml|cl|l)\b', re.IGNORECASE)

	for el in soup.select(selectors.get("unit_price_spans")):
		text = normalize_text(el.get_text())
		if not text:
			continue

		# evitar textos que describen "precio por" al considerar unidad
		if 'por' in text.lower() or re.search(r'€\s*por', text):
			# posible precio por unidad
			precio_por_unidad = text.strip("() ").replace('\xa0', ' ').strip()
			logger.debug("Detectado precio_por_unidad: %s", precio_por_unidad)
			continue

		# buscar unidades (gramos/litros/etc.)
		if unit_pattern.search(text):
			# normalizar: eliminar paréntesis y espacios redundantes
			u = text.strip("() ").replace('\xa0', ' ').strip()
			unidad = re.sub(r'\s+', ' ', u)
			logger.debug("Detectada unidad: %s (raw: %s)", unidad, text)
			continue

	nutricion = parse_nutrition_table(soup, selectors.get("box_div_selector"), default_nut)
	caracteristicas = parse_characteristics_table(soup, selectors.get("box_div_selector"), default_chars)

	name = normalize_text(name_el.get_text()) if name_el else None
	price = normalize_text(price_el.get_text()) if price_el else None

	return {
		"nombre": name,
		"precio": price,
		"unidad": unidad,
		"precio_por_unidad": precio_por_unidad,
		"nutricion": nutricion,
		"caracteristicas": caracteristicas
	}

def extract_products(product_sample: List[Dict]) -> List[Dict]:
	"""
	Procesa la muestra de productos y devuelve la lista de resultados.
	Usa config y constants importados por nombre.
	"""
	valid_products: List[Dict] = []
	total_processed = 0

	for item in product_sample:
		total_processed += 1
		orig_pid = item.get("id")
		url = item.get("url_productos_alcampo")
		logger.debug("Procesando producto original_id=%s contador=%s url=%s", orig_pid, total_processed, url)
		
		if not url:
			logger.warning("Producto original_id=%s sin URL. Saltando...", orig_pid)
			continue

		entry = {
			"url": url,
			"nombre": None,
			"precio": None,
			"unidad": None,
			"precio_por_unidad": None,
			"nutricion": constants.DEFAULT_NUTRITION.copy(),
			"caracteristicas": constants.DEFAULT_CARACTERISTICAS.copy()
		}

		try:
			resp = requests.get(url, headers=constants.HEADERS, timeout=config.request_timeout)
			if resp.status_code == 200:
				data = extract_from_page(
					resp.text,
					constants.SELECTORS,
					constants.DEFAULT_NUTRITION,
					constants.DEFAULT_CARACTERISTICAS
				)
				entry.update(data)
			else:
				logger.warning("Respuesta inesperada %s para URL %s (original_id=%s)", resp.status_code, url, orig_pid)
		except Exception:
			logger.exception("Error al procesar la URL %s (original_id=%s)", url, orig_pid)

		nombre_valido = entry.get("nombre")
		nutricion_valida = any(val is not None for val in entry.get("nutricion", {}).values())

		if nombre_valido and nutricion_valida:
			entry_clean = _prune_nones(entry)
			# Asignar id secuencial en el momento de añadir (evita huecos)
			entry_clean["id"] = len(valid_products) + 1
			valid_products.append(entry_clean)
			logger.debug("Producto válido añadido (original_id=%s id=%s)", orig_pid, entry_clean["id"])

			# Guardado incremental cada SAVE_INTERVAL productos válidos
			if len(valid_products) % SAVE_INTERVAL == 0:
				try:
					out_path = path_join_safe(config.base_dir, config.output_rel_path)
					save_json(valid_products, out_path, indent=2)
					logger.info("Guardado incremental: %d productos -> %s", len(valid_products), out_path)
				except Exception as e:
					logger.error("Error al guardar intermedio (%s): %s", out_path, e)
		else:
			logger.warning(
				"Producto original_id=%s descartado por falta de datos (nombre: %s, nutricion: %s).",
				orig_pid, bool(nombre_valido), nutricion_valida
			)

		time.sleep(config.delay_seconds)

	# No reasignamos ids: ya se han asignado secuencialmente al añadirse.
	return valid_products