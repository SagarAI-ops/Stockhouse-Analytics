import type { Alert } from "../../types";

interface Props {
  alerts: Alert[];
}

export default function AlertBanner({ alerts }: Props) {
  if (!alerts.length) return null;

  const critical = alerts.filter((a) => a.severity === "critical").length;
  const warning = alerts.filter((a) => a.severity === "warning").length;

  return (
    <div className="rounded-lg border border-amber-700 bg-amber-950/40 p-4 text-sm text-amber-100">
      <div className="mb-2 flex items-center justify-between">
        <p className="font-semibold">Active anomalies (last 24 h of data)</p>
        <p className="text-xs text-amber-300">
          {critical} critical · {warning} warning
        </p>
      </div>
      <ul className="max-h-36 space-y-1 overflow-y-auto text-xs text-amber-200">
        {alerts.slice(0, 8).map((alert) => (
          <li key={`${alert.batch_id}-${alert.message}`}>
            <span
              className={
                alert.severity === "critical"
                  ? "text-red-400"
                  : "text-amber-300"
              }
            >
              [{alert.severity}]
            </span>{" "}
            {alert.hopper_id} · {alert.message}
          </li>
        ))}
      </ul>
    </div>
  );
}
