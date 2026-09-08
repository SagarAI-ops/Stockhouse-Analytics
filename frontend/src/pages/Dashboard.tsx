import { useCallback, useEffect, useState } from "react";
import { Package, Layers, Target, Timer, Loader2 } from "lucide-react";

import Header from "../components/layout/Header";
import FilterBar from "../components/layout/FilterBar";
import KpiCard from "../components/ui/KpiCard";
import DataTable from "../components/ui/DataTable";
import AlertBanner from "../components/ui/AlertBanner";
import PrecisionControlChart from "../components/charts/PrecisionControlChart";
import CycleTimeBarChart from "../components/charts/CycleTimeBarChart";
import MaterialAggregationChart from "../components/charts/MaterialAggregationChart";
import DailyAggregationChart from "../components/charts/DailyAggregationChart";

import { fetchAlerts, fetchDashboardData, fetchFilters } from "../api/client";
import { useFilterStore } from "../store/useFilterStore";
import type { Alert, DashboardResponse, FilterOptions } from "../types";

interface Props {
  currentView?: "dashboard" | "forecast";
  onNavigate?: (view: "dashboard" | "forecast") => void;
}

export default function Dashboard({ currentView, onNavigate }: Props) {
  const { startDate, endDate, shift, hopperId } = useFilterStore();

  const [filters, setFilters] = useState<FilterOptions | null>(null);
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchFilters()
      .then(setFilters)
      .catch(() => setError("Failed to load filter options"));
  }, []);

  const loadDashboard = useCallback(() => {
    setLoading(true);
    setError(null);

    return fetchDashboardData({
      start_date: startDate,
      end_date: endDate,
      shift,
      hopper_id: hopperId,
    })
      .then((data) => setDashboard(data))
      .catch(() => {
        setError("Failed to load dashboard data. Is the backend running?");
        setDashboard(null);
      })
      .finally(() => setLoading(false));
  }, [startDate, endDate, shift, hopperId]);

  useEffect(() => {
    void loadDashboard();
  }, [loadDashboard]);

  useEffect(() => {
    const loadAlerts = () => {
      fetchAlerts()
        .then(setAlerts)
        .catch(() => setAlerts([]));
    };
    loadAlerts();
    const intervalId = window.setInterval(loadAlerts, 30_000);
    return () => window.clearInterval(intervalId);
  }, []);

  const precisionColor =
    dashboard &&
    Math.abs(dashboard.kpis.avg_precision_pct) < 0.5
      ? "text-emerald-400"
      : "text-red-400";

  return (
    <div className="min-h-screen flex flex-col bg-slate-900">
      <Header currentView={currentView} onNavigate={onNavigate} />
      <FilterBar filters={filters} />

      <main className="flex-1 p-6 space-y-6 overflow-auto">
        <AlertBanner alerts={alerts} />

        {error && (
          <div className="p-4 bg-red-900/30 border border-red-700 rounded-lg text-red-300 text-sm">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <span>{error}</span>
              <button
                type="button"
                onClick={() => void loadDashboard()}
                className="rounded-md bg-red-800/60 px-3 py-1.5 text-xs font-medium text-red-100 hover:bg-red-800"
              >
                Retry
              </button>
            </div>
          </div>
        )}

        {loading && (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
            <span className="ml-3 text-slate-400">Loading analytics data...</span>
          </div>
        )}

        {!loading && dashboard && (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <KpiCard
                title="Total Material Charged"
                value={`${dashboard.kpis.total_tonnage.toLocaleString()} t`}
                icon={Package}
                color="text-cyan-400"
              />
              <KpiCard
                title="Total Batches"
                value={dashboard.kpis.total_batches.toLocaleString()}
                icon={Layers}
                color="text-blue-400"
              />
              <KpiCard
                title="Avg Filling Precision"
                value={`${dashboard.kpis.avg_precision_pct.toFixed(4)}%`}
                icon={Target}
                color={precisionColor}
                subtitle="Within ±0.5% tolerance"
              />
              <KpiCard
                title="Avg Cycle Time"
                value={`${dashboard.kpis.avg_cycle_time_sec.toFixed(1)} s`}
                icon={Timer}
                color="text-amber-400"
              />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
              <div className="lg:col-span-3">
                <PrecisionControlChart data={dashboard.precision} />
              </div>
              <div className="lg:col-span-2">
                <MaterialAggregationChart
                  data={dashboard.aggregations.by_material}
                />
              </div>
            </div>

            <DailyAggregationChart data={dashboard.aggregations.by_day} />

            <CycleTimeBarChart
              data={dashboard.cycle_times.by_hopper}
              title="Cycle Time by Hopper (Stacked)"
            />
            <CycleTimeBarChart
              data={dashboard.cycle_times.by_shift}
              title="Cycle Time by Shift (Stacked)"
            />

            <DataTable rows={dashboard.shift_report.rows} />
          </>
        )}
      </main>
    </div>
  );
}
