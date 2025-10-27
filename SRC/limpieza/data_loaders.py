"""
Funciones para carga y guardado de archivos JSON y CSV.
"""
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def load_json_file(path: Path, encoding: str = "utf-8") -> Any:
    """
    Carga archivo JSON con manejo robusto de errores.

    Args:
        path: Ruta al archivo JSON
        encoding: Codificación del archivo

    Returns:
        Datos cargados (dict o list) o None si hay error
    """
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


def save_json_file(data: Any, path: Path, encoding: str = "utf-8") -> bool:
    """
    Guarda datos en formato JSON.

    Args:
        data: Datos a guardar
        path: Ruta del archivo de salida
        encoding: Codificación del archivo

    Returns:
        True si se guardó correctamente, False si hubo error
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding=encoding) as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"JSON guardado exitosamente: {path}")
        return True
    except Exception as e:
        logger.error(f"Error al guardar JSON en {path}: {e}")
        return False
