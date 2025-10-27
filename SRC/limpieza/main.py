"""
Pipeline de unificación de fuentes de datos nutricionales.
Carga datos de Alcampo y OpenFoodFacts y genera un JSON unificado.

Uso:
    python SRC/limpieza/main.py [--output-json PATH]
"""

import argparse
import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Ajuste del path para ejecución directa
if __name__ == "__main__":
    src_dir = Path(__file__).resolve().parent.parent
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

# Importaciones de módulos internos
from limpieza.config import (
    ALCAMPO_JSON, OPENFOOD_JSON, OUTPUT_JSON_UNIFIED,
    OUTPUT_CSV_PATH, ENCODING
)
from limpieza.data_loaders import load_json_file, save_json_file
from limpieza.transformers import unify_products_from_sources
from limpieza.dataframe_builder import flatten_to_dataframe


def step1_unify_sources():
    """Paso 1: Carga y unifica productos de todas las fuentes."""
    logger.info("="*60)
    logger.info("PASO 1: UNIFICACIÓN DE FUENTES DE DATOS")
    logger.info("="*60)

    # Validar archivos de entrada
    for path in [ALCAMPO_JSON, OPENFOOD_JSON]:
        if not path.exists():
            logger.error(f"Archivo no encontrado: {path}")
            sys.exit(1)

    # Cargar datos
    alcampo_data = load_json_file(ALCAMPO_JSON)
    openfood_data = load_json_file(OPENFOOD_JSON)

    # Unificar productos
    unified_products = unify_products_from_sources(alcampo_data, openfood_data)

    if not unified_products:
        logger.error("No se generaron productos unificados")
        sys.exit(1)

    logger.info(f"Productos unificados: {len(unified_products)}")
    return unified_products


def step2_save_unified_json(products, output_path):
    """Paso 2: Guarda productos unificados en formato JSON."""
    logger.info("="*60)
    logger.info("PASO 2: GUARDANDO JSON UNIFICADO")
    logger.info("="*60)

    success = save_json_file(products, output_path, encoding=ENCODING)

    if not success:
        logger.error(f"Error al guardar JSON en {output_path}")
        sys.exit(1)

    # Estadísticas
    valid_nutrition = sum(
        1 for p in products
        if p.get('valores_nutricionales_100_g') and
        any(v is not None for v in p['valores_nutricionales_100_g'].values())
    )
    logger.info(f"  - Con datos nutricionales: {valid_nutrition}/{len(products)}")

    with_price = sum(1 for p in products if p.get('precio_total'))
    logger.info(f"  - Con precio: {with_price}/{len(products)}")

    with_categories = sum(1 for p in products if p.get('categorias'))
    logger.info(f"  - Con categorías: {with_categories}/{len(products)}")


def step3_build_dataframe(products):
    """Paso 3: Convierte JSON unificado a DataFrame tabular."""
    return flatten_to_dataframe(products)


def step4_save_csv(df, output_path):
    """Paso 4: Guarda DataFrame básico desanidado en CSV."""
    logger.info("="*60)
    logger.info("PASO 4: GUARDANDO CSV BÁSICO DESANIDADO")
    logger.info("="*60)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding=ENCODING)
    logger.info(f"CSV guardado: {output_path}")
    logger.info(f"  - Total productos: {len(df)}")
    logger.info(f"  - Total columnas: {len(df.columns)}")
    logger.info(f"  - Columnas: {', '.join(df.columns)}")


def main():
    """Pipeline de unificación: carga fuentes y genera JSON unificado."""
    parser = argparse.ArgumentParser(
        description='Unificación de datos nutricionales de múltiples fuentes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Ejecutar con ruta por defecto
  python SRC/limpieza/main.py

  # Especificar ruta personalizada
  python SRC/limpieza/main.py --output-json Data/custom.json
        """
    )

    parser.add_argument('--output-json', type=str, default=str(OUTPUT_JSON_UNIFIED),
                       help=f'Ruta del JSON unificado (default: {OUTPUT_JSON_UNIFIED})')

    args = parser.parse_args()

    try:
        logger.info("="*60)
        logger.info("INICIANDO UNIFICACIÓN DE FUENTES DE DATOS")
        logger.info("="*60)
        logger.info(f"Fuentes de entrada:")
        logger.info(f"  - Alcampo: {ALCAMPO_JSON}")
        logger.info(f"  - OpenFoodFacts: {OPENFOOD_JSON}")
        logger.info(f"Salidas:")
        logger.info(f"  - JSON Unificado: {args.output_json}")
        logger.info(f"  - CSV Desanidado: {OUTPUT_CSV_PATH}")
        logger.info("")

        # Ejecutar pipeline de unificación y limpieza
        unified_products = step1_unify_sources()
        step2_save_unified_json(unified_products, Path(args.output_json))

        # Generar CSV básico desanidado
        df_basic = step3_build_dataframe(unified_products)
        step4_save_csv(df_basic, OUTPUT_CSV_PATH)

        # Resumen final
        logger.info("="*60)
        logger.info("LIMPIEZA Y UNIFICACIÓN COMPLETADAS EXITOSAMENTE")
        logger.info("="*60)
        logger.info(f"Archivos generados:")
        logger.info(f"  - JSON Unificado: {args.output_json}")
        logger.info(f"  - CSV Desanidado: {OUTPUT_CSV_PATH}")
        logger.info(f"  - Total productos: {len(unified_products)}")
        logger.info("="*60)

    except Exception as e:
        logger.error(f"Error durante ejecución del pipeline: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
