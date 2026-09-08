// TypeScript interfaces mirroring Pydantic backend models

export interface KpiResponse {
  total_tonnage: number;
  total_batches: number;
  avg_precision_pct: number;
  avg_cycle_time_sec: number;
}

export interface PrecisionPoint {
  batch_id: string;
  timestamp: string;
  deviation_kg: number;
  deviation_pct: number;
  within_limits: boolean;
}

export interface PrecisionStatsResponse {
  time_series: PrecisionPoint[];
  pass_count: number;
  fail_count: number;
  pass_rate_pct: number;
  ucl: number;
  lcl: number;
}

export interface CycleTimeEntry {
  group_key: string;
  avg_fill_time_sec: number;
  avg_discharge_time_sec: number;
  avg_total_cycle_time: number;
}

export interface CycleTimeResponse {
  by_hopper: CycleTimeEntry[];
  by_shift: CycleTimeEntry[];
}

export interface AggregationEntry {
  group_key: string;
  total_weight_kg: number;
  total_weight_tons: number;
  batch_count: number;
}

export interface AggregationResponse {
  by_shift: AggregationEntry[];
  by_material: AggregationEntry[];
  by_day: AggregationEntry[];
}

export interface ShiftReportRow {
  batch_id: string;
  timestamp: string;
  shift: string;
  hopper_id: string;
  material_type: string;
  target_weight_kg: number;
  actual_weight_kg: number;
  deviation_kg: number;
  deviation_pct: number;
  cycle_time_sec: number;
}

export interface ShiftReportResponse {
  rows: ShiftReportRow[];
  total_rows: number;
}

export interface DashboardResponse {
  kpis: KpiResponse;
  precision: PrecisionStatsResponse;
  cycle_times: CycleTimeResponse;
  aggregations: AggregationResponse;
  shift_report: ShiftReportResponse;
}

export interface FilterOptions {
  hoppers: string[];
  shifts: string[];
  materials: string[];
  date_min: string;
  date_max: string;
}

export interface DashboardFilters {
  startDate: string | null;
  endDate: string | null;
  shift: string | null;
  hopperId: string | null;
}

// Chat related types
export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  history: Message[];
}

export interface ChatResponse {
  role: 'assistant';
  content: string;
}

export interface ForecastPoint {
  date: string;
  predicted_tons: number;
  lower_bound: number;
  upper_bound: number;
}

export interface ForecastSeries {
  material: string;
  points: ForecastPoint[];
}

export interface ForecastResponse {
  series: ForecastSeries[];
  horizon_days: number;
  material: string;
}

export interface Alert {
  severity: 'warning' | 'critical';
  hopper_id: string;
  message: string;
  batch_id: string;
  timestamp: string;
}
