# Rutas y parámetros que el usuario puede modificar
base_dir = r"c:\Users\isma_\Desktop\Proyecto Chatbots"
input_rel_path = "Data\\productos_alcampo.json"
output_rel_path = "Data\\resultado_alcampo.json"

# Tamaño de la muestra a procesar (ajusta según necesites)
sample_size = 999999

# Permitir muestreo con reemplazo si sample_size > número de productos disponibles.
# Ponlo a True si necesitas obtener exactamente sample_size elementos aunque haya menos productos.
allow_replacement = False

# Timeouts / delays que el usuario puede ajustar
request_timeout = 12
delay_seconds = 0.6
