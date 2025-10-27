"""
Funciones para parseo y estandarización de valores nutricionales.
"""
import re
import logging
import pandas as pd
from typing import Any, Optional, Dict

from .constants import (
    NUTRITION_KEYS_STANDARD, ALCAMPO_NUTRITION_MAP,
    OPENFOOD_NUTRITION_MAP, NUMERIC_CLEAN_TOKENS, DEFAULT_NUTRITION
)

logger = logging.getLogger(__name__)


def clean_numeric_value(value: Any) -> Optional[float]:
    """
    Extrae un float de una cadena con unidades y separadores europeos.

    Args:
        value: Valor a limpiar (str, int, float o None)

    Returns:
        Valor numérico o None si no se puede extraer
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, (int, float)):
        return float(value)

    s = str(value).strip().lower()
    s = s.replace(",", ".")

    for token in NUMERIC_CLEAN_TOKENS:
        s = s.replace(token, "")

    m = re.search(r"[-+]?\d*\.?\d+", s)
    try:
        return float(m.group()) if m else None
    except Exception:
        return None


def parse_energy_field(energy_str: str) -> Dict[str, Optional[float]]:
    """
    Extrae energía en kJ y kcal de un string combinado.
    Ejemplo: "1580 kj (375 kcal)" → {'energia_kj': 1580.0, 'energia_kcal': 375.0}

    Args:
        energy_str: String con información de energía

    Returns:
        Diccionario con energia_kj y energia_kcal
    """
    result = {'energia_kj': None, 'energia_kcal': None}

    if not energy_str or not isinstance(energy_str, str):
        return result

    energy_lower = energy_str.lower()

    kj_match = re.search(r'([\d.,]+)\s*kj', energy_lower)
    if kj_match:
        result['energia_kj'] = clean_numeric_value(kj_match.group(1))

    kcal_match = re.search(r'\(?([\d.,]+)\s*kcal\)?', energy_lower)
    if kcal_match:
        result['energia_kcal'] = clean_numeric_value(kcal_match.group(1))

    return result


def validate_nutrition_values(nutrition_dict: Dict[str, Optional[float]]) -> Dict[str, Optional[float]]:
    """
    Valida valores nutricionales y convierte todos a None si todos son 0.0.

    Mejora: Detecta productos con todos los valores en 0.0 (datos erróneos)
    y los convierte a None para indicar que no hay información nutricional.

    Args:
        nutrition_dict: Diccionario con valores nutricionales

    Returns:
        Diccionario validado
    """
    if not nutrition_dict:
        return nutrition_dict

    # Verificar si todos los valores son 0.0
    non_null_values = [v for v in nutrition_dict.values() if v is not None]

    if non_null_values and all(v == 0.0 for v in non_null_values):
        logger.warning("Todos los valores nutricionales son 0.0, convirtiendo a None")
        return {key: None for key in nutrition_dict.keys()}

    return nutrition_dict


def standardize_nutrition(nutrition_dict: Optional[Dict[str, Any]],
                         source: str = 'unknown') -> Dict[str, Optional[float]]:
    """
    Estandariza diccionario nutricional de cualquier fuente.

    Args:
        nutrition_dict: Diccionario con valores nutricionales originales
        source: Fuente de datos ('alcampo', 'openfoodfacts', 'unknown')

    Returns:
        Diccionario con claves estándar
    """
    if not nutrition_dict:
        return DEFAULT_NUTRITION.copy()

    result = {}

    # Determinar mapeo por presencia de claves o fuente explícita
    if 'valor_energetico_kj' in nutrition_dict or source == 'alcampo':
        mapping = ALCAMPO_NUTRITION_MAP
    else:
        mapping = OPENFOOD_NUTRITION_MAP

    # Aplicar mapeo
    for source_key, target_key in mapping.items():
        if source_key in nutrition_dict:
            result[target_key] = clean_numeric_value(nutrition_dict[source_key])

    # Caso especial: energía en OpenFoodFacts (formato combinado)
    if 'energia' in nutrition_dict and isinstance(nutrition_dict['energia'], str):
        energy_data = parse_energy_field(nutrition_dict['energia'])
        result.update(energy_data)

    # Asegurar todas las claves existen
    for key in NUTRITION_KEYS_STANDARD:
        if key not in result:
            result[key] = None

    # Validar valores (convierte todos a None si todos son 0.0)
    result = validate_nutrition_values(result)

    return result
