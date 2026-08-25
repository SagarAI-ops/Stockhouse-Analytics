import axios from "axios";
import type { DashboardResponse, FilterOptions } from "../types";

const apiClient = axios.create({
  baseURL: "http://localhost:8000/api",
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
