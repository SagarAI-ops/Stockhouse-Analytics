import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { AggregationEntry } from "../../types";

interface Props {
  data: AggregationEntry[];
}

export default function DailyAggregationChart({ data }: Props) {
  const sorted = [...data].sort((a, b) => a.group_key.localeCompare(b.group_key));

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 shadow-lg p-5">
      <h3 className="text-sm font-semibold text-slate-200 mb-4">
        Daily Material Charged
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={sorted}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis
            dataKey="group_key"
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
            formatter={(value) => [
              `${Number(value ?? 0).toLocaleString()} t`,
              "Total Weight",
            ]}
          />
          <Area
            type="monotone"
            dataKey="total_weight_tons"
            stroke="#22d3ee"
            fill="#22d3ee"
            fillOpacity={0.25}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
