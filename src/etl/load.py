import pandas as pd

from src.db.repository import insert_records


def load_batch(df: pd.DataFrame, source_file: str) -> tuple:
    """Carga un batch de datos normalizados en la base de datos."""
    inserted_count, inserted_rows = insert_records(df, source_file)

    if inserted_count == 0:
        return 0, pd.DataFrame()

    inserted_df = pd.DataFrame(
        inserted_rows,
        columns=["event_date", "user_id", "price"]
    )

    return inserted_count, inserted_df