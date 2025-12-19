from dataclasses import dataclass, asdict
from typing import Dict

import pandas as pd


@dataclass
class RunningStats:
    """
    Estadísticas incrementales en memoria.

    Se actualizan a medida que se insertan nuevos micro-batches, sin
    necesidad de volver a leer toda la base de datos.
    """

    row_count: int = 0
    sum_price: float = 0.0
    min_price: float | None = None
    max_price: float | None = None

    def update_from_batch(self, df: pd.DataFrame) -> None:
        """
        Actualiza las estadísticas con un nuevo micro-batch (DataFrame).
        Se asume que el DataFrame tiene una columna `price`.
        """
        if df.empty:
            return

        prices = df["price"]

        batch_count = len(prices)
        batch_sum = float(prices.sum())
        batch_min = float(prices.min())
        batch_max = float(prices.max())

        # Actualizar conteo y suma
        self.row_count += batch_count
        self.sum_price += batch_sum

        # Actualizar min y max globales
        if self.min_price is None:
            self.min_price = batch_min
        else:
            self.min_price = min(self.min_price, batch_min)

        if self.max_price is None:
            self.max_price = batch_max
        else:
            self.max_price = max(self.max_price, batch_max)

    @property
    def average_price(self) -> float:
        if self.row_count == 0:
            return 0.0
        return self.sum_price / self.row_count

    def as_dict(self) -> Dict[str, float]:
        """
        Devuelve un diccionario listo para imprimir o registrar.
        """
        return {
            "row_count": self.row_count,
            "sum_price": self.sum_price,
            "min_price": self.min_price if self.min_price is not None else 0.0,
            "max_price": self.max_price if self.max_price is not None else 0.0,
            "average_price": self.average_price,
        }
