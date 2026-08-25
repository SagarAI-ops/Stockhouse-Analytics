import { Flame } from "lucide-react";

export default function Header() {
  return (
    <header className="flex items-center gap-3 px-6 py-4 bg-slate-900 border-b border-slate-700">
      <Flame className="w-8 h-8 text-amber-500" />
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight">
          Blast Furnace Stockout Analytics
        </h1>
        <p className="text-xs text-slate-400">Phase 1 &mdash; Stockhouse Dashboard</p>
      </div>
    </header>
  );
}
