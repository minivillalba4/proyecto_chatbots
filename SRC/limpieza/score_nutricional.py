"""
Cálculo del score nutricional.
"""
import pandas as pd

def calculate_nutriscore(row: pd.Series) -> float:
    """Calcula score nutricional (0-100, mayor es mejor) basado en WHO."""
    score = 100.0
    
    # Penalizaciones
    if pd.notna(row['energia_kcal']) and row['energia_kcal'] > 400:
        score -= (row['energia_kcal'] - 400) / 10
    
    if pd.notna(row['grasas_totales']) and row['grasas_totales'] > 20:
        score -= (row['grasas_totales'] - 20) * 2
    
    if pd.notna(row['grasas_saturadas']) and row['grasas_saturadas'] > 5:
        score -= (row['grasas_saturadas'] - 5) * 3
    
    if pd.notna(row['azucares']) and row['azucares'] > 15:
        score -= (row['azucares'] - 15) * 2
    
    if pd.notna(row['sal']) and row['sal'] > 1.5:
        score -= (row['sal'] - 1.5) * 10
    
    # Bonificaciones
    if pd.notna(row['fibra']) and row['fibra'] > 6:
        score += (row['fibra'] - 6) * 2
    
    if pd.notna(row['proteinas']) and row['proteinas'] > 10:
        score += (row['proteinas'] - 10) * 1.5
    
    return max(0, min(100, score))
