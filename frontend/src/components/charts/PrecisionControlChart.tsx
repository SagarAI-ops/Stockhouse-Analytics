import { useMemo } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";
import type { PrecisionStatsResponse } from "../../types";

interface Props {
  data: PrecisionStatsResponse;
}

const MAX_POINTS = 200;

export default function PrecisionControlChart({ data }: Props) {
  const chartData = useMemo(() => {
    const pts = data.time_series;
    if (pts.length === 0) return [];

    // Downsample to MAX_POINTS for render performance
    if (pts.length <= MAX_POINTS) {
      return pts.map((p) => ({
        batch: p.batch_id.slice(-7),
        deviation_pct: p.deviation_pct,
      }));
    }
    const step = Math.ceil(pts.length / MAX_POINTS);
    return pts
      .filter((_, i) => i % step === 0)
      .map((p) => ({
        batch: p.batch_id.slice(-7),
        deviation_pct: p.deviation_pct,
      }));
  }, [data.time_series]);

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 shadow-lg p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-slate-200">
          Precision Control Chart (SPC)
        </h3>
        <div className="flex items-center gap-3 text-xs">
          <span className="text-emerald-400">
            Pass: {data.pass_count} ({data.pass_rate_pct}%)
          </span>
          <span className="text-red-400">Fail: {data.fail_count}</span>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis
            dataKey="batch"
            tick={{ fill: "#94a3b8", fontSize: 10 }}
            interval="preserveStartEnd"
            tickCount={6}
          />
          <YAxis
            tick={{ fill: "#94a3b8", fontSize: 10 }}
            domain={["auto", "auto"]}
            label={{
              value: "Deviation %",
              angle: -90,
              position: "insideLeft",
              fill: "#94a3b8",
              fontSize: 11,
            }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#1e293b",
              border: "1px solid #475569",
              borderRadius: 8,
              fontSize: 12,
            }}
            labelStyle={{ color: "#e2e8f0" }}
            formatter={(value: number) => [`${value.toFixed(4)}%`, "Deviation"]}
          />
          <ReferenceLine
            y={data.ucl}
            stroke="#ef4444"
            strokeDasharray="6 3"
            label={{ value: "UCL 0.5%", fill: "#ef4444", fontSize: 10, position: "right" }}
          />
          <ReferenceLine
            y={data.lcl}
            stroke="#ef4444"
            strokeDasharray="6 3"
            label={{ value: "LCL -0.5%", fill: "#ef4444", fontSize: 10, position: "right" }}
          />
          <ReferenceLine y={0} stroke="#475569" strokeDasharray="3 3" />
          <Line
            type="monotone"
            dataKey="deviation_pct"
            stroke="#06b6d4"
            strokeWidth={1.5}
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
