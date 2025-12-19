from src.pipeline import run_full_pipeline, run_validation_step
from src.db.repository import init_db
from src.logging import setup_logging, get_logger

ZIP_PATH = "./data/data-prueba-data-engineer.zip"
UNZIP_DIR = "./data/"
BATCH_SIZE = 10


def main():
    """
    Punto de entrada principal del pipeline de la prueba técnica.

    Flujo:
    1. Inicializa la base de datos (crea tablas si no existen).
    2. Ejecuta el pipeline sobre 2012-1.csv .. 2012-5.csv.
    3. Imprime estadísticas en memoria y en base de datos.
    4. Ejecuta el pipeline sobre validation.csv.
    5. Vuelve a imprimir estadísticas en memoria y en base de datos.
    """
    # Configure logging
    setup_logging()
    logger = get_logger("data-pipeline.main")

    init_db()

    logger.info("=== Carga inicial (2012-1.csv .. 2012-5.csv) ===")
    running_stats, db_stats_before = run_full_pipeline(
        zip_path=ZIP_PATH,
        input_dir=UNZIP_DIR,
        batch_size=BATCH_SIZE,
    )

    logger.info("Estadísticas en ejecución (memoria) después de 2012-1..5: %s", running_stats.as_dict())
    logger.info("Estadísticas en base de datos después de 2012-1..5: %s", db_stats_before)

    logger.info("=== Paso de validación (validation.csv) ===")
    running_stats_after, db_stats_after = run_validation_step(
        input_dir=UNZIP_DIR,
        batch_size=BATCH_SIZE,
        running_stats=running_stats,
    )

    logger.info("Estadísticas en ejecución (memoria) después de validation.csv: %s", running_stats_after.as_dict())
    logger.info("Estadísticas en base de datos después de validation.csv: %s", db_stats_after)


if __name__ == "__main__":
    main()
