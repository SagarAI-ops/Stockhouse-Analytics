import { useEffect, useState } from "react";
import { Package, Layers, Target, Timer, Loader2 } from "lucide-react";

import Header from "../components/layout/Header";
import FilterBar from "../components/layout/FilterBar";
import KpiCard from "../components/ui/KpiCard";
import DataTable from "../components/ui/DataTable";
import PrecisionControlChart from "../components/charts/PrecisionControlChart";
import CycleTimeBarChart from "../components/charts/CycleTimeBarChart";
import MaterialAggregationChart from "../components/charts/MaterialAggregationChart";

import { fetchFilters, fetchDashboardData } from "../api/client";
import { useFilterStore } from "../store/useFilterStore";
import type { FilterOptions, DashboardResponse } from "../types";

export default function Dashboard() {
  const { startDate, endDate, shift, hopperId } = useFilterStore();

  const [filters, setFilters] = useState<FilterOptions | null>(null);
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load filter options once on mount
  useEffect(() => {
    fetchFilters()
      .then(setFilters)
      .catch(() => setError("Failed to load filter options"));
  }, []);

  // Fetch dashboard data whenever filters change, with cancellation guard
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    fetchDashboardData({
      start_date: startDate,
      end_date: endDate,
      shift,
      hopper_id: hopperId,
    })
      .then((data) => {
        if (!cancelled) setDashboard(data);
      })
      .catch(() => {
        if (!cancelled) {
          setError("Failed to load dashboard data. Is the backend running?");
          setDashboard(null);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [startDate, endDate, shift, hopperId]);

  const precisionColor =
    dashboard &&
    Math.abs(dashboard.kpis.avg_precision_pct) < 0.5
      ? "text-emerald-400"
      : "text-red-400";

  return (
    <div className="min-h-screen flex flex-col bg-slate-900">
      <Header />
      <FilterBar filters={filters} />

      <main className="flex-1 p-6 space-y-6 overflow-auto">
        {error && (
          <div className="p-4 bg-red-900/30 border border-red-700 rounded-lg text-red-300 text-sm">
            {error}
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
            {/* KPI Row */}
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
                subtitle={`Within \u00B10.5% tolerance`}
              />
              <KpiCard
                title="Avg Cycle Time"
                value={`${dashboard.kpis.avg_cycle_time_sec.toFixed(1)} s`}
                icon={Timer}
                color="text-amber-400"
              />
            </div>

            {/* Charts Row */}
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

            {/* Cycle Time Row */}
            <CycleTimeBarChart data={dashboard.cycle_times.by_hopper} />

            {/* Data Table Row */}
            <DataTable rows={dashboard.shift_report.rows} />
          </>
        )}
      </main>
    </div>
  );
}
