"""
Construcción de DataFrames tabulares a partir de productos unificados.
Transforma JSON jerárquico a formato tabular básico (desanidación simple).
"""
import logging
import pandas as pd
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def extract_row_from_product(product: Dict[str, Any], index: int) -> Dict[str, Any]:
    """
    Extrae una fila tabular de un producto unificado.

    Args:
        product: Producto en formato unificado
        index: Índice del producto (para logging)

    Returns:
        Diccionario con datos tabulares
    """
    if not isinstance(product, dict):
        logger.warning(f"Producto {index} no es dict, omitiendo")
        return None

    row = {
        'product_name': product.get('titulo'),
        'url': product.get('url'),
        'descripcion': product.get('descripcion'),
        'country': product.get('origen'),
        'precio_total': product.get('precio_total'),
        'precio_por_cantidad': product.get('precio_por_cantidad'),
        'weight_volume_clean': None,
        'weight_unit': None,
        'categorias': None,
        'alergenos': None,
        'marcas': product.get('marcas'),
        'tiendas': None,
        'certificaciones': None,
        'numero_raciones': product.get('numero_raciones'),
        'nombre_operador': product.get('nombre_operador'),
    }

    # Extraer peso/volumen
    peso_vol = product.get('peso_volumen')
    if peso_vol and isinstance(peso_vol, list) and len(peso_vol) == 2:
        value = peso_vol[0]
        unit = peso_vol[1]
        if value is not None and unit is not None:
            row['weight_volume_clean'] = float(value) if isinstance(value, (int, float)) else value
            row['weight_unit'] = str(unit)

    # Extraer categorías
    categorias = product.get('categorias')
    if categorias:
        if isinstance(categorias, list):
            row['categorias'] = ', '.join(str(c) for c in categorias if c)
        elif isinstance(categorias, str):
            row['categorias'] = categorias

    # Extraer alérgenos
    alergenos = product.get('alergenos')
    if alergenos:
        if isinstance(alergenos, list):
            row['alergenos'] = ', '.join(str(a) for a in alergenos if a)
        elif isinstance(alergenos, str):
            row['alergenos'] = alergenos

    # Extraer tiendas
    tiendas = product.get('tiendas')
    if tiendas:
        if isinstance(tiendas, list):
            row['tiendas'] = ', '.join(str(t) for t in tiendas if t)
        elif isinstance(tiendas, str):
            row['tiendas'] = tiendas

    # Extraer certificaciones
    certificaciones = product.get('certificaciones')
    if certificaciones:
        if isinstance(certificaciones, list):
            row['certificaciones'] = ', '.join(str(c) for c in certificaciones if c)
        elif isinstance(certificaciones, str):
            row['certificaciones'] = certificaciones

    # Extraer valores nutricionales
    nutri = product.get('valores_nutricionales_100_g') or {}
    if not isinstance(nutri, dict):
        nutri = {}

    row['energia_kcal'] = nutri.get('energia_kcal')
    row['energia_kj'] = nutri.get('energia_kj')
    row['grasas_totales'] = nutri.get('grasas_g')
    row['grasas_saturadas'] = nutri.get('grasas_saturadas_g')
    row['carbohidratos'] = nutri.get('hidratos_g')
    row['azucares'] = nutri.get('azucares_g')
    row['proteinas'] = nutri.get('proteinas_g')
    row['sal'] = nutri.get('sal_g')
    row['fibra'] = nutri.get('fibra_g')

    return row


def flatten_to_dataframe(products: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convierte lista de productos unificados a DataFrame tabular.

    Args:
        products: Lista de productos en formato unificado

    Returns:
        DataFrame con estructura tabular básica (desanidado)
    """
    logger.info("="*60)
    logger.info("PASO 3: TRANSFORMANDO A DATAFRAME TABULAR")
    logger.info("="*60)

    flattened = []

    for idx, product in enumerate(products):
        row = extract_row_from_product(product, idx)
        if row:
            flattened.append(row)

    df = pd.DataFrame(flattened)
    logger.info(f"DataFrame creado: {df.shape}")
    logger.info(f"Columnas: {list(df.columns)}")

    return df
