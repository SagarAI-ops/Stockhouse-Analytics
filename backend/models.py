from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class BatchRecord(BaseModel):
    batch_id: str
    timestamp_start: datetime
    timestamp_fill_end: datetime
    timestamp_discharge_end: datetime
    shift: str
    hopper_id: str
    material_type: str
    target_weight_kg: float
    actual_weight_kg: float
    fill_time_sec: int
    discharge_time_sec: int


class KpiResponse(BaseModel):
    total_tonnage: float = Field(description="Total material charged in metric tons")
    total_batches: int = Field(description="Total number of batches completed")
    avg_precision_pct: float = Field(description="Average deviation percentage")
    avg_cycle_time_sec: float = Field(description="Average total cycle time in seconds")


class PrecisionPoint(BaseModel):
    batch_id: str
    timestamp: datetime
    deviation_kg: float
    deviation_pct: float
    within_limits: bool


class PrecisionStatsResponse(BaseModel):
    time_series: List[PrecisionPoint]
    pass_count: int
    fail_count: int
    pass_rate_pct: float
    ucl: float = 0.5
    lcl: float = -0.5


class CycleTimeEntry(BaseModel):
    group_key: str
    avg_fill_time_sec: float
    avg_discharge_time_sec: float
    avg_total_cycle_time: float


class CycleTimeResponse(BaseModel):
    by_hopper: List[CycleTimeEntry]
    by_shift: List[CycleTimeEntry]


class AggregationEntry(BaseModel):
    group_key: str
    total_weight_kg: float
    total_weight_tons: float
    batch_count: int


class AggregationResponse(BaseModel):
    by_shift: List[AggregationEntry]
    by_material: List[AggregationEntry]
    by_day: List[AggregationEntry]


class ShiftReportRow(BaseModel):
    batch_id: str
    timestamp: str
    shift: str
    hopper_id: str
    material_type: str
    target_weight_kg: float
    actual_weight_kg: float
    deviation_kg: float
    deviation_pct: float
    cycle_time_sec: int


class ShiftReportResponse(BaseModel):
    rows: List[ShiftReportRow]
    total_rows: int


class DashboardResponse(BaseModel):
    kpis: KpiResponse
    precision: PrecisionStatsResponse
    cycle_times: CycleTimeResponse
    aggregations: AggregationResponse
    shift_report: ShiftReportResponse


class FilterOptions(BaseModel):
    hoppers: List[str]
    shifts: List[str]
    materials: List[str]
    date_min: str
    date_max: str

# ---------------------------------------------------------------------------
# Chat models (new)
# ---------------------------------------------------------------------------

class ChatMessage(BaseModel):
    role: str = Field(description="'user' or 'assistant'")
    content: str = Field(description="Message text")

class ChatRequest(BaseModel):
    message: str = Field(description="User's latest message")
    history: List[ChatMessage] = Field(description="Chat history, oldest first")

class ChatResponse(BaseModel):
    role: str = Field(default="assistant", description="Always 'assistant'")
    content: str = Field(description="Assistant's reply")


class ForecastPoint(BaseModel):
    date: str
    predicted_tons: float
    lower_bound: float
    upper_bound: float


class ForecastSeries(BaseModel):
    material: str
    points: List[ForecastPoint]


class ForecastResponse(BaseModel):
    series: List[ForecastSeries]
    horizon_days: int
    material: str


class Alert(BaseModel):
    severity: str = Field(description="'warning' or 'critical'")
    hopper_id: str
    message: str
    batch_id: str
    timestamp: str


class AnomalyEntry(BaseModel):
    batch_id: str
    timestamp: str
    hopper_id: str
    material_type: str
    deviation_pct: float
    cycle_time_sec: int
    reason: str


class AnomalyResponse(BaseModel):
    items: List[AnomalyEntry]
    total: int


class TrendPoint(BaseModel):
    date: str
    actual_tons: float
    moving_avg_tons: float


class TrendResponse(BaseModel):
    points: List[TrendPoint]
    window_days: int
