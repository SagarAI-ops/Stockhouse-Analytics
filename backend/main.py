"""
Blast Furnace Stockhouse Analytics – FastAPI Backend
"""

from typing import Optional
from datetime import datetime

import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from database import get_dataframe
from analytics_engine import (
    get_kpis,
    get_precision_stats,
    get_cycle_times,
    get_aggregations,
    get_shift_report,
)
from models import (
    DashboardResponse,
    FilterOptions,
)

app = FastAPI(
    title="BF Stockout Analytics API",
    version="1.0.0",
    description="Blast Furnace Stockhouse Stockout Analytics Dashboard – Phase 1",
)

# ---------------------------------------------------------------------------
# CORS – allow Vite dev server
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _filter_df(
    df: pd.DataFrame,
    start_date: Optional[str],
    end_date: Optional[str],
    shift: Optional[str],
    hopper_id: Optional[str],
) -> pd.DataFrame:
    """Apply query-parameter filters to the master DataFrame."""
    mask = pd.Series([True] * len(df), index=df.index)

    if start_date:
        mask &= df["date"] >= start_date
    if end_date:
        mask &= df["date"] <= end_date
    if shift and shift.lower() != "all":
        mask &= df["shift"] == shift
    if hopper_id and hopper_id.lower() != "all":
        mask &= df["hopper_id"] == hopper_id

    return df.loc[mask]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/filters", response_model=FilterOptions)
def filters():
    df = get_dataframe()
    return FilterOptions(
        hoppers=sorted(df["hopper_id"].unique().tolist()),
        shifts=sorted(df["shift"].unique().tolist()),
        materials=sorted(df["material_type"].unique().tolist()),
        date_min=df["date"].min(),
        date_max=df["date"].max(),
    )


@app.get("/api/dashboard_data", response_model=DashboardResponse)
def dashboard_data(
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    shift: Optional[str] = Query(None, description="A / B / C or All"),
    hopper_id: Optional[str] = Query(None, description="H1 / H2 / H3 / H4 or All"),
):
    df = get_dataframe()
    filtered = _filter_df(df, start_date, end_date, shift, hopper_id)

    return DashboardResponse(
        kpis=get_kpis(filtered),
        precision=get_precision_stats(filtered),
        cycle_times=get_cycle_times(filtered),
        aggregations=get_aggregations(filtered),
        shift_report=get_shift_report(filtered),
    )
