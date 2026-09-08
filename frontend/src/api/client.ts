import axios from "axios";
import type {
  Alert,
  ChatRequest,
  ChatResponse,
  DashboardResponse,
  FilterOptions,
  ForecastResponse,
  Message,
} from "../types";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000/api",
  timeout: 30000,
});

export async function fetchFilters(): Promise<FilterOptions> {
  const { data } = await apiClient.get<FilterOptions>("/filters");
  return data;
}

export interface DashboardParams {
  start_date?: string | null;
  end_date?: string | null;
  shift?: string | null;
  hopper_id?: string | null;
}

export async function fetchDashboardData(
  params: DashboardParams
): Promise<DashboardResponse> {
  const queryParams: Record<string, string> = {};
  if (params.start_date) queryParams.start_date = params.start_date;
  if (params.end_date) queryParams.end_date = params.end_date;
  if (params.shift && params.shift !== "All") queryParams.shift = params.shift;
  if (params.hopper_id && params.hopper_id !== "All")
    queryParams.hopper_id = params.hopper_id;

  const { data } = await apiClient.get<DashboardResponse>(
    "/dashboard_data",
    { params: queryParams }
  );
  return data;
}

export async function sendChatMessage(
  message: string,
  history: Message[]
): Promise<ChatResponse> {
  const payload: ChatRequest = { message, history };
  const { data } = await apiClient.post<ChatResponse>("/chat", payload);
  return data;
}

export interface ForecastParams {
  material?: string;
  days?: number;
}

export async function fetchForecast(
  params: ForecastParams = {}
): Promise<ForecastResponse> {
  const { data } = await apiClient.get<ForecastResponse>("/forecast", {
    params: {
      material: params.material ?? "All",
      days: params.days ?? 7,
    },
  });
  return data;
}

export async function fetchAlerts(): Promise<Alert[]> {
  const { data } = await apiClient.get<Alert[]>("/alerts");
  return data;
}
