import type { LucideIcon } from "lucide-react";

interface Props {
  title: string;
  value: string | number;
  icon: LucideIcon;
  color?: string;
  subtitle?: string;
}

export default function KpiCard({
  title,
  value,
  icon: Icon,
  color = "text-cyan-400",
  subtitle,
}: Props) {
  return (
    <div className="flex items-center gap-4 p-5 bg-slate-800 rounded-xl border border-slate-700 shadow-lg">
      <div className={`p-3 rounded-lg bg-slate-700/50 ${color}`}>
        <Icon className="w-6 h-6" />
      </div>
      <div className="min-w-0">
        <p className="text-xs text-slate-400 uppercase tracking-wider truncate">
          {title}
        </p>
        <p className={`text-2xl font-bold ${color}`}>{value}</p>
        {subtitle && (
          <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>
        )}
      </div>
    </div>
  );
}
