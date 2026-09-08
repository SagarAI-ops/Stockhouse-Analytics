import { useState, useMemo } from "react";
import { Download } from "lucide-react";
import type { ShiftReportRow } from "../../types";

interface Props {
  rows: ShiftReportRow[];
}

const PAGE_SIZE = 50;

export default function DataTable({ rows }: Props) {
  const [page, setPage] = useState(0);
  const totalPages = Math.max(1, Math.ceil(rows.length / PAGE_SIZE));
  const paged = useMemo(
    () => rows.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE),
    [rows, page]
  );

  const exportCsv = () => {
    const header = [
      "Batch ID",
      "Timestamp",
      "Shift",
      "Hopper",
      "Material",
      "Target (kg)",
      "Actual (kg)",
      "Deviation (kg)",
      "Deviation (%)",
      "Cycle Time (s)",
    ];
    const csvRows = rows.map((r) =>
      [
        r.batch_id,
        r.timestamp,
        r.shift,
        r.hopper_id,
        r.material_type,
        r.target_weight_kg,
        r.actual_weight_kg,
        r.deviation_kg,
        r.deviation_pct,
        r.cycle_time_sec,
      ].join(",")
    );
    const csv = [header.join(","), ...csvRows].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "shift_report.csv";
    a.click();
    URL.revokeObjectURL(url);
  };

  const isFail = (pct: number) => Math.abs(pct) > 0.5;

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 shadow-lg overflow-hidden">
      <div className="flex items-center justify-between px-5 py-3 border-b border-slate-700">
        <h3 className="text-sm font-semibold text-slate-200">
          Shift Report &mdash; {rows.length} batches
        </h3>
        <button
          onClick={exportCsv}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium rounded-md transition"
        >
          <Download className="w-3.5 h-3.5" />
          Export CSV
        </button>
      </div>

      <div className="overflow-x-auto max-h-[480px] overflow-y-auto">
        <table className="w-full text-xs">
          <thead className="bg-slate-900 sticky top-0 z-10">
            <tr className="text-slate-400 uppercase tracking-wider">
              <th className="px-3 py-2 text-left">Batch ID</th>
              <th className="px-3 py-2 text-left">Timestamp</th>
              <th className="px-3 py-2 text-center">Shift</th>
              <th className="px-3 py-2 text-center">Hopper</th>
              <th className="px-3 py-2 text-left">Material</th>
              <th className="px-3 py-2 text-right">Target (kg)</th>
              <th className="px-3 py-2 text-right">Actual (kg)</th>
              <th className="px-3 py-2 text-right">Dev (kg)</th>
              <th className="px-3 py-2 text-right">Dev (%)</th>
              <th className="px-3 py-2 text-right">Cycle (s)</th>
            </tr>
          </thead>
          <tbody>
            {paged.map((r, i) => (
              <tr
                key={`${r.batch_id}-${i}`}
                className={`border-t border-slate-700/50 ${
                  isFail(r.deviation_pct)
                    ? "bg-red-900/20 hover:bg-red-900/30"
                    : "hover:bg-slate-700/30"
                } transition`}
              >
                <td className="px-3 py-2 text-cyan-400 font-mono">
                  {r.batch_id}
                </td>
                <td className="px-3 py-2 text-slate-300">
                  {new Date(r.timestamp).toLocaleString()}
                </td>
                <td className="px-3 py-2 text-center">
                  <span
                    className={`inline-block px-1.5 py-0.5 rounded text-[10px] font-bold ${
                      r.shift === "A"
                        ? "bg-blue-900/50 text-blue-300"
                        : r.shift === "B"
                          ? "bg-purple-900/50 text-purple-300"
                          : "bg-amber-900/50 text-amber-300"
                    }`}
                  >
                    {r.shift}
                  </span>
                </td>
                <td className="px-3 py-2 text-center text-slate-300">
                  {r.hopper_id}
                </td>
                <td className="px-3 py-2 text-slate-300">{r.material_type}</td>
                <td className="px-3 py-2 text-right text-slate-300 tabular-nums">
                  {r.target_weight_kg.toLocaleString()}
                </td>
                <td className="px-3 py-2 text-right text-slate-300 tabular-nums">
                  {r.actual_weight_kg.toLocaleString()}
                </td>
                <td className="px-3 py-2 text-right tabular-nums text-slate-300">
                  {r.deviation_kg.toFixed(1)}
                </td>
                <td
                  className={`px-3 py-2 text-right tabular-nums font-semibold ${
                    isFail(r.deviation_pct) ? "text-red-400" : "text-emerald-400"
                  }`}
                >
                  {r.deviation_pct.toFixed(3)}%
                </td>
                <td className="px-3 py-2 text-right text-slate-300 tabular-nums">
                  {r.cycle_time_sec}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between px-5 py-2 border-t border-slate-700 text-xs text-slate-400">
          <span>
            Page {page + 1} of {totalPages}
          </span>
          <div className="flex gap-2">
            <button
              disabled={page === 0}
              onClick={() => setPage((p) => p - 1)}
              className="px-2 py-1 rounded bg-slate-700 disabled:opacity-40 hover:bg-slate-600 text-slate-300 transition"
            >
              Prev
            </button>
            <button
              disabled={page >= totalPages - 1}
              onClick={() => setPage((p) => p + 1)}
              className="px-2 py-1 rounded bg-slate-700 disabled:opacity-40 hover:bg-slate-600 text-slate-300 transition"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
