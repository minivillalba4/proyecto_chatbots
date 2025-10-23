"""
Utilidad para limpieza de valores numéricos.
"""
import re
import pandas as pd
from typing import Any, Optional

def clean_numeric_value(value: Any) -> Optional[float]:
    """Extrae un float de una cadena con unidades y separadores europeos."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, (int, float)):
        return float(value)
        
    s = str(value).strip().lower()
    
    # Normalizar separador decimal y eliminar unidades
    s = s.replace(",", ".")
    for token in ["kcal", "kj", "cal", "g", "mg", "kg", "l", "ml", "cl", "€", "%", "x"]:
        s = s.replace(token, "")
        
    # Extraer primer número
    m = re.search(r"[-+]?\d*\.?\d+", s)
    try:
        return float(m.group()) if m else None
    except Exception:
        return None
