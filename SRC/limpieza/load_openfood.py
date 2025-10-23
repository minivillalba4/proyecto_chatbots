"""
Carga y mapeo de productos desde OpenFoodFacts.
"""
import logging
import re
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

def cargar_openfoodfacts(path: Path) -> List[Dict[str, Any]]:
    """Carga productos desde JSON de OpenFoodFacts y aplica mapeo inicial."""
    logger.info("="*60)
    logger.info("CARGANDO PRODUCTOS OPENFOODFACTS")
    logger.info("="*60)
    
    data = load_json_file(path)
    if data is None:
        logger.error("No se pudo cargar datos de OpenFoodFacts")
        return []
    
    products = data.get("products") if isinstance(data, dict) else data
    
    if not isinstance(products, list):
        logger.error(f"Formato inesperado para OpenFoodFacts. Esperaba list, recibió {type(products).__name__}")
        return []
    
    logger.info(f"Estructura OpenFoodFacts detectada: {len(products)} productos")
    
    out: List[Dict[str, Any]] = []
    for idx, p in enumerate(products):
        if not isinstance(p, dict):
            logger.warning(f"Producto {idx} no es un dict, omitiendo")
            continue
        
        row = _base_row("openfoodfacts")
        
        # Nombre del producto
        row["product_name"] = p.get("titulo") or p.get("product_name") or p.get("product_name_es") or p.get("product_name_en")
        
        # Marca
        brands = p.get("marca") or p.get("brands") or ""
        if isinstance(brands, str):
            brands_list = brands.split(",")
            row["brand"] = (brands_list[0].strip() or None) if brands_list else None
        
        # País
        country_data = p.get("pais") or p.get("countries") or p.get("countries_tags")
        if isinstance(country_data, list):
            row["country"] = ", ".join(country_data)
        elif isinstance(country_data, str):
            row["country"] = country_data
        
        # Peso/volumen
        size_candidates = [
            p.get("peso_neto"), p.get("cantidad"), p.get("serving_size"),
            p.get("quantity"), p.get("product_quantity"),
        ]
        row["weight_volume_clean"] = next(
            (clean_numeric_value(v) for v in size_candidates if v), None
        )
        
        # Valores nutricionales
        nutr = p.get("valores_nutricionales_100_g", {}) or p.get("nutriments", {}) or {}
        
        # Energía
        energia_str = nutr.get("energia") or nutr.get("energy-kcal_100g") or nutr.get("energy-kcal")
        if energia_str and isinstance(energia_str, str):
            energia_str = energia_str.lower()
            kcal_match = re.search(r'(\d+\.?\d*)\s*kcal', energia_str)
            if kcal_match:
                row["energia_kcal"] = clean_numeric_value(kcal_match.group(1))
            kj_match = re.search(r'(\d+\.?\d*)\s*kj', energia_str)
            if kj_match:
                row["energia_kj"] = clean_numeric_value(kj_match.group(1))
        
        if not row["energia_kcal"]:
            row["energia_kcal"] = clean_numeric_value(nutr.get("energy-kcal_100g") or nutr.get("energy-kcal"))
        if not row["energia_kj"]:
            row["energia_kj"] = clean_numeric_value(nutr.get("energy-kj_100g") or nutr.get("energy-kj"))
        
        # Otros nutrientes
        row["grasas_totales"] = clean_numeric_value(nutr.get("grasas") or nutr.get("fat_100g"))
        row["grasas_saturadas"] = clean_numeric_value(nutr.get("grasas_saturadas") or nutr.get("saturated-fat_100g"))
        row["carbohidratos"] = clean_numeric_value(nutr.get("hidratos_de_carbono") or nutr.get("carbohidratos") or nutr.get("carbohydrates_100g"))
        row["azucares"] = clean_numeric_value(nutr.get("azucares") or nutr.get("azúcares") or nutr.get("sugars_100g"))
        row["proteinas"] = clean_numeric_value(nutr.get("proteinas") or nutr.get("proteínas") or nutr.get("proteins_100g"))
        row["sal"] = clean_numeric_value(nutr.get("sal") or nutr.get("salt_100g"))
        row["fibra"] = clean_numeric_value(nutr.get("fibra_alimentaria") or nutr.get("fibra") or nutr.get("fiber_100g"))
        
        out.append(row)
    
    logger.info(f"Productos OpenFoodFacts cargados: {len(out)}")
    return out
