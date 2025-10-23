"""
Filtrado de productos para ML.
"""
import logging
import pandas as pd

from .constants import NUTRITION_COLS, MIN_NUTRITION_COLS

logger = logging.getLogger(__name__)

def filter_ml_ready_products(df: pd.DataFrame, min_cols: int = MIN_NUTRITION_COLS) -> pd.DataFrame:
    """Filtra productos con suficientes datos nutricionales para ML."""
    df['nutrition_completeness'] = df[NUTRITION_COLS].notna().sum(axis=1)
    ml_df = df[df['nutrition_completeness'] >= min_cols].copy()
    
    logger.info(f"Filtrados {len(df)} -> {len(ml_df)} productos "
                f"(mín {min_cols} valores nutricionales)")
    
    return ml_df
