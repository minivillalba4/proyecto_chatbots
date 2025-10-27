"""
Limpieza de datos: duplicados, valores nulos, normalización de texto.
"""

import logging
import re
import pandas as pd
from typing import Tuple

from .constants import MIN_REQUIRED_NUTRIENTS, NUTRITIONAL_FIELDS, TEXT_FIELDS


class DataCleaner:
    """Realiza limpieza básica de datos en DataFrames."""

    def __init__(self):
        """Inicializa el limpiador de datos."""
        self.logger = logging.getLogger(__name__)

    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Elimina productos duplicados basándose en la URL.

        Args:
            df: DataFrame con productos

        Returns:
            DataFrame sin duplicados
        """
        self.logger.info("Eliminando productos duplicados por URL")

        initial_count = len(df)

        # Eliminar duplicados manteniendo la primera ocurrencia
        if "url" in df.columns:
            df = df.drop_duplicates(subset=["url"], keep="first")
        else:
            self.logger.warning("Columna 'url' no encontrada, no se pueden eliminar duplicados")

        duplicates_removed = initial_count - len(df)

        self.logger.info(
            f"Duplicados eliminados: {duplicates_removed}. "
            f"Productos restantes: {len(df)}"
        )

        return df

    def filter_insufficient_nutrition(
        self,
        df: pd.DataFrame,
        min_nutrients: int = MIN_REQUIRED_NUTRIENTS
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Filtra productos sin información nutricional suficiente.

        Args:
            df: DataFrame con productos
            min_nutrients: Número mínimo de valores nutricionales no nulos

        Returns:
            Tupla (productos_válidos, productos_removidos)
        """
        self.logger.info(
            f"Filtrando productos con menos de {min_nutrients} valores nutricionales"
        )

        initial_count = len(df)

        # Identificar columnas nutricionales presentes
        nutrition_cols = [col for col in NUTRITIONAL_FIELDS if col in df.columns]

        if not nutrition_cols:
            self.logger.warning("No se encontraron columnas nutricionales")
            return df, pd.DataFrame()

        # Contar valores nutricionales no nulos por producto
        nutrition_count = df[nutrition_cols].notna().sum(axis=1)

        # Filtrar productos que cumplen el mínimo
        mask_valid = nutrition_count >= min_nutrients
        df_valid = df[mask_valid].copy()
        df_removed = df[~mask_valid].copy()

        self.logger.info(
            f"Productos con info nutricional suficiente: {len(df_valid)}. "
            f"Productos removidos: {len(df_removed)}"
        )

        return df_valid, df_removed

    def normalize_text_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normaliza campos de texto: elimina espacios extra, normaliza formato.

        Args:
            df: DataFrame con productos

        Returns:
            DataFrame con texto normalizado
        """
        self.logger.info("Normalizando campos de texto")

        text_fields_present = [field for field in TEXT_FIELDS if field in df.columns]

        for field in text_fields_present:
            # Convertir a string y normalizar
            df[field] = df[field].astype(str)
            df[field] = df[field].apply(self._normalize_text)

            # Convertir "nan" string de vuelta a NaN
            df[field] = df[field].replace("nan", pd.NA)

        self.logger.info(f"Normalizados {len(text_fields_present)} campos de texto")

        return df

    def _normalize_text(self, text: str) -> str:
        """
        Normaliza un texto individual.

        Args:
            text: Texto a normalizar

        Returns:
            Texto normalizado
        """
        if pd.isna(text) or text == "nan":
            return ""

        # Eliminar espacios múltiples y espacios al inicio/final
        text = re.sub(r'\s+', ' ', str(text)).strip()

        return text

    def clean_weight_volume(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpia y valida los campos weight_volume_clean y weight_unit.

        Args:
            df: DataFrame con productos

        Returns:
            DataFrame con peso/volumen limpio
        """
        self.logger.info("Limpiando campos weight_volume_clean y weight_unit")

        if "weight_volume_clean" not in df.columns or "weight_unit" not in df.columns:
            self.logger.warning("Columnas de peso/volumen no encontradas")
            return df

        # Convertir weight_volume_clean a numérico
        df["weight_volume_clean"] = pd.to_numeric(
            df["weight_volume_clean"],
            errors="coerce"
        )

        # Normalizar weight_unit (a minúsculas y sin espacios)
        df["weight_unit"] = df["weight_unit"].astype(str).str.lower().str.strip()

        # Reemplazar "nan" string con NaN real
        df["weight_unit"] = df["weight_unit"].replace("nan", pd.NA)

        # Contar registros válidos
        valid_weight = df["weight_volume_clean"].notna().sum()
        valid_unit = df["weight_unit"].notna().sum()

        self.logger.info(
            f"Registros con peso/volumen válido: {valid_weight}. "
            f"Registros con unidad válida: {valid_unit}"
        )

        return df

    def clean_numeric_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpia campos numéricos asegurando tipos correctos.

        Args:
            df: DataFrame con productos

        Returns:
            DataFrame con campos numéricos limpios
        """
        self.logger.info("Limpiando campos numéricos")

        numeric_cols = ["precio_total", "precio_por_cantidad", "numero_raciones"]

        for col in numeric_cols:
            if col in df.columns:
                # Convertir a numérico, valores inválidos se convierten a NaN
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Limpiar valores nutricionales
        nutrition_cols = [col for col in NUTRITIONAL_FIELDS if col in df.columns]

        for col in nutrition_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        self.logger.info("Campos numéricos limpiados")

        return df

    def remove_empty_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Elimina filas completamente vacías o con datos insignificantes.

        Args:
            df: DataFrame con productos

        Returns:
            DataFrame sin filas vacías
        """
        self.logger.info("Eliminando filas vacías")

        initial_count = len(df)

        # Eliminar filas donde todas las columnas (excepto URL) son NaN
        required_cols = ["product_name"]
        existing_required = [col for col in required_cols if col in df.columns]

        if existing_required:
            df = df.dropna(subset=existing_required, how="all")

        removed = initial_count - len(df)

        if removed > 0:
            self.logger.info(f"Filas vacías eliminadas: {removed}")
        else:
            self.logger.info("No se encontraron filas vacías")

        return df

    def clean_all(
        self,
        df: pd.DataFrame,
        min_nutrients: int = MIN_REQUIRED_NUTRIENTS
    ) -> Tuple[pd.DataFrame, dict]:
        """
        Ejecuta todos los pasos de limpieza en orden.

        Args:
            df: DataFrame con productos
            min_nutrients: Número mínimo de valores nutricionales requeridos

        Returns:
            Tupla (DataFrame limpio, reporte de limpieza)
        """
        self.logger.info("Iniciando proceso completo de limpieza")

        initial_count = len(df)
        report = {
            "initial_count": initial_count,
            "duplicates_removed": 0,
            "insufficient_nutrition_removed": 0,
            "empty_rows_removed": 0,
            "final_count": 0
        }

        # Paso 1: Eliminar filas vacías
        before = len(df)
        df = self.remove_empty_rows(df)
        report["empty_rows_removed"] = before - len(df)

        # Paso 2: Eliminar duplicados
        before = len(df)
        df = self.remove_duplicates(df)
        report["duplicates_removed"] = before - len(df)

        # Paso 3: Filtrar por información nutricional
        before = len(df)
        df, df_removed = self.filter_insufficient_nutrition(df, min_nutrients)
        report["insufficient_nutrition_removed"] = len(df_removed)

        # Paso 4: Normalizar texto
        df = self.normalize_text_fields(df)

        # Paso 5: Limpiar peso/volumen
        df = self.clean_weight_volume(df)

        # Paso 6: Limpiar campos numéricos
        df = self.clean_numeric_fields(df)

        report["final_count"] = len(df)
        total_removed = initial_count - report["final_count"]

        self.logger.info(
            f"Limpieza completada. Productos iniciales: {initial_count}, "
            f"Productos finales: {report['final_count']}, "
            f"Total removidos: {total_removed}"
        )

        return df, report
