import {
  Area,
  ComposedChart,
  CartesianGrid,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ForecastPoint } from "../../types";

interface Props {
  data: ForecastPoint[];
  title?: string;
}

export default function ForecastChart({ data, title = "Forecast" }: Props) {
  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 shadow-lg p-5">
      <h3 className="text-sm font-semibold text-slate-200 mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={280}>
        <ComposedChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis
            dataKey="date"
            tick={{ fill: "#94a3b8", fontSize: 10 }}
            interval="preserveStartEnd"
          />
          <YAxis
            tick={{ fill: "#94a3b8", fontSize: 10 }}
            label={{
              value: "Tons",
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
          />
          <Area
            type="monotone"
            dataKey="upper_bound"
            stroke="none"
            fill="#22d3ee"
            fillOpacity={0.18}
            isAnimationActive={false}
          />
          <Area
            type="monotone"
            dataKey="lower_bound"
            stroke="none"
            fill="#0f172a"
            fillOpacity={0.85}
            isAnimationActive={false}
          />
          <Line
            type="monotone"
            dataKey="predicted_tons"
            stroke="#22d3ee"
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
            name="Predicted tons"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
