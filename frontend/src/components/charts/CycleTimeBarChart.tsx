import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import type { CycleTimeEntry } from "../../types";

interface Props {
  data: CycleTimeEntry[];
}

export default function CycleTimeBarChart({ data }: Props) {
  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 shadow-lg p-5">
      <h3 className="text-sm font-semibold text-slate-200 mb-4">
        Cycle Time by Hopper (Stacked)
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} barCategoryGap="20%">
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis
            dataKey="group_key"
            tick={{ fill: "#94a3b8", fontSize: 11 }}
          />
          <YAxis
            tick={{ fill: "#94a3b8", fontSize: 10 }}
            label={{
              value: "Seconds",
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
          <Legend
            wrapperStyle={{ fontSize: 11, color: "#94a3b8" }}
          />
          <Bar
            dataKey="avg_fill_time_sec"
            name="Fill Time"
            stackId="a"
            fill="#3b82f6"
            radius={[0, 0, 0, 0]}
            isAnimationActive={false}
          />
          <Bar
            dataKey="avg_discharge_time_sec"
            name="Discharge Time"
            stackId="a"
            fill="#f59e0b"
            radius={[4, 4, 0, 0]}
            isAnimationActive={false}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
