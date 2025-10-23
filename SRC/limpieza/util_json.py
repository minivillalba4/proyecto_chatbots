"""
Utilidad para carga de archivos JSON.
"""
import json
import logging
from typing import Any
from pathlib import Path

logger = logging.getLogger(__name__)

def load_json_file(path: Path, encoding: str = "utf-8") -> Any:
    """Carga archivo JSON con manejo robusto de errores."""
    try:
        if not path.exists():
            logger.error(f"Archivo no existe: {path}")
            return None
        
        logger.info(f"Cargando archivo: {path}")
        raw = path.read_text(encoding=encoding).strip()
        
        if not raw:
            logger.warning(f"Archivo vacío: {path}")
            return None
        
        data = json.loads(raw)
        logger.info(f"JSON cargado exitosamente: {path} (tipo: {type(data).__name__})")
        
        if isinstance(data, list):
            logger.info(f"  - Elementos en lista: {len(data)}")
        elif isinstance(data, dict):
            logger.info(f"  - Keys en dict: {list(data.keys())}")
        
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Error de formato JSON en {path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error al cargar {path}: {e}")
        return None
