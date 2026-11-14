from __future__ import annotations

from pathlib import Path

import pandas as pd

from ic616.security import inject_single_parameter_faults
from ic616.threshold import primitive_catalog

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "fault_injection.csv"


def main() -> None:
    rows = []
    for name, cell in primitive_catalog().items():
        result = inject_single_parameter_faults(cell, trials=5_000, seed=616)
        rows.append(
            {
                "cell": name,
                "trials": result.trials,
                "semantic_changes": result.semantic_changes,
                "checksum_detections": result.checksum_detections,
                "checksum_misses": result.checksum_misses,
            }
        )
    frame = pd.DataFrame(rows)
    OUT.parent.mkdir(exist_ok=True)
    frame.to_csv(OUT, index=False)
    print(frame.to_string(index=False))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
