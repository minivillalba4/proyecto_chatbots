"""
Validación de productos unificados y sus componentes.
"""
import logging
from typing import Dict, Any

from .constants import REQUIRED_FIELDS

logger = logging.getLogger(__name__)


def validate_unified_product(product: Dict[str, Any]) -> bool:
    """
    Valida que el producto tenga todos los campos obligatorios.

    Campos obligatorios:
    - url (str, no None)
    - titulo (str, no None)
    - valores_nutricionales_100_g (dict)

    Args:
        product: Diccionario de producto unificado

    Returns:
        True si el producto es válido, False en caso contrario
    """
    if not isinstance(product, dict):
        logger.warning("Producto no es un diccionario")
        return False

    # Verificar campos obligatorios
    for field in REQUIRED_FIELDS:
        if field not in product or product[field] is None:
            logger.warning(f"Producto inválido: falta campo obligatorio '{field}'")
            return False

    # Verificar que valores_nutricionales_100_g sea un dict
    if not isinstance(product['valores_nutricionales_100_g'], dict):
        logger.warning("Campo 'valores_nutricionales_100_g' debe ser dict")
        return False

    return True


def validate_nutrition_completeness(nutrition_dict: Dict[str, Any], min_values: int = 1) -> bool:
    """
    Valida que el diccionario nutricional tenga al menos min_values valores no-None.

    Args:
        nutrition_dict: Diccionario con valores nutricionales
        min_values: Número mínimo de valores requeridos

    Returns:
        True si cumple el criterio de completitud
    """
    if not isinstance(nutrition_dict, dict):
        return False

    non_null_count = sum(1 for v in nutrition_dict.values() if v is not None and v != 0.0)
    return non_null_count >= min_values


def create_base_product() -> Dict[str, Any]:
    """
    Crea estructura base para producto unificado con todos los campos en None.

    Returns:
        Diccionario con estructura de producto vacío
    """
    from .constants import REQUIRED_FIELDS, OPTIONAL_FIELDS

    product = {}
    for field in REQUIRED_FIELDS + OPTIONAL_FIELDS:
        product[field] = None

    return product
