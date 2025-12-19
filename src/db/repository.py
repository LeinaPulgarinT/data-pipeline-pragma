from typing import Dict
import pandas as pd
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    create_engine,
    func,
    Boolean,
    UniqueConstraint
    
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session as SASession

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()


class Record(Base):
    """
    Tabla principal donde se almacenan todos los eventos del CSV.
    """
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_date = Column(Date, nullable=False)
    price = Column(Integer, nullable=True)
    price_imputed = Column(Boolean, nullable=False, default=False)
    user_id = Column(Integer, nullable=False)
    source_file = Column(String(50), nullable=False)

    __table_args__ = (
        UniqueConstraint("event_date", "user_id", "price", name="uq_event"),
    )


def _get_database_url() -> str:
    user = "pragma"
    password = "pragma123"
    host = "localhost"
    port = "5432"
    db = "admin_db"
    # todo: mirar si agrego esto en un .env

    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


ENGINE = create_engine(_get_database_url())
SessionLocal = sessionmaker(bind=ENGINE)


def init_db() -> None:
    Base.metadata.create_all(ENGINE)


def get_session() -> SASession:
    return SessionLocal()

def insert_records(df: pd.DataFrame, source_file: str) -> tuple[int, list]:
    if df.empty:
        return 0, pd.DataFrame()

    df["price_imputed"] = df["price"].isna()
    impute_value = df["price"].median()
    df["price"] = df["price"].fillna(impute_value)
    
    # Construcción de records para SQLAlchemy
    records = []
    for _, row in df.iterrows():
        records.append(
            {
                "event_date": row["event_date"],
                "user_id": int(row["user_id"]),
                "price": (int(row["price"])),
                "price_imputed": bool(row["price_imputed"]),
                "source_file": source_file,
            }
        )

    stmt = (
        insert(Record)
        .values(records)
        .on_conflict_do_nothing(
            index_elements=["event_date", "user_id", "price"]
        )
        .returning(
            Record.event_date,
            Record.user_id,
            Record.price,
        )
    )

    session = get_session()
    try:
        result = session.execute(stmt)

        # Filas realmente insertadas
        inserted_rows = result.fetchall()
        inserted_count = len(inserted_rows)

        # skipped = len(records) - inserted_count
        # Note: intentionally not logging skipped records to avoid noisy output

        session.commit()

        return inserted_count, inserted_rows

    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()


def get_aggregate_statistics() -> Dict[str, float]:
    """
    Obtiene estadísticas globales recorriendo toda la tabla.
    Se usa SOLO para validación final.
    """
    session = get_session()
    try:
        total_rows = session.query(func.count(Record.id)).scalar() or 0
        avg_price = session.query(func.avg(Record.price)).scalar()
        min_price = session.query(func.min(Record.price)).scalar()
        max_price = session.query(func.max(Record.price)).scalar()
    finally:
        session.close()

    return {
        "row_count": int(total_rows),
        "average_price": float(avg_price) if avg_price is not None else 0.0,
        "min_price": int(min_price) if min_price is not None else 0,
        "max_price": int(max_price) if max_price is not None else 0,
    }
