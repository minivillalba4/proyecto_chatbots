# Header HTTP y otras constantes del proyecto (NO tocar si no sabes)
HEADERS = {
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
				  "(KHTML, like Gecko) Chrome/116.0 Safari/537.36"
}

# Diccionarios por defecto y selectores del proyecto
DEFAULT_NUTRITION = {
	"valor_energetico_kj": None,
	"valor_energetico_kcal": None,
	"grasas_g": None,
	"grasas_saturadas_g": None,
	"hidratos_g": None,
	"azucares_g": None,
	"proteinas_g": None,
	"sal_g": None
}

DEFAULT_CARACTERISTICAS = {
	"nombre_operador": None,
	"direccion_operador": None,
	"pais_origen": None,
	"lugar_procedencia": None,
	"denominacion_legal": None,
	"formato": None,
	"peso_neto": None,
	"sabor": None,
	"agrupacion": None,
	"capacidad": None,
	"numero_raciones": None,
	"cantidad_neta_disgregada": None,
	"signo_estimacion": None
}

# Selectores (ajustables si cambia la web)
SELECTORS = {
	"name_selector": "h1._display_xy0eg_1",
	"price_selector": "span._display_xy0eg_1",
	"unit_price_spans": "span._text_cn5lb_1._text--m_cn5lb_23",
	"box_div_selector": "div._box_1qlpx_1"
}
