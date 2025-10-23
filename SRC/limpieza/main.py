"""
Script principal para limpieza y preparación de datos nutricionales para ML.
"""

import argparse
import sys
import logging
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any

# Ajuste del path para ejecución directa
if __name__ == "__main__":
    src_dir = Path(__file__).resolve().parent.parent
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

# Importaciones de módulos de limpieza
from limpieza.config import ALCAMPO_JSON, OPENFOOD_JSON, OUTPUT_CSV_PATH, ENCODING
from limpieza.constants import NUTRITION_COLS
from limpieza.load_alcampo import cargar_alcampo
from limpieza.load_openfood import cargar_openfoodfacts
from limpieza.consolidate_nutrition import consolidate_nutrition_columns
from limpieza.consolidate_features import consolidate_additional_features
from limpieza.score_nutricional import calculate_nutriscore
from limpieza.filter_data import filter_ml_ready_products
from limpieza.impute_data import impute_missing_values

logger = logging.getLogger(__name__)


def load_products(alcampo_path: Path, openfood_path: Path) -> List[Dict[str, Any]]:
    """Carga productos de ambas fuentes y los concatena."""
    logger.info("="*60)
    logger.info("INICIANDO CARGA DE PRODUCTOS")
    logger.info("="*60)
    
    alcampo_products = cargar_alcampo(alcampo_path)
    openfood_products = cargar_openfoodfacts(openfood_path)
    
    total = alcampo_products + openfood_products
    
    logger.info("="*60)
    logger.info(f"RESUMEN DE CARGA: {len(total)} productos totales")
    logger.info(f"  - Alcampo: {len(alcampo_products)}")
    logger.info(f"  - OpenFoodFacts: {len(openfood_products)}")
    logger.info("="*60)
    
    return total


def prepare_ml_features_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """Pipeline completo de ingeniería de features."""
    logger.info("="*60)
    logger.info("PIPELINE DE INGENIERÍA DE FEATURES")
    logger.info("="*60)
    
    if df.empty:
        logger.warning("DataFrame vacío recibido")
        return df
    
    if 'source' not in df.columns:
        logger.error(f"Falta columna 'source'. Columnas: {df.columns.tolist()}")
        raise ValueError("DataFrame debe contener columna 'source'")
    
    logger.info(f"Productos de entrada: {len(df)}")
    
    # 1. Consolidación
    df = consolidate_nutrition_columns(df)
    df = consolidate_additional_features(df)
    
    # 2. Imputación y filtrado
    df = impute_missing_values(df)
    df = filter_ml_ready_products(df)
    
    # 3. Cálculo de score
    df['score_nutricional'] = df.apply(calculate_nutriscore, axis=1)
    logger.info(f"Score nutricional - Media: {df['score_nutricional'].mean():.2f}, "
                f"Mediana: {df['score_nutricional'].median():.2f}")
    
    # 4. Selección de columnas finales
    ml_cols = ['source', 'product_name', 'brand', 'weight_volume_clean', 'country'] + \
              NUTRITION_COLS + ['score_nutricional']
              
    existing_cols = [col for col in ml_cols if col in df.columns]
    final_df = df[existing_cols].copy()
    
    logger.info(f"Dataset ML final: {final_df.shape}")
    return final_df


def save_to_csv(df: pd.DataFrame, output_path: str) -> str:
    """Guarda DataFrame a CSV."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding=ENCODING)
    logger.info(f"Datos guardados en: {output_path}")
    return str(output_path)


def print_summary(df: pd.DataFrame, output_path: str) -> None:
    """Imprime resumen del procesamiento."""
    logger.info("="*60)
    logger.info("RESUMEN FINAL")
    logger.info("="*60)
    logger.info(f"Total productos procesados: {len(df)}")
    logger.info(f"Distribución por fuente:")
    for source, count in df['source'].value_counts().items():
        logger.info(f"  - {source}: {count}")
    
    logger.info(f"Columnas generadas: {len(df.columns)}")
    logger.info(f"Archivo de salida: {output_path}")
    logger.info("="*60)


def main():
    """Función principal de ejecución del pipeline."""
    parser = argparse.ArgumentParser(
        description='Limpieza y preparación de datos nutricionales para ML.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--alcampo', type=str, default=str(ALCAMPO_JSON),
                        help=f'Ruta al archivo Alcampo JSON (default: {ALCAMPO_JSON})')
    parser.add_argument('--openfood', type=str, default=str(OPENFOOD_JSON),
                        help=f'Ruta al archivo OpenFoodFacts JSON (default: {OPENFOOD_JSON})')
    parser.add_argument('--output', type=str, default=str(OUTPUT_CSV_PATH),
                        help=f'Ruta del archivo CSV de salida (default: {OUTPUT_CSV_PATH})')
    
    args = parser.parse_args()
    
    # Validar archivos de entrada
    for path in [args.alcampo, args.openfood]:
        if not Path(path).exists():
            logger.error(f"Archivo no encontrado: {path}")
            sys.exit(1)
            
    logger.info("="*60)
    logger.info("INICIO DEL PIPELINE DE LIMPIEZA")
    logger.info("="*60)
    logger.info(f"Alcampo: {args.alcampo}")
    logger.info(f"OpenFoodFacts: {args.openfood}")
    logger.info(f"Salida: {args.output}")
    
    try:
        # 1. Cargar datos
        productos_cargados = load_products(Path(args.alcampo), Path(args.openfood))
        
        if not productos_cargados:
            logger.error("No se cargaron productos. Verifica los archivos de entrada.")
            sys.exit(1)
        
        df = pd.DataFrame(productos_cargados)
        logger.info(f"Cargados {len(df)} productos de {df['source'].nunique()} fuentes")
        
        # 2. Ingeniería de features y limpieza
        df_ml = prepare_ml_features_pipeline(df)
        
        # 3. Guardar resultados
        output_path = save_to_csv(df_ml, args.output)
        
        # 4. Resumen
        print_summary(df_ml, output_path)
        
        logger.info("PROCESAMIENTO COMPLETADO EXITOSAMENTE")
        
    except Exception as e:
        logger.error(f"Error durante ejecución: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
