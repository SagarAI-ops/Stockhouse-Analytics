import { Filter } from "lucide-react";
import { useFilterStore } from "../../store/useFilterStore";
import type { FilterOptions } from "../../types";

interface Props {
  filters: FilterOptions | null;
}

export default function FilterBar({ filters }: Props) {
  const {
    startDate,
    endDate,
    shift,
    hopperId,
    setStartDate,
    setEndDate,
    setShift,
    setHopperId,
  } = useFilterStore();

  const selectClass =
    "bg-slate-700 text-slate-200 border border-slate-600 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500";

  const labelClass = "text-xs font-medium text-slate-400 uppercase tracking-wider";

  return (
    <div className="flex flex-wrap items-end gap-4 px-6 py-3 bg-slate-800/60 border-b border-slate-700">
      <div className="flex items-center gap-1.5 text-slate-400 mr-2">
        <Filter className="w-4 h-4" />
        <span className="text-sm font-semibold">Filters</span>
      </div>

      {/* Start Date */}
      <div className="flex flex-col gap-1">
        <label className={labelClass}>Start Date</label>
        <input
          type="date"
          value={startDate ?? ""}
          min={filters?.date_min ?? ""}
          max={filters?.date_max ?? ""}
          onChange={(e) => setStartDate(e.target.value || null)}
          className={selectClass}
        />
      </div>

      {/* End Date */}
      <div className="flex flex-col gap-1">
        <label className={labelClass}>End Date</label>
        <input
          type="date"
          value={endDate ?? ""}
          min={filters?.date_min ?? ""}
          max={filters?.date_max ?? ""}
          onChange={(e) => setEndDate(e.target.value || null)}
          className={selectClass}
        />
      </div>

      {/* Shift */}
      <div className="flex flex-col gap-1">
        <label className={labelClass}>Shift</label>
        <select
          value={shift}
          onChange={(e) => setShift(e.target.value)}
          className={selectClass}
        >
          <option value="All">All Shifts</option>
          {filters?.shifts.map((s) => (
            <option key={s} value={s}>
              Shift {s}
            </option>
          ))}
        </select>
      </div>

      {/* Hopper */}
      <div className="flex flex-col gap-1">
        <label className={labelClass}>Hopper</label>
        <select
          value={hopperId}
          onChange={(e) => setHopperId(e.target.value)}
          className={selectClass}
        >
          <option value="All">All Hoppers</option>
          {filters?.hoppers.map((h) => (
            <option key={h} value={h}>
              {h}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
