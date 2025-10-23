"""Selectores CSS y constantes inmutables usados por el scraper."""
# Eliminadas importaciones circulares (no importar config ni scraper aquí)

# Selectores CSS (usando atributos data-test para mayor estabilidad)
CSS_PRODUCTO_LINK = "a[data-test='fop-product-link']"
CSS_PRODUCTO_TITULO = "h3[data-test='fop-title']"
