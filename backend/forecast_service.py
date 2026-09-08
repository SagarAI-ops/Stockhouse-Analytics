from datetime import timedelta

import pandas as pd

from models import ForecastPoint, ForecastResponse, ForecastSeries


def get_forecast(
    df: pd.DataFrame,
    material: str = "All",
    days: int = 7,
) -> ForecastResponse:
    """Statistical stub: last rolling mean ± 1.5σ, held constant over the horizon."""
    horizon = max(1, min(int(days), 30))
    materials = (
        sorted(df["material_type"].dropna().unique().tolist())
        if material.lower() == "all"
        else [material]
    )
    series: list[ForecastSeries] = []
    for mat in materials:
        subset = df[df["material_type"] == mat] if mat else df
        series.append(_forecast_one(subset, mat, horizon))

    if not series:
        series.append(
            ForecastSeries(
                material=material,
                points=[
                    ForecastPoint(
                        date=pd.Timestamp.utcnow().strftime("%Y-%m-%d"),
                        predicted_tons=0.0,
                        lower_bound=0.0,
                        upper_bound=0.0,
                    )
                ],
            )
        )

    return ForecastResponse(series=series, horizon_days=horizon, material=material)


def _forecast_one(df: pd.DataFrame, material: str, days: int) -> ForecastSeries:
    if df.empty:
        today = pd.Timestamp.utcnow().strftime("%Y-%m-%d")
        return ForecastSeries(
            material=material,
            points=[
                ForecastPoint(
                    date=today,
                    predicted_tons=0.0,
                    lower_bound=0.0,
                    upper_bound=0.0,
                )
            ],
        )

    daily = (
        df.groupby("date")["actual_weight_kg"]
        .sum()
        .sort_index()
        / 1000.0
    )
    window = min(7, max(1, len(daily)))
    mean = float(daily.rolling(window=window, min_periods=1).mean().iloc[-1])
    std = float(daily.std(ddof=0)) if len(daily) > 1 else 0.0
    if pd.isna(std):
        std = 0.0
    lower = max(0.0, mean - 1.5 * std)
    upper = mean + 1.5 * std
    last_date = pd.to_datetime(daily.index[-1])

    points = []
    for offset in range(1, days + 1):
        points.append(
            ForecastPoint(
                date=(last_date + timedelta(days=offset)).strftime("%Y-%m-%d"),
                predicted_tons=round(mean, 2),
                lower_bound=round(lower, 2),
                upper_bound=round(upper, 2),
            )
        )
    return ForecastSeries(material=material, points=points)
