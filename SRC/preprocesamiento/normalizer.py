"""
Normalización de valores: unidades, precios, rangos nutricionales.
"""

import logging
import pandas as pd

from .constants import (
    CONVERSION_FACTORS,
    VALID_WEIGHT_UNITS,
    VALID_VOLUME_UNITS,
    NUTRITIONAL_FIELDS
)


class DataNormalizer:
    """Normaliza valores en DataFrames de productos."""

    def __init__(self):
        """Inicializa el normalizador de datos."""
        self.logger = logging.getLogger(__name__)

    def normalize_weight_volume_units(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normaliza unidades de peso/volumen a gramos/mililitros base.

        Args:
            df: DataFrame con productos

        Returns:
            DataFrame con unidades normalizadas
        """
        self.logger.info("Normalizando unidades de peso/volumen")

        if "weight_volume_clean" not in df.columns or "weight_unit" not in df.columns:
            self.logger.warning("Columnas de peso/volumen no encontradas")
            return df

        normalized_count = 0

        # Iterar por cada fila y normalizar
        for idx in df.index:
            value = df.at[idx, "weight_volume_clean"]
            unit = df.at[idx, "weight_unit"]

            # Saltar si falta valor o unidad
            if pd.isna(value) or pd.isna(unit):
                continue

            unit_lower = str(unit).lower().strip()

            # Verificar si la unidad es válida y convertir
            if unit_lower in CONVERSION_FACTORS:
                factor = CONVERSION_FACTORS[unit_lower]

                # Normalizar a g o ml según el tipo de unidad original
                if unit_lower in VALID_WEIGHT_UNITS:
                    df.at[idx, "weight_volume_clean"] = float(value) * factor
                    df.at[idx, "weight_unit"] = "g"
                    normalized_count += 1
                elif unit_lower in VALID_VOLUME_UNITS:
                    df.at[idx, "weight_volume_clean"] = float(value) * factor
                    df.at[idx, "weight_unit"] = "ml"
                    normalized_count += 1
            else:
                self.logger.debug(f"Unidad desconocida: '{unit}' en índice {idx}")

        self.logger.info(f"Unidades normalizadas en {normalized_count} productos")

        return df

    def normalize_prices(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normaliza precios, asegurando valores positivos y formato correcto.

        Args:
            df: DataFrame con productos

        Returns:
            DataFrame con precios normalizados
        """
        self.logger.info("Normalizando precios")

        price_cols = ["precio_total", "precio_por_cantidad"]

        for col in price_cols:
            if col not in df.columns:
                continue

            # Convertir a numérico
            df[col] = pd.to_numeric(df[col], errors="coerce")

            # Establecer valores negativos como NaN
            negative_mask = df[col] < 0
            negative_count = negative_mask.sum()

            if negative_count > 0:
                self.logger.warning(
                    f"Encontrados {negative_count} precios negativos en '{col}', "
                    f"se establecen como NaN"
                )
                df.loc[negative_mask, col] = pd.NA

            # Redondear a 2 decimales
            df[col] = df[col].round(2)

        self.logger.info("Normalización de precios completada")

        return df

    def calculate_precio_unitario(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula precio por 100g/100ml cuando falta precio_por_cantidad.

        Args:
            df: DataFrame con productos

        Returns:
            DataFrame con precio unitario calculado
        """
        self.logger.info("Calculando precio por 100g/100ml cuando es posible")

        required_cols = ["precio_total", "precio_por_cantidad", "weight_volume_clean"]

        if not all(col in df.columns for col in required_cols):
            self.logger.warning("Faltan columnas necesarias para calcular precio unitario")
            return df

        # Identificar productos sin precio_por_cantidad pero con precio_total y peso
        mask = (
            df["precio_por_cantidad"].isna() &
            df["precio_total"].notna() &
            df["weight_volume_clean"].notna() &
            (df["weight_volume_clean"] > 0)
        )

        calculated_count = mask.sum()

        if calculated_count > 0:
            # Calcular precio por 100g o 100ml
            df.loc[mask, "precio_por_cantidad"] = (
                (df.loc[mask, "precio_total"] / df.loc[mask, "weight_volume_clean"]) * 100
            ).round(2)

            self.logger.info(f"Precio unitario calculado para {calculated_count} productos")
        else:
            self.logger.info("No hay productos para calcular precio unitario")

        return df

    def add_peso_en_kg(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Añade campo auxiliar peso_en_kg para facilitar análisis.

        Args:
            df: DataFrame con productos

        Returns:
            DataFrame con campo peso_en_kg
        """
        self.logger.info("Añadiendo campo peso_en_kg")

        if "weight_volume_clean" not in df.columns or "weight_unit" not in df.columns:
            self.logger.warning("Columnas de peso/volumen no encontradas")
            df["peso_en_kg"] = pd.NA
            return df

        # Crear columna peso_en_kg
        df["peso_en_kg"] = pd.NA

        # Para unidades de peso en gramos
        mask_g = (df["weight_unit"] == "g") & df["weight_volume_clean"].notna()
        df.loc[mask_g, "peso_en_kg"] = (df.loc[mask_g, "weight_volume_clean"] / 1000).round(3)

        # Para unidades de volumen en ml (aproximación: 1ml ≈ 1g)
        mask_ml = (df["weight_unit"] == "ml") & df["weight_volume_clean"].notna()
        df.loc[mask_ml, "peso_en_kg"] = (df.loc[mask_ml, "weight_volume_clean"] / 1000).round(3)

        non_null_count = df["peso_en_kg"].notna().sum()
        self.logger.info(f"Campo peso_en_kg añadido para {non_null_count} productos")

        return df

    def validate_nutritional_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Valida que los valores nutricionales sean numéricos y positivos.

        Args:
            df: DataFrame con productos

        Returns:
            DataFrame con valores nutricionales validados
        """
        self.logger.info("Validando valores nutricionales")

        nutrition_cols = [col for col in NUTRITIONAL_FIELDS if col in df.columns]

        for col in nutrition_cols:
            # Convertir a numérico
            df[col] = pd.to_numeric(df[col], errors="coerce")

            # Establecer valores negativos como NaN
            negative_mask = df[col] < 0
            negative_count = negative_mask.sum()

            if negative_count > 0:
                self.logger.warning(
                    f"Encontrados {negative_count} valores negativos en '{col}', "
                    f"se establecen como NaN"
                )
                df.loc[negative_mask, col] = pd.NA

        self.logger.info("Validación de valores nutricionales completada")

        return df

    def normalize_all(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ejecuta todos los pasos de normalización en orden.

        Args:
            df: DataFrame con productos

        Returns:
            DataFrame normalizado
        """
        self.logger.info("Iniciando normalización completa")

        initial_count = len(df)

        # Paso 1: Normalizar unidades de peso/volumen
        df = self.normalize_weight_volume_units(df)

        # Paso 2: Normalizar precios
        df = self.normalize_prices(df)

        # Paso 3: Validar valores nutricionales
        df = self.validate_nutritional_values(df)

        # Paso 4: Calcular precio unitario
        df = self.calculate_precio_unitario(df)

        # Paso 5: Añadir peso en kg
        df = self.add_peso_en_kg(df)

        final_count = len(df)

        self.logger.info(
            f"Normalización completada. Productos procesados: {final_count}"
        )

        return df
