"""
Tokenización y eliminación de stopwords para NLP.
Utiliza NLTK para stopwords en español y tokenización.
"""

import logging
import pandas as pd
from typing import List, Set, Optional

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import SnowballStemmer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

from .constants import (
    DOMAIN_STOPWORDS,
    MIN_TOKEN_LENGTH,
    MAX_TOKEN_LENGTH,
    USE_STEMMING,
    STEMMER_LANGUAGE
)


class TextTokenizer:
    """Tokeniza texto y elimina stopwords."""

    def __init__(self, use_stemming: bool = USE_STEMMING):
        """
        Inicializa el tokenizador.

        Args:
            use_stemming: Si True, aplica stemming a los tokens
        """
        self.logger = logging.getLogger(__name__)
        self.use_stemming = use_stemming

        # Verificar disponibilidad de NLTK
        if not NLTK_AVAILABLE:
            self.logger.error(
                "NLTK no está instalado. Por favor instala: pip install nltk"
            )
            raise ImportError("NLTK es requerido para tokenización")

        # Descargar recursos necesarios de NLTK
        self._download_nltk_resources()

        # Cargar stopwords
        self.stopwords = self._load_stopwords()

        # Inicializar stemmer si se requiere
        self.stemmer = None
        if self.use_stemming:
            try:
                self.stemmer = SnowballStemmer(STEMMER_LANGUAGE)
                self.logger.info(f"Stemmer inicializado: {STEMMER_LANGUAGE}")
            except Exception as e:
                self.logger.warning(f"No se pudo inicializar stemmer: {e}")
                self.use_stemming = False

    def _download_nltk_resources(self):
        """Descarga recursos necesarios de NLTK."""
        resources = ['punkt', 'stopwords', 'punkt_tab']

        for resource in resources:
            try:
                nltk.data.find(f'tokenizers/{resource}')
            except LookupError:
                try:
                    nltk.data.find(f'corpora/{resource}')
                except LookupError:
                    self.logger.info(f"Descargando recurso NLTK: {resource}")
                    try:
                        nltk.download(resource, quiet=True)
                    except Exception as e:
                        self.logger.warning(f"No se pudo descargar {resource}: {e}")

    def _load_stopwords(self) -> Set[str]:
        """
        Carga stopwords en español desde NLTK y las del dominio.

        Returns:
            Set con todas las stopwords
        """
        try:
            # Stopwords de NLTK en español
            nltk_stopwords = set(stopwords.words('spanish'))
            self.logger.info(f"Cargadas {len(nltk_stopwords)} stopwords de NLTK")

            # Combinar con stopwords del dominio
            all_stopwords = nltk_stopwords.union(DOMAIN_STOPWORDS)

            self.logger.info(
                f"Total stopwords: {len(all_stopwords)} "
                f"(NLTK: {len(nltk_stopwords)}, Dominio: {len(DOMAIN_STOPWORDS)})"
            )

            return all_stopwords

        except Exception as e:
            self.logger.warning(f"Error cargando stopwords: {e}. Usando solo dominio.")
            return DOMAIN_STOPWORDS

    def tokenize(self, text: str) -> List[str]:
        """
        Tokeniza texto en palabras individuales.

        Args:
            text: Texto a tokenizar

        Returns:
            Lista de tokens
        """
        if not isinstance(text, str) or not text.strip():
            return []

        try:
            # Tokenizar usando NLTK
            tokens = word_tokenize(text, language='spanish')

            # Filtrar tokens por longitud
            tokens = [
                token for token in tokens
                if MIN_TOKEN_LENGTH <= len(token) <= MAX_TOKEN_LENGTH
            ]

            return tokens

        except Exception as e:
            self.logger.warning(f"Error en tokenización: {e}. Usando split simple.")
            # Fallback: split simple
            return [
                token for token in text.split()
                if MIN_TOKEN_LENGTH <= len(token) <= MAX_TOKEN_LENGTH
            ]

    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """
        Elimina stopwords de una lista de tokens.

        Args:
            tokens: Lista de tokens

        Returns:
            Lista de tokens sin stopwords
        """
        if not tokens:
            return []

        # Filtrar stopwords (case insensitive)
        filtered_tokens = [
            token for token in tokens
            if token.lower() not in self.stopwords
        ]

        return filtered_tokens

    def apply_stemming(self, tokens: List[str]) -> List[str]:
        """
        Aplica stemming a una lista de tokens.

        Args:
            tokens: Lista de tokens

        Returns:
            Lista de tokens con stemming aplicado
        """
        if not tokens or not self.stemmer:
            return tokens

        try:
            stemmed_tokens = [self.stemmer.stem(token) for token in tokens]
            return stemmed_tokens
        except Exception as e:
            self.logger.warning(f"Error en stemming: {e}")
            return tokens

    def process_text(
        self,
        text: str,
        remove_stopwords: bool = True,
        apply_stemming: bool = None
    ) -> List[str]:
        """
        Procesa texto completo: tokenización, stopwords y stemming.

        Args:
            text: Texto a procesar
            remove_stopwords: Si True, elimina stopwords
            apply_stemming: Si True, aplica stemming (None usa configuración por defecto)

        Returns:
            Lista de tokens procesados
        """
        # Tokenizar
        tokens = self.tokenize(text)

        if not tokens:
            return []

        # Eliminar stopwords
        if remove_stopwords:
            tokens = self.remove_stopwords(tokens)

        # Aplicar stemming
        if apply_stemming is None:
            apply_stemming = self.use_stemming

        if apply_stemming:
            tokens = self.apply_stemming(tokens)

        return tokens

    def process_text_to_string(
        self,
        text: str,
        remove_stopwords: bool = True,
        apply_stemming: bool = None
    ) -> str:
        """
        Procesa texto y devuelve una cadena con tokens unidos.

        Args:
            text: Texto a procesar
            remove_stopwords: Si True, elimina stopwords
            apply_stemming: Si True, aplica stemming

        Returns:
            String con tokens procesados unidos por espacios
        """
        tokens = self.process_text(text, remove_stopwords, apply_stemming)
        return " ".join(tokens)

    def process_dataframe_column(
        self,
        df: pd.DataFrame,
        column: str,
        output_column: Optional[str] = None,
        remove_stopwords: bool = True,
        apply_stemming: bool = None
    ) -> pd.DataFrame:
        """
        Procesa una columna completa del DataFrame.

        Args:
            df: DataFrame con los datos
            column: Nombre de la columna a procesar
            output_column: Nombre de la columna de salida (por defecto: column + '_tokenized')
            remove_stopwords: Si True, elimina stopwords
            apply_stemming: Si True, aplica stemming

        Returns:
            DataFrame con la columna procesada
        """
        if column not in df.columns:
            self.logger.warning(f"Columna '{column}' no encontrada en el DataFrame")
            return df

        if output_column is None:
            output_column = f"{column}_tokenized"

        self.logger.info(f"Tokenizando columna: {column} → {output_column}")

        # Procesar cada valor
        df[output_column] = df[column].apply(
            lambda x: self.process_text_to_string(
                x, remove_stopwords, apply_stemming
            )
        )

        # Contar valores procesados
        non_empty = df[output_column].notna() & (df[output_column] != "")
        count = non_empty.sum()

        self.logger.info(f"  → {count} valores tokenizados")

        return df
