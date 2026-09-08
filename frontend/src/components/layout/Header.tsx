import { Flame } from "lucide-react";

interface Props {
  currentView?: "dashboard" | "forecast";
  onNavigate?: (view: "dashboard" | "forecast") => void;
}

export default function Header({
  currentView = "dashboard",
  onNavigate,
}: Props) {
  return (
    <header className="flex items-center justify-between gap-3 px-6 py-4 bg-slate-900 border-b border-slate-700">
      <div className="flex items-center gap-3">
        <Flame className="w-8 h-8 text-amber-500" />
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">
            Blast Furnace Stockout Analytics
          </h1>
          <p className="text-xs text-slate-400">
            Stockhouse Analytics · AI-Powered
          </p>
        </div>
      </div>
      {onNavigate && (
        <nav className="flex gap-2 text-sm">
          <button
            type="button"
            onClick={() => onNavigate("dashboard")}
            className={`rounded-md px-3 py-1.5 ${
              currentView === "dashboard"
                ? "bg-slate-700 text-white"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Dashboard
          </button>
          <button
            type="button"
            onClick={() => onNavigate("forecast")}
            className={`rounded-md px-3 py-1.5 ${
              currentView === "forecast"
                ? "bg-slate-700 text-white"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Forecast
          </button>
        </nav>
      )}
    </header>
  );
}
