"""
Carga y mapeo de productos desde Alcampo.
"""
import logging
from typing import Any, Dict, List
from pathlib import Path

from .util_json import load_json_file
from .util_numeric import clean_numeric_value

logger = logging.getLogger(__name__)

def _base_row(source: str) -> Dict[str, Any]:
    """Estructura base para una fila de producto."""
    return {
        "source": source,
        "product_name": None,
        "brand": None,
        "country": None,
        "weight_volume_clean": None,
        "energia_kcal": None,
        "energia_kj": None,
        "grasas_totales": None,
        "grasas_saturadas": None,
        "carbohidratos": None,
        "azucares": None,
        "proteinas": None,
        "sal": None,
        "fibra": None,
    }

def cargar_alcampo(path: Path) -> List[Dict[str, Any]]:
    """Carga productos desde JSON de Alcampo y aplica mapeo inicial."""
    logger.info("="*60)
    logger.info("CARGANDO PRODUCTOS ALCAMPO")
    logger.info("="*60)
    
    data = load_json_file(path)
    if not isinstance(data, list):
        logger.error(f"Formato inesperado para Alcampo. Esperaba list, recibió {type(data).__name__}")
        return []
    
    out: List[Dict[str, Any]] = []
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            logger.warning(f"Item {idx} no es un dict, omitiendo")
            continue
        
        row = _base_row("alcampo")
        row["product_name"] = item.get("nombre")
        
        # Marca tentativa: primera palabra si está en mayúsculas
        nombre = (item.get("nombre") or "").strip()
        primera = nombre.split(" ", 1)[0].strip(".,:") if nombre else ""
        row["brand"] = primera if primera and primera.isupper() else None

        carac = item.get("caracteristicas", {}) or {}
        paises = [carac.get("pais_origen"), carac.get("lugar_procedencia")]
        row["country"] = ", ".join([p for p in paises if p]) or None

        # Peso/volumen
        weight_candidates = [
            item.get("unidad"),
            carac.get("peso_neto"),
            carac.get("capacidad"),
            carac.get("cantidad_neta_disgregada"),
        ]
        row["weight_volume_clean"] = next(
            (clean_numeric_value(v) for v in weight_candidates if v), None
        )

        nutr = item.get("nutricion", {}) or {}
        row["energia_kj"] = clean_numeric_value(nutr.get("valor_energetico_kj"))
        row["energia_kcal"] = clean_numeric_value(nutr.get("valor_energetico_kcal"))
        row["grasas_totales"] = clean_numeric_value(nutr.get("grasas_g"))
        row["grasas_saturadas"] = clean_numeric_value(nutr.get("grasas_saturadas_g"))
        row["carbohidratos"] = clean_numeric_value(nutr.get("hidratos_g"))
        row["azucares"] = clean_numeric_value(nutr.get("azucares_g"))
        row["proteinas"] = clean_numeric_value(nutr.get("proteinas_g"))
        row["sal"] = clean_numeric_value(nutr.get("sal_g"))
        
        out.append(row)
    
    logger.info(f"Productos Alcampo cargados: {len(out)}")
    return out
