"""
Utilidades comunes para el proyecto de scraping.
Funciones reutilizables para manejo de archivos, JSON y directorios.
"""

import os
import json
import logging
from typing import Any, Dict, List, Union

logger = logging.getLogger(__name__)


def ensure_dir(path: str) -> None:
    """
    Crea un directorio si no existe.
    
    Args:
        path: Ruta del directorio a crear
    """
    if path and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        logger.debug("Directorio creado: %s", path)


def ensure_dir_for_file(filepath: str) -> None:
    """
    Crea el directorio padre de un archivo si no existe.
    
    Args:
        filepath: Ruta completa del archivo
    """
    directory = os.path.dirname(filepath)
    if directory:
        ensure_dir(directory)


def load_json(path: str, encoding: str = "utf-8") -> Union[Dict, List]:
    """
    Carga un archivo JSON.
    
    Args:
        path: Ruta del archivo JSON
        encoding: Codificación del archivo (default: utf-8)
    
    Returns:
        Contenido del archivo JSON (dict o list)
    
    Raises:
        FileNotFoundError: Si el archivo no existe
        json.JSONDecodeError: Si el archivo no es JSON válido
    """
    logger.debug("Cargando JSON desde: %s", path)
    with open(path, "r", encoding=encoding) as f:
        return json.load(f)


def save_json(
    data: Union[Dict, List],
    path: str,
    encoding: str = "utf-8",
    **dump_kwargs
) -> None:
    """
    Guarda datos en un archivo JSON, creando directorios si es necesario.
    
    Args:
        data: Datos a guardar (dict o list)
        path: Ruta del archivo de destino
        encoding: Codificación del archivo (default: utf-8)
        **dump_kwargs: Argumentos adicionales para json.dump
            (por defecto: ensure_ascii=False, indent=2)
    """
    # Establecer valores por defecto si no se proporcionan
    dump_kwargs.setdefault("ensure_ascii", False)
    dump_kwargs.setdefault("indent", 2)
    
    ensure_dir_for_file(path)
    
    logger.debug("Guardando JSON en: %s", path)
    with open(path, "w", encoding=encoding) as f:
        json.dump(data, f, **dump_kwargs)


def path_join_safe(*parts: str) -> str:
    """
    Une componentes de ruta de forma segura y normalizada.
    
    Args:
        *parts: Componentes de la ruta a unir
    
    Returns:
        Ruta normalizada
    """
    return os.path.normpath(os.path.join(*parts))
