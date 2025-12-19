import pandas as pd

from src.stats.recorder import RunningStats


def normalize_batch(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza tipos y deja el batch listo para cargar y calcular stats."""
    if df.empty:
        return df

    # Convertir price a numérico, valores inválidos como NaN
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    # Eliminar filas sin price (estas no nos sirven para las estadisticas)
    #df = df.dropna(subset=["price"])

    df["user_id"] = df["user_id"].astype(int)

    return df


def update_stats(running_stats: RunningStats, df: pd.DataFrame) -> RunningStats:
    """Actualiza estadísticas incrementales con un batch ya normalizado."""
    running_stats.update_from_batch(df)
    return running_stats
