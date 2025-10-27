"""
Limpieza básica de texto para preprocesamiento NLP.
Maneja normalización Unicode, eliminación de caracteres especiales y patrones.
"""

import re
import logging
import unicodedata
import pandas as pd
from typing import Optional

from .constants import (
    SPECIAL_CHARS_TO_REMOVE,
    PATTERNS_TO_CLEAN
)


class TextCleaner:
    """Limpia y normaliza texto a nivel básico."""

    def __init__(self):
        """Inicializa el limpiador de texto."""
        self.logger = logging.getLogger(__name__)

        # Compilar patrones regex para eficiencia
        self.special_chars_pattern = re.compile(SPECIAL_CHARS_TO_REMOVE)
        self.compiled_patterns = {
            re.compile(pattern): replacement
            for pattern, replacement in PATTERNS_TO_CLEAN.items()
        }

    def normalize_unicode(self, text: str) -> str:
        """
        Normaliza caracteres Unicode manteniendo acentos del español.

        Args:
            text: Texto a normalizar

        Returns:
            Texto con Unicode normalizado
        """
        if not isinstance(text, str) or not text.strip():
            return ""

        # Normalizar a forma NFC (Canonical Decomposition, followed by Canonical Composition)
        # Esto mantiene los acentos pero normaliza variantes Unicode
        text = unicodedata.normalize('NFC', text)

        return text

    def remove_extra_whitespace(self, text: str) -> str:
        """
        Elimina espacios en blanco excesivos.

        Args:
            text: Texto a limpiar

        Returns:
            Texto sin espacios excesivos
        """
        if not isinstance(text, str):
            return ""

        # Múltiples espacios a uno solo
        text = re.sub(r'\s+', ' ', text)

        # Eliminar espacios al inicio y final
        text = text.strip()

        return text

    def remove_special_characters(self, text: str, keep_numbers: bool = False) -> str:
        """
        Elimina caracteres especiales manteniendo letras, espacios y acentos.

        Args:
            text: Texto a limpiar
            keep_numbers: Si True, mantiene números

        Returns:
            Texto sin caracteres especiales
        """
        if not isinstance(text, str) or not text.strip():
            return ""

        if keep_numbers:
            # Mantener letras, números, espacios y acentos
            pattern = re.compile(r'[^\w\sáéíóúüñÁÉÍÓÚÜÑ0-9]')
        else:
            # Solo letras, espacios y acentos
            pattern = self.special_chars_pattern

        text = pattern.sub(' ', text)

        return text

    def remove_patterns(self, text: str) -> str:
        """
        Elimina patrones específicos del dominio (cantidades, porcentajes, etc.).

        Args:
            text: Texto a limpiar

        Returns:
            Texto sin patrones específicos
        """
        if not isinstance(text, str) or not text.strip():
            return ""

        # Aplicar todos los patrones compilados
        for pattern, replacement in self.compiled_patterns.items():
            text = pattern.sub(replacement, text)

        return text

    def to_lowercase(self, text: str) -> str:
        """
        Convierte texto a minúsculas.

        Args:
            text: Texto a convertir

        Returns:
            Texto en minúsculas
        """
        if not isinstance(text, str):
            return ""

        return text.lower()

    def clean_text(
        self,
        text: str,
        lowercase: bool = True,
        remove_patterns: bool = True,
        remove_special_chars: bool = True,
        keep_numbers: bool = False
    ) -> str:
        """
        Pipeline completo de limpieza de texto.

        Args:
            text: Texto a limpiar
            lowercase: Convertir a minúsculas
            remove_patterns: Eliminar patrones específicos
            remove_special_chars: Eliminar caracteres especiales
            keep_numbers: Mantener números en el texto

        Returns:
            Texto limpio
        """
        # Validar entrada
        if pd.isna(text) or not isinstance(text, str):
            return ""

        text = str(text).strip()
        if not text:
            return ""

        # Paso 1: Normalizar Unicode
        text = self.normalize_unicode(text)

        # Paso 2: Convertir a minúsculas (antes de limpiar para mejor matching)
        if lowercase:
            text = self.to_lowercase(text)

        # Paso 3: Eliminar patrones específicos
        if remove_patterns:
            text = self.remove_patterns(text)

        # Paso 4: Eliminar caracteres especiales
        if remove_special_chars:
            text = self.remove_special_characters(text, keep_numbers=keep_numbers)

        # Paso 5: Limpiar espacios en blanco
        text = self.remove_extra_whitespace(text)

        return text

    def clean_categorical_field(self, text: str, separator: str = ",") -> str:
        """
        Limpia campos categóricos que contienen listas separadas por comas.

        Args:
            text: Texto con categorías separadas
            separator: Separador usado (por defecto coma)

        Returns:
            Texto limpio con categorías normalizadas
        """
        if pd.isna(text) or not isinstance(text, str):
            return ""

        # Dividir por separador
        categories = [cat.strip() for cat in text.split(separator) if cat.strip()]

        # Limpiar cada categoría
        cleaned_categories = []
        for cat in categories:
            cleaned = self.clean_text(
                cat,
                lowercase=True,
                remove_patterns=True,
                remove_special_chars=True,
                keep_numbers=False
            )
            if cleaned:
                cleaned_categories.append(cleaned)

        # Unir con espacio (mejor para NLP que coma)
        return " ".join(cleaned_categories)

    def clean_dataframe_column(
        self,
        df: pd.DataFrame,
        column: str,
        is_categorical: bool = False,
        overwrite: bool = True,
        **clean_kwargs
    ) -> pd.DataFrame:
        """
        Limpia una columna completa del DataFrame.

        Args:
            df: DataFrame con los datos
            column: Nombre de la columna a limpiar
            is_categorical: Si es un campo categórico con separadores
            overwrite: Si True, sobrescribe la columna original; si False, crea una nueva con sufijo _normalized
            **clean_kwargs: Argumentos adicionales para clean_text

        Returns:
            DataFrame con la columna limpia
        """
        if column not in df.columns:
            self.logger.warning(f"Columna '{column}' no encontrada en el DataFrame")
            return df

        self.logger.info(f"Limpiando columna: {column}")

        # Determinar el nombre de la columna de destino
        if overwrite:
            output_column = column
        else:
            output_column = f"{column}_normalized"

        if is_categorical:
            df[output_column] = df[column].apply(self.clean_categorical_field)
        else:
            df[output_column] = df[column].apply(
                lambda x: self.clean_text(x, **clean_kwargs)
            )

        # Contar valores procesados
        non_empty = df[output_column].notna() & (df[output_column] != "")
        count = non_empty.sum()

        if overwrite:
            self.logger.info(f"  → {count} valores limpiados (sobrescribiendo '{column}')")
        else:
            self.logger.info(f"  → {count} valores limpiados en '{output_column}'")

        return df
