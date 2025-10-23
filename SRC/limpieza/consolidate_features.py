"""
Consolidación de características adicionales (no nutricionales).
"""
import logging
import pandas as pd
from typing import List

from .util_numeric import clean_numeric_value

logger = logging.getLogger(__name__)

def safe_consolidate_columns(df: pd.DataFrame, unified_name: str, possible_cols: List[str]) -> pd.Series:
    """Consolida múltiples columnas en una, priorizando valores no nulos."""
    result = pd.Series([None] * len(df), index=df.index)
    
    for col in possible_cols:
        if col in df.columns:
            mask = result.isna() & df[col].notna()
            result[mask] = df[col][mask]
    
    return result

def consolidate_additional_features(df: pd.DataFrame) -> pd.DataFrame:
    """Consolida características adicionales (país, ingredientes, porción, precio)."""
    country_cols = ['desc_países de venta', 'desc_country', 'char_país', 'country']
    ingredients_cols = ['char_ingredientes', 'desc_ingredientes', 'nutr_ingredientes']
    serving_cols = ['char_porción', 'char_serving_size', 'char_tamaño porción']
    
    df['country'] = safe_consolidate_columns(df, 'country', country_cols)
    df['ingredients'] = safe_consolidate_columns(df, 'ingredients', ingredients_cols)
    df['serving_size'] = safe_consolidate_columns(df, 'serving_size', serving_cols)
    
    if 'price' in df.columns:
        df['price_clean'] = df['price'].apply(clean_numeric_value)
    
    if 'weight_volume_clean' in df.columns:
        df['weight_volume_clean'] = df['weight_volume_clean'].apply(clean_numeric_value)
    
    logger.info("Consolidadas características adicionales")
    return df
