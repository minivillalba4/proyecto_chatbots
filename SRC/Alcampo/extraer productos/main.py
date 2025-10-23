import sys
import os

# Añadir la ruta de SRC al path para importar utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import json
import logging
import random
from importlib import reload

import config
import constants
from extraer_productos import extract_products
from utils import load_json, save_json, path_join_safe

# configurar logging básico
logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

def safe_sample_list(items, k, replace=False):
	if replace:
		return [random.choice(items) for _ in range(k)]
	# sin reemplazo: limitar k a N
	k = min(k, len(items))
	return random.sample(items, k)

def main():
	reload(config)
	logger.info("Config recargado (sample_size actual: %r)", config.sample_size)

	# usar config para rutas (evita importar nombres sueltos)
	input_path = path_join_safe(config.base_dir, config.input_rel_path)
	output_path = path_join_safe(config.base_dir, config.output_rel_path)

	# debug: mostrar qué fichero config se está usando y el valor actual de sample_size
	logger.info("Config cargado desde: %s", getattr(config, "__file__", "<desconocido>"))
	logger.info("Valor de config.sample_size (tipo %s): %r", type(config.sample_size).__name__, config.sample_size)

	logger.info("Leyendo productos desde %s", input_path)
	all_products = load_json(input_path)

	total_products = len(all_products)
	try:
		requested = int(config.sample_size)
		if requested <= 0:
			raise ValueError("sample_size debe ser > 0")
	except Exception as exc:
		logger.warning("sample_size inválido (%r). Usando total disponible (%d). Detalle: %s", config.sample_size, total_products, exc)
		requested = total_products

	allow_replacement = bool(getattr(config, "allow_replacement", False))
	if requested > total_products and not allow_replacement:
		logger.warning(
			"Tamaño de muestra solicitado (%d) mayor que productos disponibles (%d). "
			"Activa allow_replacement=True en config.py para permitir duplicados.",
			requested, total_products
		)
		effective_sample_size = total_products
		use_replace = False
	else:
		use_replace = allow_replacement and requested > total_products
		effective_sample_size = requested if use_replace else min(requested, total_products)

	logger.info(
		"Tamaño de muestra solicitado: %d, efectivo: %d, reemplazo: %s",
		requested, effective_sample_size, use_replace
	)

	product_sample = safe_sample_list(all_products, effective_sample_size, replace=use_replace)

	results = extract_products(product_sample)

	save_json(results, output_path)

	logger.info("Resultados escritos en %s (productos procesados: %d)", output_path, len(results))

if __name__ == "__main__":
	main()