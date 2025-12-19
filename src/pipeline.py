import time
from typing import List, Tuple

from src.db.repository import get_aggregate_statistics
from src.logging import get_logger
from src.stats.recorder import RunningStats
from src.etl.extract import (
    ensure_unzipped,
    split_training_and_validation,
    read_csv_file_in_micro_batches,
)
from src.etl.transform import normalize_batch, update_stats
from src.etl.load import load_batch


def process_files(
    files: List[str],
    batch_size: int,
    running_stats: RunningStats,
) -> None:
    logger = get_logger("data-pipeline.pipeline")

    for file_path in files:
        filename = file_path.split("/")[-1]
        logger.info("Procesando archivo: %s", filename)

        start_time = time.perf_counter()

        rows_read = 0
        rows_inserted = 0

        for batch_df in read_csv_file_in_micro_batches(file_path, batch_size):
            rows_read += len(batch_df)

            batch_df = normalize_batch(batch_df)
            inserted_count, inserted_rows = load_batch(batch_df, filename)

            rows_inserted += inserted_count

            if inserted_count > 0:
                inserted_rows = inserted_rows.dropna(subset=["price"])
                update_stats(running_stats, inserted_rows)

        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        rows_skipped = rows_read - rows_inserted

        logger.info(
            "Archivo %s | leídas=%d | insertadas=%d | ignoradas=%d | tiempo=%d ms",
            filename,
            rows_read,
            rows_inserted,
            rows_skipped,
            elapsed_ms,
        )

def run_full_pipeline(
    zip_path: str,
    input_dir: str,
    batch_size: int,
) -> Tuple[RunningStats, dict]:
    """
    Ejecuta el pipeline completo para los 5 archivos iniciales:
    - Descomprime el ZIP si es necesario.
    - Carga 2012-1.csv .. 2012-5.csv en micro-batches.
    - Actualiza estadísticas incrementales.
    - Devuelve las estadísticas en memoria y las estadísticas agregadas en DB.
    """
    ensure_unzipped(zip_path, input_dir)

    training_files, validation_files = split_training_and_validation(input_dir)
    if not training_files:
        raise RuntimeError(
            f"No se encontraron archivos CSV de entrenamiento en {input_dir}"
        )

    running_stats = RunningStats()
    process_files(training_files, batch_size, running_stats)

    db_stats = get_aggregate_statistics()
    return running_stats, db_stats


def run_validation_step(
    input_dir: str,
    batch_size: int,
    running_stats: RunningStats,
) -> Tuple[RunningStats, dict]:
    """
    Ejecuta el paso de validación:
    - Procesa únicamente validation.csv (si existe).
    - Actualiza las estadísticas incrementales existentes.
    - Devuelve las nuevas estadísticas en memoria y las de la base de datos.
    """
    _, validation_files = split_training_and_validation(input_dir)
    if not validation_files:
        raise RuntimeError(
            f"No se encontró validation.csv en el directorio {input_dir}"
        )

    process_files(validation_files, batch_size, running_stats)
    db_stats = get_aggregate_statistics()
    return running_stats, db_stats
