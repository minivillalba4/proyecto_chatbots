"""
Funciones para extracción y parseo de campos específicos de productos.
"""
import re
import logging
from typing import Any, Optional, List

from .nutrition_parsers import clean_numeric_value

logger = logging.getLogger(__name__)


def parse_weight_volume(weight_str: Any) -> Optional[List]:
    """
    Extrae valor numérico y unidad de peso/volumen.

    Args:
        weight_str: String con peso/volumen (ej: "500g", "1.5l") o lista [valor, unidad]

    Returns:
        [valor, unidad] normalizado o None si no se puede parsear
        Normaliza kg→g (*1000), l→ml (*1000), cl→ml (*10)
    """
    if weight_str is None:
        return None

    # Si ya es una lista con formato [valor, unidad]
    if isinstance(weight_str, list):
        if len(weight_str) >= 2:
            value = clean_numeric_value(weight_str[0])
            unit = weight_str[1]
            if value is not None and unit is not None:
                return [value, str(unit)]
        return None

    weight_str = str(weight_str).strip()

    if 'rango de peso' in weight_str.lower() or not weight_str:
        return None

    # Pattern para capturar: número + unidad (g, kg, ml, l, cl)
    match = re.match(r'^\s*([\d.,]+)\s*([m]?[lgk]+|[c]?[l])\.?\s*$',
                    weight_str, re.IGNORECASE)

    if match:
        value = clean_numeric_value(match.group(1))
        unit = match.group(2).lower()

        if value is None:
            return None

        # Normalizar unidades a g y ml
        if unit == 'kg':
            value *= 1000
            unit = 'g'
        elif unit == 'l':
            value *= 1000
            unit = 'ml'
        elif unit == 'cl':
            value *= 10
            unit = 'ml'

        return [value, unit]

    return None


def clean_off_title(title: Optional[str]) -> Optional[str]:
    """
    Limpia título de OpenFoodFacts eliminando sufijos innecesarios.

    Ejemplo: "Copos de avena – Brüggen – 500 g Esta página..." → "Copos de avena"

    Args:
        title: Título original de OpenFoodFacts

    Returns:
        Título limpio
    """
    if not title:
        return None

    # Eliminar sufijo después de " – "
    parts = title.split(' – ', 1)
    return parts[0].strip() if parts else title.strip()


def parse_categories(categories_str: Optional[str]) -> Optional[List[str]]:
    """
    Convierte string de categorías en lista limpia.

    Args:
        categories_str: String con categorías separadas por comas o lista

    Returns:
        Lista de categorías o None
    """
    if not categories_str:
        return None

    if isinstance(categories_str, list):
        return categories_str

    cats = [cat.strip() for cat in str(categories_str).split(',') if cat.strip()]
    return cats if cats else None


def extract_allergens(allergens_data: Any) -> Optional[List[str]]:
    """
    Extrae y normaliza lista de alérgenos.

    Args:
        allergens_data: Lista o string con alérgenos

    Returns:
        Lista de alérgenos o None
    """
    if not allergens_data:
        return None

    if isinstance(allergens_data, list):
        allergens = [str(a).strip() for a in allergens_data if a]
        return allergens if allergens else None

    if isinstance(allergens_data, str):
        allergens = [a.strip() for a in allergens_data.split(',') if a.strip()]
        return allergens if allergens else None

    return None


def extract_certifications(description_dict: Optional[dict]) -> Optional[List[str]]:
    """
    Extrae certificaciones y sellos de calidad de OpenFoodFacts.

    Args:
        description_dict: Diccionario de descripción de OpenFoodFacts

    Returns:
        Lista de certificaciones o None
    """
    if not description_dict or not isinstance(description_dict, dict):
        return None

    cert_field = description_dict.get('sellos, certificados de calidad, premios')
    if not cert_field:
        return None

    if isinstance(cert_field, list):
        certs = [str(c).strip() for c in cert_field if c]
        return certs if certs else None

    if isinstance(cert_field, str):
        certs = [c.strip() for c in cert_field.split(',') if c.strip()]
        return certs if certs else None

    return None


def extract_brands(description_dict: Optional[dict]) -> Optional[str]:
    """
    Extrae marca del producto de OpenFoodFacts.

    Args:
        description_dict: Diccionario de descripción de OpenFoodFacts

    Returns:
        Marca del producto o None
    """
    if not description_dict or not isinstance(description_dict, dict):
        return None

    brand = description_dict.get('marcas')
    if brand and str(brand).strip():
        return str(brand).strip()

    return None


def extract_stores(description_dict: Optional[dict]) -> Optional[List[str]]:
    """
    Extrae tiendas donde se vende el producto (OpenFoodFacts).

    Args:
        description_dict: Diccionario de descripción de OpenFoodFacts

    Returns:
        Lista de tiendas o None
    """
    if not description_dict or not isinstance(description_dict, dict):
        return None

    stores_field = description_dict.get('tiendas')
    if not stores_field:
        return None

    if isinstance(stores_field, list):
        stores = [str(s).strip() for s in stores_field if s]
        return stores if stores else None

    if isinstance(stores_field, str):
        stores = [s.strip() for s in stores_field.split(',') if s.strip()]
        return stores if stores else None

    return None


def extract_numero_raciones(caracteristicas: Optional[dict]) -> Optional[int]:
    """
    Extrae número de raciones de las características de Alcampo.

    Args:
        caracteristicas: Diccionario de características de Alcampo

    Returns:
        Número de raciones como entero o None
    """
    if not caracteristicas or not isinstance(caracteristicas, dict):
        return None

    num_raciones = caracteristicas.get('numero_raciones')
    if num_raciones is None:
        return None

    try:
        return int(clean_numeric_value(num_raciones) or 0) or None
    except Exception:
        return None
