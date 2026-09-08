"""
Blast Furnace Stockhouse Analytics – FastAPI Backend
"""

from pathlib import Path
from typing import List, Optional

import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

_BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(_BACKEND_DIR.parent / ".env")
load_dotenv(_BACKEND_DIR / ".env")

from database import get_dataframe
from analytics_engine import (
    get_kpis,
    get_precision_stats,
    get_cycle_times,
    get_aggregations,
    get_shift_report,
    get_anomalies,
    get_trend,
)
from models import (
    DashboardResponse,
    FilterOptions,
    ChatRequest,
    ChatResponse,
    ForecastResponse,
    Alert,
    AnomalyResponse,
    TrendResponse,
)
from llm_service import GeminiService, LLMNotConfigured
from chat_service import ChatService
from forecast_service import get_forecast
from alert_service import get_alerts

app = FastAPI(
    title="BF Stockout Analytics API",
    version="1.0.0",
    description="Blast Furnace Stockhouse Stockout Analytics Dashboard",
)

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

llm_service = GeminiService()
chat_service = ChatService(llm_service)


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


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "BF Stockout Analytics API",
        "health": "/api/health",
        "docs": "/docs",
    }


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    if not llm_service.is_configured:
        raise HTTPException(status_code=503, detail="LLM not configured")
    try:
        response_content = chat_service.handle_message(
            request.message,
            request.history,
            get_dataframe(),
        )
    except LLMNotConfigured:
        raise HTTPException(status_code=503, detail="LLM not configured") from None
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM request failed: {exc}") from exc
    return ChatResponse(content=response_content)


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


@app.get("/api/forecast", response_model=ForecastResponse)
def forecast(
    material: str = Query("All"),
    days: int = Query(7, ge=1, le=30),
):
    return get_forecast(get_dataframe(), material=material, days=days)


@app.get("/api/alerts", response_model=List[Alert])
def alerts():
    return get_alerts(get_dataframe())


@app.get("/api/anomalies", response_model=AnomalyResponse)
def anomalies():
    return get_anomalies(get_dataframe())


@app.get("/api/trend", response_model=TrendResponse)
def trend(window_days: int = Query(7, ge=1, le=60)):
    return get_trend(get_dataframe(), window_days=window_days)
