"""
Blast Furnace Stockhouse Dummy Data Generator.
Generates 30 days of realistic batch data simulating PLC/SCADA data streams.
"""

import csv
import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

import numpy as np

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
NUM_DAYS: int = 30
BATCHES_PER_DAY: int = 200
OUTPUT_FILE: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dummy_data.csv")

HOPPERS: List[str] = ["H1", "H2", "H3", "H4"]

MATERIALS: List[str] = ["Coke", "Sinter", "Pellet", "Limestone", "Ore"]

# Weight ranges per material (kg)
MATERIAL_WEIGHT_RANGES: Dict[str, tuple] = {
    "Coke": (10000.0, 18000.0),
    "Sinter": (15000.0, 25000.0),
    "Pellet": (12000.0, 22000.0),
    "Limestone": (10000.0, 16000.0),
    "Ore": (18000.0, 30000.0),
}

# Shift definitions based on hour of day
# Shift A: 06:00 - 14:00, Shift B: 14:00 - 22:00, Shift C: 22:00 - 06:00
FAILURE_RATE: float = 0.02  # 2% chance of large deviation

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _assign_shift(hour: int) -> str:
    if 6 <= hour < 14:
        return "A"
    elif 14 <= hour < 22:
        return "B"
    else:
        return "C"


def _generate_target_weight(material: str) -> float:
    lo, hi = MATERIAL_WEIGHT_RANGES[material]
    return round(random.uniform(lo, hi), 1)


def _generate_actual_weight(target: float) -> float:
    """Normal noise around target with occasional large deviations."""
    if random.random() < FAILURE_RATE:
        # Inject a failure: deviation > 150 kg
        direction = random.choice([-1, 1])
        deviation = direction * random.uniform(150.0, target * 0.03)
    else:
        deviation = float(np.random.normal(0, 50))
    return round(target + deviation, 1)


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def generate_dummy_data() -> None:
    now = datetime.now()
    start_date = now - timedelta(days=NUM_DAYS)
    current_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

    rows: List[Dict[str, Any]] = []
    daily_batch_counter: int = 0
    batch_global: int = 0

    while current_date < now:
        date_str = current_date.strftime("%Y%m%d")
        daily_batch_counter = 0

        # Distribute ~BATCHES_PER_DAY batches across 24 hours
        intervals = sorted(
            [random.randint(0, 24 * 60 - 1) for _ in range(BATCHES_PER_DAY)]
        )

        for minute_offset in intervals:
            batch_global += 1
            daily_batch_counter += 1

            ts_start = current_date + timedelta(minutes=minute_offset)
            shift = _assign_shift(ts_start.hour)
            hopper_id = random.choice(HOPPERS)
            material_type = random.choice(MATERIALS)
            target_weight = _generate_target_weight(material_type)
            actual_weight = _generate_actual_weight(target_weight)

            fill_time = random.randint(30, 90)
            discharge_time = random.randint(20, 60)

            ts_fill_end = ts_start + timedelta(seconds=fill_time)
            ts_discharge_end = ts_fill_end + timedelta(seconds=discharge_time)

            batch_id = f"BATCH-{date_str}-{daily_batch_counter:03d}"

            rows.append({
                "batch_id": batch_id,
                "timestamp_start": ts_start.isoformat(),
                "timestamp_fill_end": ts_fill_end.isoformat(),
                "timestamp_discharge_end": ts_discharge_end.isoformat(),
                "shift": shift,
                "hopper_id": hopper_id,
                "material_type": material_type,
                "target_weight_kg": target_weight,
                "actual_weight_kg": actual_weight,
                "fill_time_sec": fill_time,
                "discharge_time_sec": discharge_time,
            })

        current_date += timedelta(days=1)

    # Write to CSV
    fieldnames = [
        "batch_id",
        "timestamp_start",
        "timestamp_fill_end",
        "timestamp_discharge_end",
        "shift",
        "hopper_id",
        "material_type",
        "target_weight_kg",
        "actual_weight_kg",
        "fill_time_sec",
        "discharge_time_sec",
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} batch records -> {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_dummy_data()
