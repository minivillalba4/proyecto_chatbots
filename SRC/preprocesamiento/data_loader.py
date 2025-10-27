"""
Carga de datos desde CSV y estadísticas iniciales.
"""

import logging
import pandas as pd
from pathlib import Path
from typing import Dict, Any

from .config import INPUT_CSV, ENCODING
from .constants import REQUIRED_FIELDS


def setup_logger(name: str, log_file: Path, level=logging.INFO) -> logging.Logger:
    """
    Configura un logger con archivo y formato específico.

    Args:
        name: Nombre del logger
        log_file: Ruta del archivo de log
        level: Nivel de logging

    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Evitar duplicar handlers si ya existe
    if logger.handlers:
        return logger

    # Handler para archivo
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)

    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


class DataLoader:
    """Carga y valida datos desde CSV."""

    def __init__(self, input_file: Path = INPUT_CSV):
        """
        Inicializa el cargador de datos.

        Args:
            input_file: Ruta al archivo CSV de entrada
        """
        self.input_file = input_file
        self.logger = logging.getLogger(__name__)

    def load_data(self) -> pd.DataFrame:
        """
        Carga los datos desde el archivo CSV.

        Returns:
            DataFrame con los productos

        Raises:
            FileNotFoundError: Si el archivo no existe
            pd.errors.EmptyDataError: Si el archivo está vacío
        """
        self.logger.info(f"Cargando datos desde {self.input_file}")

        if not self.input_file.exists():
            self.logger.error(f"Archivo no encontrado: {self.input_file}")
            raise FileNotFoundError(f"No se encontró el archivo: {self.input_file}")

        try:
            # Leer CSV con encoding adecuado
            df = pd.read_csv(self.input_file, encoding=ENCODING)

            # Verificar que no esté vacío
            if df.empty:
                raise pd.errors.EmptyDataError("El archivo CSV está vacío")

            self.logger.info(
                f"Se cargaron {len(df)} productos con {len(df.columns)} columnas"
            )
            self.logger.info(f"Columnas: {', '.join(df.columns.tolist())}")

            return df

        except pd.errors.EmptyDataError as e:
            self.logger.error(f"Error: Archivo CSV vacío - {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado al cargar CSV: {e}")
            raise

    def validate_structure(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Valida que el DataFrame tenga la estructura mínima requerida.

        Args:
            df: DataFrame a validar

        Returns:
            DataFrame validado (sin cambios si es válido)

        Raises:
            ValueError: Si faltan columnas obligatorias
        """
        self.logger.info("Validando estructura del DataFrame")

        # Verificar columnas obligatorias
        missing_fields = [field for field in REQUIRED_FIELDS if field not in df.columns]

        if missing_fields:
            error_msg = f"Faltan campos obligatorios: {missing_fields}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        self.logger.info("Estructura validada correctamente")
        return df

    def get_data_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcula estadísticas básicas del DataFrame.

        Args:
            df: DataFrame con los productos

        Returns:
            Diccionario con estadísticas
        """
        self.logger.info("Calculando estadísticas de los datos")

        stats = {
            "total_products": len(df),
            "total_columns": len(df.columns),
            "columns": df.columns.tolist(),
            "memory_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
            "missing_data": {},
            "data_types": {}
        }

        # Contar valores nulos por columna
        null_counts = df.isnull().sum()
        for col, count in null_counts.items():
            if count > 0:
                percentage = round(count / len(df) * 100, 2)
                stats["missing_data"][col] = {
                    "count": int(count),
                    "percentage": percentage
                }

        # Tipos de datos
        stats["data_types"] = df.dtypes.astype(str).to_dict()

        # Estadísticas de fuentes (tiendas)
        if "tiendas" in df.columns:
            tiendas_count = df["tiendas"].value_counts()
            stats["tiendas_distribution"] = tiendas_count.head(10).to_dict()

        # Estadísticas de países
        if "country" in df.columns:
            country_count = df["country"].value_counts()
            stats["country_distribution"] = country_count.head(10).to_dict()

        self.logger.info(
            f"Estadísticas calculadas: {stats['total_products']} productos, "
            f"{stats['total_columns']} columnas, {stats['memory_mb']} MB"
        )

        return stats

    def get_nutrition_coverage(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcula la cobertura de datos nutricionales.

        Args:
            df: DataFrame con los productos

        Returns:
            Diccionario con cobertura nutricional
        """
        from .constants import NUTRITIONAL_FIELDS

        coverage = {
            "total_products": len(df),
            "fields_coverage": {}
        }

        for field in NUTRITIONAL_FIELDS:
            if field in df.columns:
                non_null = df[field].notna().sum()
                percentage = round(non_null / len(df) * 100, 2)
                coverage["fields_coverage"][field] = {
                    "count": int(non_null),
                    "percentage": percentage
                }

        # Productos con al menos N valores nutricionales
        if all(field in df.columns for field in NUTRITIONAL_FIELDS):
            nutrition_cols = [col for col in NUTRITIONAL_FIELDS if col in df.columns]
            products_with_nutrition = df[nutrition_cols].notna().sum(axis=1)

            coverage["products_with_at_least"] = {
                "1_nutrient": int((products_with_nutrition >= 1).sum()),
                "2_nutrients": int((products_with_nutrition >= 2).sum()),
                "3_nutrients": int((products_with_nutrition >= 3).sum()),
                "5_nutrients": int((products_with_nutrition >= 5).sum()),
                "all_nutrients": int((products_with_nutrition == len(nutrition_cols)).sum())
            }

        self.logger.info("Cobertura nutricional calculada")

        return coverage
