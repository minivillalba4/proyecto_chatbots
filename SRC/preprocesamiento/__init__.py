"""
Módulo de preprocesamiento de datos de productos alimenticios.
Incluye limpieza, normalización numérica, validación, feature engineering
y normalización de texto para NLP.
"""

from .data_loader import DataLoader
from .cleaner import DataCleaner
from .normalizer import DataNormalizer
from .validator import DataValidator
from .feature_engineer import FeatureEngineer
from .text_cleaner import TextCleaner
from .tokenizer import TextTokenizer
from .text_normalizer import TextNormalizer
from .main import PreprocessingPipeline

__version__ = "0.2.0"

__all__ = [
    "DataLoader",
    "DataCleaner",
    "DataNormalizer",
    "DataValidator",
    "FeatureEngineer",
    "TextCleaner",
    "TextTokenizer",
    "TextNormalizer",
    "PreprocessingPipeline"
]
