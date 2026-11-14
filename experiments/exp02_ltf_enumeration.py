from __future__ import annotations

from itertools import product
from pathlib import Path

import pandas as pd

from ic616.synthesis import find_real_ltf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "ltf_counts.csv"


def count_ltf(n: int) -> int:
    inputs = list(product((0, 1), repeat=n))
    count = 0
    for outputs in product((0, 1), repeat=len(inputs)):
        truth = dict(zip(inputs, outputs, strict=True))
        count += int(find_real_ltf(truth) is not None)
    return count


def main() -> None:
    rows = []
    for n in (1, 2, 3):
        total = 2 ** (2**n)
        threshold = count_ltf(n)
        rows.append(
            {
                "inputs": n,
                "all_boolean_functions": total,
                "linear_threshold_functions": threshold,
                "share": threshold / total,
            }
        )
    frame = pd.DataFrame(rows)
    OUT.parent.mkdir(exist_ok=True)
    frame.to_csv(OUT, index=False)
    print(frame.to_string(index=False))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
