import os
import zipfile
from typing import Generator, List, Tuple

import pandas as pd


def ensure_unzipped(zip_path: str, extract_dir: str) -> None:
    """Descomprime el ZIP con los CSV si el directorio de destino está vacío."""
    if not os.path.exists(zip_path):
        raise FileNotFoundError(
            f"No se encontró el archivo ZIP de datos en: {zip_path}"
        )

    os.makedirs(extract_dir, exist_ok=True)

    existing_csvs = [f for f in os.listdir(extract_dir) if f.endswith(".csv")]
    if existing_csvs:
        return

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_dir)


def list_csv_files(directory: str) -> List[str]:
    """Lista los archivos CSV en un directorio, ordenados por nombre."""
    files = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.endswith(".csv")
    ]
    return sorted(files)


def split_training_and_validation(input_dir: str) -> Tuple[List[str], List[str]]:
    """Separa archivos de entrenamiento de validation.csv."""
    all_files = list_csv_files(input_dir)
    training = [f for f in all_files if not f.endswith("validation.csv")]
    validation = [f for f in all_files if f.endswith("validation.csv")]
    return training, validation


def read_csv_file_in_micro_batches(
    file_path: str, batch_size: int = 10
) -> Generator[pd.DataFrame, None, None]:
    """Lee un archivo CSV en microbatches usando pandas."""
    for chunk in pd.read_csv(file_path, chunksize=batch_size):
        # renombrar columna timestamp a event_date
        chunk = chunk.rename(columns={"timestamp": "event_date"})
        yield chunk

