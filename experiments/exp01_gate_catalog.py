from __future__ import annotations

import csv
from pathlib import Path

from ic616.threshold import primitive_catalog

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "gate_catalog.csv"


def main() -> None:
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "gate",
                "input",
                "output",
                "score",
                "absolute_margin",
                "geometric_margin",
            ]
        )
        for name, gate in primitive_catalog().items():
            for x, y, score in gate.truth_table():
                writer.writerow(
                    [
                        name,
                        "".join(map(str, x)),
                        y,
                        score,
                        gate.absolute_margin(),
                        gate.geometric_margin(),
                    ]
                )
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
