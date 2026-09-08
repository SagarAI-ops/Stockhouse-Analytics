import { useEffect, useState } from "react";

import Header from "../components/layout/Header";
import ForecastChart from "../components/charts/ForecastChart";
import { fetchForecast } from "../api/client";
import type { ForecastResponse } from "../types";

interface Props {
  currentView?: "dashboard" | "forecast";
  onNavigate?: (view: "dashboard" | "forecast") => void;
}

export default function ForecastPage({ currentView, onNavigate }: Props) {
  const [material, setMaterial] = useState("All");
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchForecast({ material, days: 7 })
      .then((data) => {
        if (!cancelled) setForecast(data);
      })
      .catch(() => {
        if (!cancelled) setError("Failed to load forecast.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [material]);

  return (
    <div className="min-h-screen flex flex-col bg-slate-900">
      <Header currentView={currentView} onNavigate={onNavigate} />
      <main className="flex-1 space-y-6 overflow-auto p-6">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold text-white">
              24-hour material consumption forecast
            </h2>
            <p className="text-sm text-slate-400">
              Rolling 7-day mean ± 1.5σ, held over a 7-day horizon
            </p>
          </div>
          <label className="text-sm text-slate-300">
            Material
            <select
              value={material}
              onChange={(e) => setMaterial(e.target.value)}
              className="ml-2 rounded-md border border-slate-600 bg-slate-800 px-2 py-1"
            >
              <option value="All">All</option>
              <option value="Ore">Ore</option>
              <option value="Coke">Coke</option>
              <option value="Sinter">Sinter</option>
              <option value="Pellet">Pellet</option>
              <option value="Flux">Flux</option>
            </select>
          </label>
        </div>

        {error && (
          <div className="rounded-lg border border-red-700 bg-red-900/30 p-4 text-sm text-red-300">
            {error}
          </div>
        )}

        {loading && <p className="text-slate-400">Loading forecast…</p>}

        {!loading && forecast && (
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            {forecast.series.map((series) => (
              <ForecastChart
                key={series.material}
                data={series.points}
                title={`${series.material} — predicted tons`}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
