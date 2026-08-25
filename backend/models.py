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
