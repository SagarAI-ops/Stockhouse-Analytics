"""
Analytics Engine – Pandas-based computations for the stockout dashboard.
"""

from typing import List, Dict, Any

import numpy as np
import pandas as pd

from models import (
    KpiResponse,
    PrecisionPoint,
    PrecisionStatsResponse,
    CycleTimeEntry,
    CycleTimeResponse,
    AggregationEntry,
    AggregationResponse,
    ShiftReportRow,
    ShiftReportResponse,
)


# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------

def get_kpis(df: pd.DataFrame) -> KpiResponse:
    if df.empty:
        return KpiResponse(
            total_tonnage=0.0,
            total_batches=0,
            avg_precision_pct=0.0,
            avg_cycle_time_sec=0.0,
        )

    total_tonnage = df["actual_weight_kg"].sum() / 1000.0
    total_batches = len(df)
    avg_precision_pct = float(df["deviation_pct"].mean())
    avg_cycle_time_sec = float(df["total_cycle_time"].mean())

    return KpiResponse(
        total_tonnage=round(total_tonnage, 2),
        total_batches=total_batches,
        avg_precision_pct=round(avg_precision_pct, 4),
        avg_cycle_time_sec=round(avg_cycle_time_sec, 2),
    )


# ---------------------------------------------------------------------------
# Precision / SPC
# ---------------------------------------------------------------------------

def get_precision_stats(df: pd.DataFrame) -> PrecisionStatsResponse:
    if df.empty:
        return PrecisionStatsResponse(
            time_series=[], pass_count=0, fail_count=0, pass_rate_pct=0.0
        )

    ucl, lcl = 0.5, -0.5
    within = (df["deviation_pct"] >= lcl) & (df["deviation_pct"] <= ucl)
    pass_count = int(within.sum())
    fail_count = len(df) - pass_count

    sorted_df = df.sort_values("timestamp_start")

    time_series: List[PrecisionPoint] = []
    for _, row in sorted_df.iterrows():
        time_series.append(
            PrecisionPoint(
                batch_id=row["batch_id"],
                timestamp=row["timestamp_start"],
                deviation_kg=round(float(row["deviation_kg"]), 2),
                deviation_pct=round(float(row["deviation_pct"]), 4),
                within_limits=bool(lcl <= row["deviation_pct"] <= ucl),
            )
        )

    return PrecisionStatsResponse(
        time_series=time_series,
        pass_count=pass_count,
        fail_count=fail_count,
        pass_rate_pct=round((pass_count / len(df)) * 100, 2),
    )


# ---------------------------------------------------------------------------
# Cycle times
# ---------------------------------------------------------------------------

def get_cycle_times(df: pd.DataFrame) -> CycleTimeResponse:
    if df.empty:
        return CycleTimeResponse(by_hopper=[], by_shift=[])

    def _aggregate(grouped: pd.DataFrame) -> List[CycleTimeEntry]:
        entries: List[CycleTimeEntry] = []
        for key, grp in grouped:
            entries.append(
                CycleTimeEntry(
                    group_key=str(key),
                    avg_fill_time_sec=round(float(grp["fill_time_sec"].mean()), 2),
                    avg_discharge_time_sec=round(float(grp["discharge_time_sec"].mean()), 2),
                    avg_total_cycle_time=round(float(grp["total_cycle_time"].mean()), 2),
                )
            )
        return entries

    by_hopper = _aggregate(df.groupby("hopper_id"))
    by_shift = _aggregate(df.groupby("shift"))

    return CycleTimeResponse(by_hopper=by_hopper, by_shift=by_shift)


# ---------------------------------------------------------------------------
# Aggregations
# ---------------------------------------------------------------------------

def get_aggregations(df: pd.DataFrame) -> AggregationResponse:
    if df.empty:
        return AggregationResponse(by_shift=[], by_material=[], by_day=[])

    def _agg_group(grouped: pd.DataFrame) -> List[AggregationEntry]:
        entries: List[AggregationEntry] = []
        for key, grp in grouped:
            total_kg = float(grp["actual_weight_kg"].sum())
            entries.append(
                AggregationEntry(
                    group_key=str(key),
                    total_weight_kg=round(total_kg, 2),
                    total_weight_tons=round(total_kg / 1000.0, 2),
                    batch_count=len(grp),
                )
            )
        return entries

    return AggregationResponse(
        by_shift=_agg_group(df.groupby("shift")),
        by_material=_agg_group(df.groupby("material_type")),
        by_day=_agg_group(df.groupby("date")),
    )


# ---------------------------------------------------------------------------
# Shift report (tabular)
# ---------------------------------------------------------------------------

def get_shift_report(df: pd.DataFrame) -> ShiftReportResponse:
    if df.empty:
        return ShiftReportResponse(rows=[], total_rows=0)

    sorted_df = df.sort_values("timestamp_start", ascending=False)

    rows: List[ShiftReportRow] = []
    for _, r in sorted_df.iterrows():
        rows.append(
            ShiftReportRow(
                batch_id=r["batch_id"],
                timestamp=r["timestamp_start"].isoformat(),
                shift=r["shift"],
                hopper_id=r["hopper_id"],
                material_type=r["material_type"],
                target_weight_kg=round(float(r["target_weight_kg"]), 1),
                actual_weight_kg=round(float(r["actual_weight_kg"]), 1),
                deviation_kg=round(float(r["deviation_kg"]), 2),
                deviation_pct=round(float(r["deviation_pct"]), 4),
                cycle_time_sec=int(r["total_cycle_time"]),
            )
        )

    return ShiftReportResponse(rows=rows, total_rows=len(rows))
