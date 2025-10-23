"""
Consolidación de columnas nutricionales.
"""
import logging
import pandas as pd

from .constants import NUTRITION_COLS, NUTRITION_MAPPING
from .consolidate_features import safe_consolidate_columns
from .util_numeric import clean_numeric_value

logger = logging.getLogger(__name__)

def consolidate_nutrition_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Consolida datos nutricionales de Alcampo y OpenFoodFacts."""
    for unified_col, possible_cols in NUTRITION_MAPPING.items():
        df[unified_col] = safe_consolidate_columns(df, unified_col, possible_cols)
        df[unified_col] = df[unified_col].apply(clean_numeric_value)
    
    logger.info("Consolidadas columnas nutricionales")
    
    # Log de completitud
    for source in df['source'].unique():
        source_df = df[df['source'] == source]
        completeness = {
            col: f"{source_df[col].notna().sum()}/{len(source_df)}"
            for col in NUTRITION_COLS if col in source_df.columns
        }
        logger.info(f"Completitud '{source}': {completeness}")
    
    return df
