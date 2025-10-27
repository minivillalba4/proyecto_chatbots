"""
Ingeniería de features y preparación de datos para Machine Learning.
Incluye cálculo de score nutricional, filtrado e imputación.
"""
import logging
import pandas as pd

from .constants import NUTRITION_COLS, MIN_NUTRITION_COLS

logger = logging.getLogger(__name__)


def calculate_nutriscore(row: pd.Series) -> float:
    """
    Calcula score nutricional (0-100, mayor es mejor) basado en WHO.

    Penalizaciones:
    - Calorías > 400 kcal
    - Grasas totales > 20g
    - Grasas saturadas > 5g
    - Azúcares > 15g
    - Sal > 1.5g

    Bonificaciones:
    - Fibra > 6g
    - Proteínas > 10g

    Args:
        row: Fila de DataFrame con valores nutricionales

    Returns:
        Score nutricional entre 0 y 100
    """
    score = 100.0

    # Penalizaciones
    if pd.notna(row.get('energia_kcal')) and row['energia_kcal'] > 400:
        score -= (row['energia_kcal'] - 400) / 10

    if pd.notna(row.get('grasas_totales')) and row['grasas_totales'] > 20:
        score -= (row['grasas_totales'] - 20) * 2

    if pd.notna(row.get('grasas_saturadas')) and row['grasas_saturadas'] > 5:
        score -= (row['grasas_saturadas'] - 5) * 3

    if pd.notna(row.get('azucares')) and row['azucares'] > 15:
        score -= (row['azucares'] - 15) * 2

    if pd.notna(row.get('sal')) and row['sal'] > 1.5:
        score -= (row['sal'] - 1.5) * 10

    # Bonificaciones
    if pd.notna(row.get('fibra')) and row['fibra'] > 6:
        score += (row['fibra'] - 6) * 2

    if pd.notna(row.get('proteinas')) and row['proteinas'] > 10:
        score += (row['proteinas'] - 10) * 1.5

    return max(0, min(100, score))


def filter_ml_ready_products(df: pd.DataFrame, min_cols: int = MIN_NUTRITION_COLS) -> pd.DataFrame:
    """
    Filtra productos con suficientes datos nutricionales para ML.

    Args:
        df: DataFrame con productos
        min_cols: Número mínimo de columnas nutricionales con valores

    Returns:
        DataFrame filtrado
    """
    if df.empty:
        logger.warning("DataFrame vacío recibido en filter_ml_ready_products")
        return df

    df['nutrition_completeness'] = df[NUTRITION_COLS].notna().sum(axis=1)
    ml_df = df[df['nutrition_completeness'] >= min_cols].copy()

    logger.info(f"Filtrados {len(df)} -> {len(ml_df)} productos "
                f"(mín {min_cols} valores nutricionales)")

    return ml_df


def impute_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Imputa valores nutricionales faltantes usando mediana.

    Si existe columna 'source', imputa por fuente.
    Si no existe, imputa con mediana global.

    Args:
        df: DataFrame con productos

    Returns:
        DataFrame con valores imputados
    """
    if df.empty:
        logger.warning("DataFrame vacío recibido en impute_missing_values")
        return df

    # Caso 1: Sin columna source (usar mediana global)
    if 'source' not in df.columns:
        for col in NUTRITION_COLS:
            if col in df.columns:
                median_val = df[col].median()
                if pd.notna(median_val):
                    df[col].fillna(median_val, inplace=True)
        logger.info("Imputados valores nutricionales faltantes (sin fuente)")
        return df

    # Caso 2: Con columna source (imputar por fuente)
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

    logger.info("Imputados valores nutricionales faltantes (por fuente)")
    return df


def apply_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica ingeniería de features completa al DataFrame.

    Pasos:
    1. Imputación de valores faltantes
    2. Filtrado de productos con suficientes datos
    3. Cálculo de score nutricional

    Args:
        df: DataFrame con productos

    Returns:
        DataFrame con features de ML
    """
    logger.info("="*60)
    logger.info("INGENIERÍA DE FEATURES PARA ML")
    logger.info("="*60)

    if df.empty:
        logger.warning("DataFrame vacío recibido")
        return df

    logger.info(f"Productos de entrada: {len(df)}")

    # 1. Imputación
    df = impute_missing_values(df)

    # 2. Filtrado
    df = filter_ml_ready_products(df)

    # 3. Cálculo de score nutricional
    df['score_nutricional'] = df.apply(calculate_nutriscore, axis=1)
    logger.info(f"Score nutricional - Media: {df['score_nutricional'].mean():.2f}, "
                f"Mediana: {df['score_nutricional'].median():.2f}")

    logger.info(f"Dataset ML final: {df.shape}")
    return df
