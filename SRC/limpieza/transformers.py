"""
Transformadores de productos de diferentes fuentes al formato unificado.
Incluye mejoras en extracción de datos de Alcampo y OpenFoodFacts.
"""
import logging
from typing import Any, Dict, List

from .validators import create_base_product, validate_unified_product
from .nutrition_parsers import standardize_nutrition
from .field_extractors import (
    parse_weight_volume, clean_off_title, parse_categories,
    extract_allergens, extract_certifications, extract_brands,
    extract_stores, extract_numero_raciones
)
from .nutrition_parsers import clean_numeric_value

logger = logging.getLogger(__name__)


def transform_alcampo_product(product: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforma producto de Alcampo al formato unificado.

    MEJORAS:
    - Extrae nombre_operador de características
    - Extrae numero_raciones de características
    - Elimina búsqueda de categorías inexistentes

    Args:
        product: Producto en formato Alcampo

    Returns:
        Producto en formato unificado
    """
    if not product or not isinstance(product, dict):
        logger.warning("Producto Alcampo inválido (no es dict)")
        return create_base_product()

    unified = create_base_product()

    # ========== CAMPOS OBLIGATORIOS ==========
    unified['url'] = product.get('url')
    unified['titulo'] = product.get('nombre')
    unified['valores_nutricionales_100_g'] = standardize_nutrition(
        product.get('nutricion'), source='alcampo'
    )

    if not unified['url'] or not unified['titulo']:
        logger.warning("Producto Alcampo sin URL o título")

    # ========== CAMPOS OPCIONALES ==========
    caracteristicas = product.get('caracteristicas')
    if caracteristicas and isinstance(caracteristicas, dict):
        unified['descripcion'] = caracteristicas.get('denominacion_legal')

        # Origen
        origen = caracteristicas.get('pais_origen') or caracteristicas.get('lugar_procedencia')
        unified['origen'] = origen

        # Dirección de manufactura
        unified['direccion_manufactura'] = caracteristicas.get('direccion_operador')

        # NUEVO: Nombre del operador/fabricante
        unified['nombre_operador'] = caracteristicas.get('nombre_operador')

        # NUEVO: Número de raciones
        unified['numero_raciones'] = extract_numero_raciones(caracteristicas)

    # Precios
    unified['precio_total'] = clean_numeric_value(product.get('precio'))
    unified['precio_por_cantidad'] = clean_numeric_value(product.get('precio_por_unidad'))

    # Peso/Volumen
    unified['peso_volumen'] = parse_weight_volume(product.get('unidad'))

    # Alérgenos (Alcampo no proporciona esta información)
    unified['alergenos'] = None

    # Categorías (Alcampo no tiene categorías estructuradas en los datos actuales)
    unified['categorias'] = None

    # Campos que no aplican a Alcampo
    unified['marcas'] = None
    unified['tiendas'] = ['Alcampo']  # Siempre es Alcampo
    unified['certificaciones'] = None

    return unified


def transform_openfood_product(product: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforma producto de OpenFoodFacts al formato unificado.

    MEJORAS:
    - Extrae marcas del producto
    - Extrae tiendas donde se vende
    - Extrae certificaciones y sellos de calidad

    Args:
        product: Producto en formato OpenFoodFacts

    Returns:
        Producto en formato unificado
    """
    if not product or not isinstance(product, dict):
        logger.warning("Producto OFF inválido (no es dict)")
        return create_base_product()

    unified = create_base_product()

    # ========== CAMPOS OBLIGATORIOS ==========
    unified['url'] = product.get('URL')
    unified['titulo'] = clean_off_title(product.get('titulo'))
    unified['valores_nutricionales_100_g'] = standardize_nutrition(
        product.get('valores_nutricionales_100_g'), source='openfoodfacts'
    )

    if not unified['url'] or not unified['titulo']:
        logger.warning("Producto OFF sin URL o título")

    # ========== CAMPOS OPCIONALES ==========
    descripcion = product.get('descripcion')
    if descripcion and isinstance(descripcion, dict):
        unified['descripcion'] = descripcion.get('denominación general') or descripcion.get('denominacion_general')
        unified['categorias'] = parse_categories(descripcion.get('categorias'))

        # Origen
        origen = (descripcion.get('paises_de_venta') or
                 descripcion.get('lugares_de_fabricación_o_de_transformación') or
                 descripcion.get('lugares_de_fabricacion_o_de_transformacion'))
        unified['origen'] = origen

        # NUEVO: Marcas
        unified['marcas'] = extract_brands(descripcion)

        # NUEVO: Tiendas
        unified['tiendas'] = extract_stores(descripcion)

        # NUEVO: Certificaciones
        unified['certificaciones'] = extract_certifications(descripcion)

    # Precios (OpenFoodFacts no proporciona precios)
    unified['precio_total'] = None
    unified['precio_por_cantidad'] = None

    # Peso/Volumen
    unified['peso_volumen'] = parse_weight_volume(product.get('peso_volumen'))

    # Alérgenos
    unified['alergenos'] = extract_allergens(product.get('alergenos'))

    # Dirección de manufactura (no disponible en OFF)
    unified['direccion_manufactura'] = None

    # Nombre operador (no disponible en OFF)
    unified['nombre_operador'] = None

    # Número de raciones (no disponible en OFF)
    unified['numero_raciones'] = None

    return unified


def unify_products_from_sources(alcampo_data: Any, openfood_data: Any) -> List[Dict[str, Any]]:
    """
    Unifica productos de múltiples fuentes en un solo dataset.

    Args:
        alcampo_data: Lista de productos de Alcampo
        openfood_data: Lista o dict con productos de OpenFoodFacts

    Returns:
        Lista de productos unificados
    """
    logger.info("="*60)
    logger.info("UNIFICANDO PRODUCTOS DE MÚLTIPLES FUENTES")
    logger.info("="*60)

    unified_products = []

    # ========== PROCESAR ALCAMPO ==========
    if alcampo_data and isinstance(alcampo_data, list):
        logger.info(f"Procesando {len(alcampo_data)} productos de Alcampo")

        for idx, product in enumerate(alcampo_data):
            try:
                unified = transform_alcampo_product(product)
                if validate_unified_product(unified):
                    unified_products.append(unified)
                else:
                    logger.warning(f"Producto Alcampo #{idx} no válido, omitiendo")
            except Exception as e:
                logger.error(f"Error procesando producto Alcampo #{idx}: {e}")
    else:
        logger.warning("No se pudieron cargar productos de Alcampo")

    # ========== PROCESAR OPENFOODFACTS ==========
    # Manejar estructura con "products" o lista directa
    if isinstance(openfood_data, dict) and 'products' in openfood_data:
        openfood_products = openfood_data['products']
    elif isinstance(openfood_data, list):
        openfood_products = openfood_data
    else:
        openfood_products = []
        logger.warning("Formato de OpenFoodFacts no reconocido")

    if openfood_products:
        logger.info(f"Procesando {len(openfood_products)} productos de OpenFoodFacts")

        for idx, product in enumerate(openfood_products):
            try:
                unified = transform_openfood_product(product)
                if validate_unified_product(unified):
                    unified_products.append(unified)
                else:
                    logger.warning(f"Producto OFF #{idx} no válido, omitiendo")
            except Exception as e:
                logger.error(f"Error procesando producto OFF #{idx}: {e}")
    else:
        logger.warning("No se pudieron cargar productos de OpenFoodFacts")

    logger.info("="*60)
    logger.info(f"UNIFICACIÓN COMPLETADA: {len(unified_products)} productos totales")
    logger.info("="*60)

    return unified_products
