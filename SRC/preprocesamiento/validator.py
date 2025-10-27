"""
Validación de calidad de datos: rangos, outliers, consistencia nutricional.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, Any

from .constants import (
    NUTRITIONAL_RANGES,
    NUTRITIONAL_FIELDS,
    OUTLIER_STD_THRESHOLD,
    KCAL_TO_KJ_FACTOR,
    ENERGY_TOLERANCE
)


class DataValidator:
    """Valida la calidad de los datos de productos."""

    def __init__(self):
        """Inicializa el validador de datos."""
        self.logger = logging.getLogger(__name__)

    def validate_nutritional_ranges(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Valida que los valores nutricionales estén en rangos válidos.
        NO elimina productos, solo reporta.

        Args:
            df: DataFrame con productos

        Returns:
            Diccionario con reporte de validación
        """
        self.logger.info("Validando rangos de valores nutricionales")

        report = {
            "total_checked": len(df),
            "products_with_errors": 0,
            "errors_by_field": {}
        }

        nutrition_cols = [col for col in NUTRITIONAL_FIELDS if col in df.columns]

        for col in nutrition_cols:
            if col not in NUTRITIONAL_RANGES:
                continue

            min_val, max_val = NUTRITIONAL_RANGES[col]

            # Contar valores fuera de rango
            mask = df[col].notna() & ((df[col] < min_val) | (df[col] > max_val))
            out_of_range = mask.sum()

            if out_of_range > 0:
                report["errors_by_field"][col] = {
                    "count": int(out_of_range),
                    "expected_range": (min_val, max_val)
                }

                self.logger.warning(
                    f"Campo '{col}': {out_of_range} valores fuera del rango "
                    f"[{min_val}, {max_val}]"
                )

        # Contar productos con al menos un error
        if report["errors_by_field"]:
            error_mask = pd.Series(False, index=df.index)
            for col in report["errors_by_field"].keys():
                min_val, max_val = NUTRITIONAL_RANGES[col]
                error_mask |= (df[col].notna() & ((df[col] < min_val) | (df[col] > max_val)))

            report["products_with_errors"] = int(error_mask.sum())

        self.logger.info(
            f"Validación de rangos completada: {report['products_with_errors']} productos "
            f"con valores fuera de rango"
        )

        return report

    def detect_outliers(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detecta outliers en valores nutricionales usando Z-score.
        NO elimina productos, solo reporta.

        Args:
            df: DataFrame con productos

        Returns:
            Diccionario con outliers por campo
        """
        self.logger.info(f"Detectando outliers (umbral: {OUTLIER_STD_THRESHOLD}σ)")

        outliers_report = {
            "outliers_by_field": {},
            "total_outliers": 0
        }

        nutrition_cols = [col for col in NUTRITIONAL_FIELDS if col in df.columns]

        for col in nutrition_cols:
            values = df[col].dropna()

            if len(values) < 2:
                continue

            # Calcular Z-score
            mean = values.mean()
            std = values.std()

            if std == 0:
                continue

            z_scores = np.abs((values - mean) / std)
            outliers = z_scores > OUTLIER_STD_THRESHOLD

            outlier_count = outliers.sum()

            if outlier_count > 0:
                outliers_report["outliers_by_field"][col] = {
                    "count": int(outlier_count),
                    "mean": round(mean, 2),
                    "std": round(std, 2),
                    "threshold_z": OUTLIER_STD_THRESHOLD
                }

                outliers_report["total_outliers"] += outlier_count

        self.logger.info(
            f"Outliers detectados: {outliers_report['total_outliers']} en "
            f"{len(outliers_report['outliers_by_field'])} campos"
        )

        return outliers_report

    def validate_consistency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Valida consistencia entre campos relacionados.
        NO elimina productos, solo reporta.

        Args:
            df: DataFrame con productos

        Returns:
            Diccionario con inconsistencias detectadas
        """
        self.logger.info("Validando consistencia entre campos")

        report = {
            "inconsistencies": [],
            "total_inconsistent_products": 0
        }

        # Validación 1: grasas_saturadas <= grasas_totales
        if "grasas_saturadas" in df.columns and "grasas_totales" in df.columns:
            mask = (
                df["grasas_saturadas"].notna() &
                df["grasas_totales"].notna() &
                (df["grasas_saturadas"] > df["grasas_totales"])
            )
            count = mask.sum()
            if count > 0:
                report["inconsistencies"].append({
                    "type": "grasas_saturadas > grasas_totales",
                    "count": int(count)
                })

        # Validación 2: azucares <= carbohidratos
        if "azucares" in df.columns and "carbohidratos" in df.columns:
            mask = (
                df["azucares"].notna() &
                df["carbohidratos"].notna() &
                (df["azucares"] > df["carbohidratos"])
            )
            count = mask.sum()
            if count > 0:
                report["inconsistencies"].append({
                    "type": "azucares > carbohidratos",
                    "count": int(count)
                })

        # Validación 3: coherencia energética (kcal vs kj)
        if "energia_kcal" in df.columns and "energia_kj" in df.columns:
            mask = (
                df["energia_kcal"].notna() &
                df["energia_kj"].notna() &
                (df["energia_kcal"] > 0)
            )

            if mask.any():
                expected_kj = df.loc[mask, "energia_kcal"] * KCAL_TO_KJ_FACTOR
                actual_kj = df.loc[mask, "energia_kj"]
                relative_diff = np.abs(actual_kj - expected_kj) / expected_kj

                inconsistent = relative_diff > ENERGY_TOLERANCE
                count = inconsistent.sum()

                if count > 0:
                    report["inconsistencies"].append({
                        "type": f"energia_kcal y energia_kj inconsistentes (>{ENERGY_TOLERANCE*100}%)",
                        "count": int(count)
                    })

        # Validación 4: suma de macronutrientes <= 100g
        macro_cols = ["grasas_totales", "carbohidratos", "proteinas", "fibra"]
        available_macros = [col for col in macro_cols if col in df.columns]

        if len(available_macros) >= 2:
            suma_macros = df[available_macros].sum(axis=1)
            mask = suma_macros > 100
            count = mask.sum()

            if count > 0:
                report["inconsistencies"].append({
                    "type": "suma_macronutrientes > 100g",
                    "count": int(count)
                })

        # Contar productos con al menos una inconsistencia
        inconsistent_mask = pd.Series(False, index=df.index)

        # Aplicar todas las condiciones
        if "grasas_saturadas" in df.columns and "grasas_totales" in df.columns:
            inconsistent_mask |= (
                df["grasas_saturadas"].notna() &
                df["grasas_totales"].notna() &
                (df["grasas_saturadas"] > df["grasas_totales"])
            )

        if "azucares" in df.columns and "carbohidratos" in df.columns:
            inconsistent_mask |= (
                df["azucares"].notna() &
                df["carbohidratos"].notna() &
                (df["azucares"] > df["carbohidratos"])
            )

        report["total_inconsistent_products"] = int(inconsistent_mask.sum())

        self.logger.info(
            f"Inconsistencias detectadas: {len(report['inconsistencies'])} tipos, "
            f"{report['total_inconsistent_products']} productos afectados"
        )

        return report

    def validate_all(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Ejecuta todas las validaciones y genera un reporte completo.
        NO elimina ni modifica productos, solo reporta.

        Args:
            df: DataFrame con productos

        Returns:
            Diccionario con reporte completo de validación
        """
        self.logger.info("Iniciando validación completa")

        report = {
            "total_products": len(df),
            "range_validation": {},
            "outliers": {},
            "consistency": {}
        }

        # Validación 1: Rangos nutricionales
        report["range_validation"] = self.validate_nutritional_ranges(df)

        # Validación 2: Outliers
        report["outliers"] = self.detect_outliers(df)

        # Validación 3: Consistencia
        report["consistency"] = self.validate_consistency(df)

        self.logger.info("Validación completa finalizada")

        return report
