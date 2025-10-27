"""
Ingeniería de características: creación de características derivadas.
"""

import logging
import pandas as pd

from .constants import (
    THRESHOLD_HIGH_SALT,
    THRESHOLD_HIGH_SUGAR,
    THRESHOLD_HIGH_FAT,
    THRESHOLD_HIGH_SATURATED,
    CALORIE_CATEGORIES
)


class FeatureEngineer:
    """Crea características derivadas a partir de datos nutricionales."""

    def __init__(self):
        """Inicializa el ingeniero de características."""
        self.logger = logging.getLogger(__name__)

    def create_nutritional_ratios(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Crea ratios nutricionales entre valores relacionados.

        Args:
            df: DataFrame con productos

        Returns:
            DataFrame con ratios añadidos
        """
        self.logger.info("Creando ratios nutricionales")

        # Ratio grasas saturadas / grasas totales
        if "grasas_saturadas" in df.columns and "grasas_totales" in df.columns:
            mask = (df["grasas_totales"].notna()) & (df["grasas_totales"] > 0)
            df.loc[mask, "ratio_grasas_saturadas"] = (
                df.loc[mask, "grasas_saturadas"] / df.loc[mask, "grasas_totales"]
            ).round(3)

        # Ratio azúcares / carbohidratos
        if "azucares" in df.columns and "carbohidratos" in df.columns:
            mask = (df["carbohidratos"].notna()) & (df["carbohidratos"] > 0)
            df.loc[mask, "ratio_azucares"] = (
                df.loc[mask, "azucares"] / df.loc[mask, "carbohidratos"]
            ).round(3)

        # Ratio proteína / carbohidratos
        if "proteinas" in df.columns and "carbohidratos" in df.columns:
            mask = (df["carbohidratos"].notna()) & (df["carbohidratos"] > 0)
            df.loc[mask, "ratio_proteina_carbohidratos"] = (
                df.loc[mask, "proteinas"] / df.loc[mask, "carbohidratos"]
            ).round(3)

        # Ratio proteína / grasas
        if "proteinas" in df.columns and "grasas_totales" in df.columns:
            mask = (df["grasas_totales"].notna()) & (df["grasas_totales"] > 0)
            df.loc[mask, "ratio_proteina_grasas"] = (
                df.loc[mask, "proteinas"] / df.loc[mask, "grasas_totales"]
            ).round(3)

        self.logger.info("Ratios nutricionales creados")

        return df

    def create_health_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Crea indicadores booleanos de salud nutricional.

        Args:
            df: DataFrame con productos

        Returns:
            DataFrame con indicadores añadidos
        """
        self.logger.info("Creando indicadores de salud")

        # Indicador: tiene fibra
        if "fibra" in df.columns:
            df["tiene_fibra"] = (df["fibra"].notna()) & (df["fibra"] > 0)

        # Indicador: alto contenido de sal (>1.5g por 100g)
        if "sal" in df.columns:
            df["alto_contenido_sal"] = (df["sal"].notna()) & (df["sal"] > THRESHOLD_HIGH_SALT)

        # Indicador: alto contenido de azúcar (>15g por 100g)
        if "azucares" in df.columns:
            df["alto_contenido_azucar"] = (df["azucares"].notna()) & (df["azucares"] > THRESHOLD_HIGH_SUGAR)

        # Indicador: alto contenido de grasas (>17.5g por 100g)
        if "grasas_totales" in df.columns:
            df["alto_contenido_grasas"] = (df["grasas_totales"].notna()) & (df["grasas_totales"] > THRESHOLD_HIGH_FAT)

        # Indicador: alto contenido de grasas saturadas (>5g por 100g)
        if "grasas_saturadas" in df.columns:
            df["alto_contenido_grasas_saturadas"] = (
                (df["grasas_saturadas"].notna()) & (df["grasas_saturadas"] > THRESHOLD_HIGH_SATURATED)
            )

        # Indicador: tiene alérgenos
        if "alergenos" in df.columns:
            df["tiene_alergenos"] = df["alergenos"].notna() & (df["alergenos"] != "")

        # Indicador: tiene certificaciones
        if "certificaciones" in df.columns:
            df["tiene_certificaciones"] = df["certificaciones"].notna() & (df["certificaciones"] != "")

        self.logger.info("Indicadores de salud creados")

        return df

    def create_aggregate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Crea características agregadas de macronutrientes.

        Args:
            df: DataFrame con productos

        Returns:
            DataFrame con características agregadas
        """
        self.logger.info("Creando características agregadas")

        # Suma de macronutrientes
        macro_cols = []
        for col in ["grasas_totales", "carbohidratos", "proteinas", "fibra"]:
            if col in df.columns:
                macro_cols.append(col)

        if macro_cols:
            df["suma_macronutrientes"] = df[macro_cols].sum(axis=1, skipna=True).round(2)

        # Densidad calórica (ya está en energia_kcal, pero lo hacemos explícito)
        if "energia_kcal" in df.columns:
            df["densidad_calorica"] = df["energia_kcal"]

        # Calorías de grasas (1g grasa = 9 kcal)
        if "grasas_totales" in df.columns:
            df["calorias_de_grasas"] = (df["grasas_totales"] * 9).round(1)

        # Calorías de carbohidratos (1g carbohidrato = 4 kcal)
        if "carbohidratos" in df.columns:
            df["calorias_de_carbohidratos"] = (df["carbohidratos"] * 4).round(1)

        # Calorías de proteínas (1g proteína = 4 kcal)
        if "proteinas" in df.columns:
            df["calorias_de_proteinas"] = (df["proteinas"] * 4).round(1)

        self.logger.info("Características agregadas creadas")

        return df

    def create_categorical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Crea características categóricas basadas en rangos.

        Args:
            df: DataFrame con productos

        Returns:
            DataFrame con categorías añadidas
        """
        self.logger.info("Creando características categóricas")

        # Categoría calórica
        if "energia_kcal" in df.columns:
            def categorize_calories(kcal):
                if pd.isna(kcal):
                    return "desconocido"
                for category, (min_val, max_val) in CALORIE_CATEGORIES.items():
                    if min_val <= kcal < max_val:
                        return category
                return "muy_alto"

            df["categoria_calorica"] = df["energia_kcal"].apply(categorize_calories)

        # Perfil nutricional (basado en macronutrientes dominantes)
        if all(col in df.columns for col in ["grasas_totales", "carbohidratos", "proteinas"]):
            def get_macronutrient_profile(row):
                if pd.isna(row["grasas_totales"]) or pd.isna(row["carbohidratos"]) or pd.isna(row["proteinas"]):
                    return "desconocido"

                total = row["grasas_totales"] + row["carbohidratos"] + row["proteinas"]
                if total == 0:
                    return "desconocido"

                pct_fat = (row["grasas_totales"] / total) * 100
                pct_carb = (row["carbohidratos"] / total) * 100
                pct_protein = (row["proteinas"] / total) * 100

                max_macro = max(pct_fat, pct_carb, pct_protein)

                if max_macro == pct_fat:
                    return "alto_en_grasas"
                elif max_macro == pct_carb:
                    return "alto_en_carbohidratos"
                else:
                    return "alto_en_proteinas"

            df["perfil_macronutrientes"] = df.apply(get_macronutrient_profile, axis=1)

        self.logger.info("Características categóricas creadas")

        return df

    def create_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ejecuta todas las creaciones de características en orden.

        Args:
            df: DataFrame con productos

        Returns:
            DataFrame con todas las características derivadas
        """
        self.logger.info("Iniciando creación de características derivadas")

        initial_columns = len(df.columns)

        # Paso 1: Ratios nutricionales
        df = self.create_nutritional_ratios(df)

        # Paso 2: Indicadores de salud
        df = self.create_health_indicators(df)

        # Paso 3: Características agregadas
        df = self.create_aggregate_features(df)

        # Paso 4: Características categóricas
        df = self.create_categorical_features(df)

        final_columns = len(df.columns)
        new_features = final_columns - initial_columns

        self.logger.info(
            f"Creación de características completada. "
            f"Nuevas características: {new_features}. "
            f"Total columnas: {final_columns}"
        )

        return df
