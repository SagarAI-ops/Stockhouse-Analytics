"""
Database module – loads and caches the CSV into a Pandas DataFrame.
"""

import os
from typing import Optional

import pandas as pd

_CSV_PATH: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dummy_data.csv")

_df_cache: Optional[pd.DataFrame] = None


def load_data(force_reload: bool = False) -> pd.DataFrame:
    """Load dummy_data.csv into a DataFrame, with in-memory caching."""
    global _df_cache
    if _df_cache is not None and not force_reload:
        return _df_cache

    if not os.path.exists(_CSV_PATH):
        raise FileNotFoundError(
            f"dummy_data.csv not found at {_CSV_PATH}. "
            "Run `python data_generator.py` first."
        )

    df = pd.read_csv(_CSV_PATH, parse_dates=[
        "timestamp_start",
        "timestamp_fill_end",
        "timestamp_discharge_end",
    ])

    # Derived columns for convenience
    df["deviation_kg"] = df["actual_weight_kg"] - df["target_weight_kg"]
    df["deviation_pct"] = (df["deviation_kg"] / df["target_weight_kg"]) * 100.0
    df["total_cycle_time"] = df["fill_time_sec"] + df["discharge_time_sec"]
    df["date"] = df["timestamp_start"].dt.strftime("%Y-%m-%d")

    _df_cache = df
    return df


def get_dataframe() -> pd.DataFrame:
    """Public accessor that ensures data is loaded."""
    return load_data()
