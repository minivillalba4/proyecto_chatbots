"""
Imputación de valores faltantes.
"""
import logging
import pandas as pd

from .constants import NUTRITION_COLS

logger = logging.getLogger(__name__)

def impute_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Imputa valores nutricionales faltantes por fuente (mediana)."""
    for col in NUTRITION_COLS:
        if col in df.columns:
            for source in df['source'].unique():
                mask = (df['source'] == source) & df[col].isna()
                if mask.any():
                    median_value = df[df['source'] == source][col].median()
                    if pd.notna(median_value):
                        df.loc[mask, col] = median_value
                    else:
                        overall_median = df[col].median()
                        df.loc[mask, col] = overall_median if pd.notna(overall_median) else 0.0
    
    logger.info("Imputados valores nutricionales faltantes")
    return df
