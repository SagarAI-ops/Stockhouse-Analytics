import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import type { AggregationEntry } from "../../types";

interface Props {
  data: AggregationEntry[];
}

const COLORS = ["#06b6d4", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"];

export default function MaterialAggregationChart({ data }: Props) {
  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 shadow-lg p-5">
      <h3 className="text-sm font-semibold text-slate-200 mb-4">
        Material Tonnage Distribution
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} barCategoryGap="25%">
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis
            dataKey="group_key"
            tick={{ fill: "#94a3b8", fontSize: 11 }}
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
          <Bar dataKey="total_weight_tons" radius={[6, 6, 0, 0]} isAnimationActive={false}>
            {data.map((_, index) => (
              <Cell
                key={`cell-${index}`}
                fill={COLORS[index % COLORS.length]}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
