import pandas as pd

from models import Alert


def get_alerts(df: pd.DataFrame) -> list[Alert]:
    """Flag last-24h (of data) precision breaches and cycle-time outliers."""
    if df.empty:
        return []

    cutoff = df["timestamp_start"].max() - pd.Timedelta(hours=24)
    recent = df[df["timestamp_start"] >= cutoff]
    if recent.empty:
        return []

    alerts: list[Alert] = []
    cycle_mean = float(recent["total_cycle_time"].mean())
    cycle_std = float(recent["total_cycle_time"].std(ddof=0) or 0.0)
    cycle_limit = cycle_mean + 2 * cycle_std if cycle_std else cycle_mean * 1.5

    for _, row in recent.iterrows():
        ts = row["timestamp_start"].isoformat()
        hopper = str(row["hopper_id"])
        batch = str(row["batch_id"])
        abs_dev = abs(float(row["deviation_pct"]))

        if abs_dev > 2.5:
            alerts.append(
                Alert(
                    severity="critical",
                    hopper_id=hopper,
                    message=f"Filling deviation {abs_dev:.2f}% exceeds 2.5% critical limit",
                    batch_id=batch,
                    timestamp=ts,
                )
            )
        elif abs_dev > 1.5:
            alerts.append(
                Alert(
                    severity="warning",
                    hopper_id=hopper,
                    message=f"Filling deviation {abs_dev:.2f}% exceeds 1.5% warning limit",
                    batch_id=batch,
                    timestamp=ts,
                )
            )

        cycle = float(row["total_cycle_time"])
        if cycle_std and cycle > cycle_limit:
            alerts.append(
                Alert(
                    severity="warning",
                    hopper_id=hopper,
                    message=f"Cycle time {cycle:.0f}s is an outlier vs last-24h mean {cycle_mean:.0f}s",
                    batch_id=batch,
                    timestamp=ts,
                )
            )

    alerts.sort(key=lambda a: (0 if a.severity == "critical" else 1, a.timestamp), reverse=False)
    return alerts[:50]
