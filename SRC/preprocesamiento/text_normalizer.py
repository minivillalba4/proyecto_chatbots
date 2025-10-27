"""
Orquestador de normalización de texto para NLP.
Combina limpieza de texto y tokenización para crear campos normalizados.
"""

import logging
import pandas as pd
from typing import Dict, List

from .text_cleaner import TextCleaner
from .tokenizer import TextTokenizer
from .constants import (
    TEXT_FIELDS_TO_NORMALIZE,
    CATEGORICAL_TEXT_FIELDS,
    TEXT_NORMALIZED_SUFFIX
)


class TextNormalizer:
    """Normaliza campos de texto para análisis NLP."""

    def __init__(self, use_stemming: bool = True):
        """
        Inicializa el normalizador de texto.

        Args:
            use_stemming: Si True, aplica stemming en tokenización
        """
        self.logger = logging.getLogger(__name__)

        # Inicializar componentes
        self.text_cleaner = TextCleaner()

        try:
            self.tokenizer = TextTokenizer(use_stemming=use_stemming)
        except ImportError as e:
            self.logger.error(f"Error inicializando tokenizer: {e}")
            raise

        self.stats = {
            "fields_processed": [],
            "total_values_cleaned": 0,
            "total_values_tokenized": 0
        }

    def normalize_field(
        self,
        df: pd.DataFrame,
        field: str,
        apply_tokenization: bool = False,
        overwrite: bool = True
    ) -> pd.DataFrame:
        """
        Normaliza un campo específico del DataFrame.

        Args:
            df: DataFrame con los datos
            field: Nombre del campo a normalizar
            apply_tokenization: Si True, aplica tokenización y stopwords (crea columna adicional)
            overwrite: Si True, sobrescribe la columna original con texto limpio

        Returns:
            DataFrame con campos normalizados
        """
        if field not in df.columns:
            self.logger.warning(f"Campo '{field}' no encontrado, se omite")
            return df

        self.logger.info(f"Normalizando campo: {field}")

        # Determinar si es un campo categórico
        is_categorical = field in CATEGORICAL_TEXT_FIELDS

        # Paso 1: Limpieza básica de texto (sobrescribe la columna original)
        df = self.text_cleaner.clean_dataframe_column(
            df=df,
            column=field,
            is_categorical=is_categorical,
            overwrite=overwrite,
            lowercase=True,
            remove_patterns=True,
            remove_special_chars=True,
            keep_numbers=False
        )

        # Contar valores limpiados
        cleaned_count = (df[field].notna() & (df[field] != "")).sum()
        self.stats["total_values_cleaned"] += cleaned_count

        # Paso 2: Tokenización y stopwords (opcional - solo si se requiere para análisis adicional)
        if apply_tokenization:
            df = self.tokenizer.process_dataframe_column(
                df=df,
                column=field,
                output_column=f"{field}_tokenized",
                remove_stopwords=True,
                apply_stemming=True
            )

            # Contar valores tokenizados
            tokenized_count = (
                df[f"{field}_tokenized"].notna() &
                (df[f"{field}_tokenized"] != "")
            ).sum()
            self.stats["total_values_tokenized"] += tokenized_count

        self.stats["fields_processed"].append(field)

        return df

    def normalize_all_fields(
        self,
        df: pd.DataFrame,
        fields: List[str] = None,
        apply_tokenization: bool = False,
        overwrite: bool = True
    ) -> pd.DataFrame:
        """
        Normaliza todos los campos de texto especificados.

        Args:
            df: DataFrame con los datos
            fields: Lista de campos a normalizar (None usa TEXT_FIELDS_TO_NORMALIZE)
            apply_tokenization: Si True, aplica tokenización (crea columnas adicionales)
            overwrite: Si True, sobrescribe las columnas originales

        Returns:
            DataFrame con todos los campos normalizados
        """
        self.logger.info("=" * 80)
        self.logger.info("INICIANDO NORMALIZACIÓN DE TEXTO PARA NLP")
        self.logger.info("=" * 80)

        # Usar campos por defecto si no se especifican
        if fields is None:
            fields = TEXT_FIELDS_TO_NORMALIZE

        # Filtrar solo campos que existen en el DataFrame
        existing_fields = [field for field in fields if field in df.columns]

        self.logger.info(f"Campos a normalizar: {len(existing_fields)}")
        self.logger.info(f"Campos: {', '.join(existing_fields)}")
        self.logger.info(f"Modo: {'Sobrescribir originales' if overwrite else 'Crear nuevas columnas'}")

        # Resetear estadísticas
        self.stats = {
            "fields_processed": [],
            "total_values_cleaned": 0,
            "total_values_tokenized": 0,
            "initial_columns": len(df.columns),
            "final_columns": 0
        }

        # Normalizar cada campo
        for field in existing_fields:
            try:
                df = self.normalize_field(
                    df=df,
                    field=field,
                    apply_tokenization=apply_tokenization,
                    overwrite=overwrite
                )
            except Exception as e:
                self.logger.error(
                    f"Error normalizando campo '{field}': {e}",
                    exc_info=True
                )
                continue

        # Actualizar estadísticas finales
        self.stats["final_columns"] = len(df.columns)
        self.stats["new_columns"] = self.stats["final_columns"] - self.stats["initial_columns"]

        # Resumen
        self.logger.info("-" * 80)
        self.logger.info("NORMALIZACIÓN DE TEXTO COMPLETADA")
        self.logger.info(f"  Campos procesados: {len(self.stats['fields_processed'])}")
        self.logger.info(f"  Valores limpiados: {self.stats['total_values_cleaned']}")
        if apply_tokenization:
            self.logger.info(f"  Valores tokenizados: {self.stats['total_values_tokenized']}")
        self.logger.info(f"  Nuevas columnas: {self.stats['new_columns']}")
        self.logger.info("=" * 80)

        return df

    def get_normalized_columns(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Obtiene un diccionario con las columnas normalizadas generadas.

        Args:
            df: DataFrame procesado

        Returns:
            Diccionario con tipos de columnas normalizadas
        """
        normalized_cols = {
            "cleaned": [],
            "tokenized": []
        }

        for col in df.columns:
            if col.endswith(TEXT_NORMALIZED_SUFFIX):
                normalized_cols["cleaned"].append(col)
            elif col.endswith("_tokenized"):
                normalized_cols["tokenized"].append(col)

        return normalized_cols

    def create_combined_text_field(
        self,
        df: pd.DataFrame,
        fields: List[str],
        output_column: str = "combined_text",
        use_tokenized: bool = True
    ) -> pd.DataFrame:
        """
        Crea un campo combinado con múltiples campos de texto normalizados.
        Útil para embeddings o búsqueda semántica.

        Args:
            df: DataFrame con los datos
            fields: Lista de campos originales a combinar
            output_column: Nombre de la columna de salida
            use_tokenized: Si True, usa versiones tokenizadas; si False, usa normalizadas

        Returns:
            DataFrame con campo combinado
        """
        self.logger.info(f"Creando campo de texto combinado: {output_column}")

        suffix = "_tokenized" if use_tokenized else TEXT_NORMALIZED_SUFFIX

        # Identificar columnas a combinar
        columns_to_combine = []
        for field in fields:
            target_col = f"{field}{suffix}"
            if target_col in df.columns:
                columns_to_combine.append(target_col)

        if not columns_to_combine:
            self.logger.warning("No se encontraron columnas para combinar")
            df[output_column] = ""
            return df

        self.logger.info(f"Combinando {len(columns_to_combine)} columnas")

        # Combinar campos con espacios
        df[output_column] = df[columns_to_combine].apply(
            lambda row: " ".join(
                str(val) for val in row if pd.notna(val) and str(val).strip()
            ),
            axis=1
        )

        # Contar valores no vacíos
        non_empty = (df[output_column].notna() & (df[output_column] != "")).sum()
        self.logger.info(f"Campo combinado creado: {non_empty} valores no vacíos")

        return df

    def get_statistics(self) -> Dict:
        """
        Obtiene estadísticas del proceso de normalización.

        Returns:
            Diccionario con estadísticas
        """
        return self.stats.copy()
