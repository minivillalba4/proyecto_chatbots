"""
Pipeline principal de preprocesamiento de datos de productos alimenticios.
Orquesta la limpieza, normalización, validación e ingeniería de características.
"""

import sys
import logging
from datetime import datetime
from pathlib import Path

# Configurar path para imports
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from SRC.preprocesamiento.config import (
    INPUT_CSV, OUTPUT_CSV, LOG_FILE, ENCODING
)
from SRC.preprocesamiento.constants import MIN_REQUIRED_NUTRIENTS
from SRC.preprocesamiento.data_loader import DataLoader, setup_logger
from SRC.preprocesamiento.cleaner import DataCleaner
from SRC.preprocesamiento.normalizer import DataNormalizer
from SRC.preprocesamiento.validator import DataValidator
from SRC.preprocesamiento.feature_engineer import FeatureEngineer
from SRC.preprocesamiento.text_normalizer import TextNormalizer


class PreprocessingPipeline:
    """Pipeline completo de preprocesamiento y feature engineering."""

    def __init__(self):
        """Inicializa el pipeline y sus componentes."""
        # Configurar logger principal
        self.logger = setup_logger("preprocessing", LOG_FILE)

        # Inicializar componentes
        self.loader = DataLoader(INPUT_CSV)
        self.cleaner = DataCleaner()
        self.normalizer = DataNormalizer()
        self.validator = DataValidator()
        self.feature_engineer = FeatureEngineer()
        self.text_normalizer = TextNormalizer()

        # Estadísticas del pipeline
        self.stats = {
            "start_time": None,
            "end_time": None,
            "duration_seconds": None,
            "initial_products": 0,
            "final_products": 0,
            "removed_products": 0,
            "initial_columns": 0,
            "final_columns": 0,
            "stages": {}
        }

    def run(self) -> dict:
        """
        Ejecuta el pipeline completo de preprocesamiento.

        Returns:
            Diccionario con estadísticas del proceso
        """
        self.logger.info("=" * 80)
        self.logger.info("INICIANDO PIPELINE DE PREPROCESAMIENTO")
        self.logger.info("=" * 80)

        self.stats["start_time"] = datetime.now()

        try:
            # ============================================================
            # ETAPA 1: CARGA DE DATOS
            # ============================================================
            self.logger.info("\n[ETAPA 1/7] CARGA DE DATOS")
            self.logger.info("-" * 80)

            df = self.loader.load_data()
            df = self.loader.validate_structure(df)

            self.stats["initial_products"] = len(df)
            self.stats["initial_columns"] = len(df.columns)

            # Estadísticas iniciales
            initial_stats = self.loader.get_data_statistics(df)
            nutrition_coverage = self.loader.get_nutrition_coverage(df)

            self.stats["stages"]["load"] = {
                "products": len(df),
                "columns": len(df.columns),
                "stats": initial_stats,
                "nutrition_coverage": nutrition_coverage
            }

            self.logger.info(f"Productos cargados: {len(df)}")
            self.logger.info(f"Columnas: {len(df.columns)}")

            # ============================================================
            # ETAPA 2: LIMPIEZA DE DATOS
            # ============================================================
            self.logger.info("\n[ETAPA 2/7] LIMPIEZA DE DATOS")
            self.logger.info("-" * 80)

            df, cleaning_report = self.cleaner.clean_all(df, MIN_REQUIRED_NUTRIENTS)

            self.stats["stages"]["cleaning"] = cleaning_report

            self.logger.info(
                f"Productos después de limpieza: {len(df)} "
                f"(removidos: {cleaning_report['initial_count'] - cleaning_report['final_count']})"
            )

            # ============================================================
            # ETAPA 3: NORMALIZACIÓN DE VALORES NUMÉRICOS
            # ============================================================
            self.logger.info("\n[ETAPA 3/7] NORMALIZACIÓN DE VALORES NUMÉRICOS")
            self.logger.info("-" * 80)

            df = self.normalizer.normalize_all(df)

            self.stats["stages"]["normalization"] = {
                "completed": True,
                "products_processed": len(df)
            }

            self.logger.info(f"Normalización completada: {len(df)} productos")

            # ============================================================
            # ETAPA 4: VALIDACIÓN DE CALIDAD
            # ============================================================
            self.logger.info("\n[ETAPA 4/7] VALIDACIÓN DE CALIDAD")
            self.logger.info("-" * 80)

            validation_report = self.validator.validate_all(df)

            self.stats["stages"]["validation"] = validation_report

            self.logger.info(
                f"Validación completada: "
                f"{validation_report['outliers'].get('total_outliers', 0)} outliers detectados, "
                f"{validation_report['consistency'].get('total_inconsistent_products', 0)} "
                f"productos con inconsistencias"
            )

            # ============================================================
            # ETAPA 5: INGENIERÍA DE CARACTERÍSTICAS
            # ============================================================
            self.logger.info("\n[ETAPA 5/7] INGENIERÍA DE CARACTERÍSTICAS")
            self.logger.info("-" * 80)

            initial_cols = len(df.columns)
            df = self.feature_engineer.create_all_features(df)
            final_cols = len(df.columns)

            self.stats["stages"]["feature_engineering"] = {
                "initial_columns": initial_cols,
                "final_columns": final_cols,
                "new_features": final_cols - initial_cols
            }

            self.logger.info(
                f"Características creadas: {final_cols - initial_cols} nuevas columnas"
            )

            # ============================================================
            # ETAPA 6: NORMALIZACIÓN DE TEXTO PARA NLP
            # ============================================================
            self.logger.info("\n[ETAPA 6/7] NORMALIZACIÓN DE TEXTO PARA NLP")
            self.logger.info("-" * 80)

            df = self.text_normalizer.normalize_all_fields(
                df=df,
                apply_tokenization=False,  # No crear columnas tokenizadas adicionales
                overwrite=True              # Sobrescribir columnas originales
            )

            text_stats = self.text_normalizer.get_statistics()
            self.stats["stages"]["text_normalization"] = text_stats

            self.logger.info(
                f"Campos de texto normalizados: {len(text_stats['fields_processed'])}"
            )

            # ============================================================
            # ETAPA 7: EXPORTACIÓN DE RESULTADOS
            # ============================================================
            self.logger.info("\n[ETAPA 7/7] EXPORTACIÓN DE RESULTADOS")
            self.logger.info("-" * 80)

            self._save_csv(df)

            # Actualizar estadísticas finales
            self.stats["final_products"] = len(df)
            self.stats["final_columns"] = len(df.columns)
            self.stats["removed_products"] = (
                self.stats["initial_products"] - self.stats["final_products"]
            )
            self.stats["end_time"] = datetime.now()
            self.stats["duration_seconds"] = (
                self.stats["end_time"] - self.stats["start_time"]
            ).total_seconds()

            # ============================================================
            # RESUMEN FINAL
            # ============================================================
            self.logger.info("=" * 80)
            self.logger.info("PIPELINE COMPLETADO EXITOSAMENTE")
            self.logger.info("=" * 80)
            self.logger.info(
                f"Productos: {self.stats['initial_products']} → "
                f"{self.stats['final_products']} "
                f"({self.stats['removed_products']} removidos, "
                f"{round(self.stats['removed_products']/self.stats['initial_products']*100, 1)}%)"
            )
            self.logger.info(
                f"Columnas: {self.stats['initial_columns']} → {self.stats['final_columns']} "
                f"(+{self.stats['final_columns'] - self.stats['initial_columns']} características)"
            )
            self.logger.info(
                f"Duración: {self.stats['duration_seconds']:.2f} segundos"
            )
            self.logger.info(f"Archivo CSV: {OUTPUT_CSV}")
            self.logger.info(f"Log: {LOG_FILE}")
            self.logger.info("=" * 80)

            return self.stats

        except Exception as e:
            self.logger.error(f"Error en el pipeline: {e}", exc_info=True)
            raise

    def _save_csv(self, df):
        """Guarda el DataFrame en formato CSV."""
        self.logger.info(f"Guardando CSV en: {OUTPUT_CSV}")

        OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(OUTPUT_CSV, index=False, encoding=ENCODING)

        self.logger.info(
            f"CSV guardado: {len(df)} filas, {len(df.columns)} columnas"
        )



def main():
    """Función principal."""
    pipeline = PreprocessingPipeline()
    pipeline.run()


if __name__ == "__main__":
    main()
