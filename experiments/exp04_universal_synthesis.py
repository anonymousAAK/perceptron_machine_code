from __future__ import annotations

from itertools import product
from pathlib import Path

import pandas as pd

from ic616.synthesis import synthesize_two_layer_exact, verify_network

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "universal_synthesis.csv"


def parity(x: tuple[int, ...]) -> int:
    return sum(x) % 2


def majority(x: tuple[int, ...]) -> int:
    return int(sum(x) >= (len(x) + 1) // 2)


def exact_one(x: tuple[int, ...]) -> int:
    return int(sum(x) == 1)


def main() -> None:
    rows = []
    for n in range(2, 9):
        inputs = list(product((0, 1), repeat=n))
        for name, fn in (
            ("parity", parity),
            ("majority", majority),
            ("exactly_one", exact_one),
        ):
            truth = {x: fn(x) for x in inputs}
            network = synthesize_two_layer_exact(truth)
            rows.append(
                {
                    "function": name,
                    "inputs": n,
                    "positive_minterms": sum(truth.values()),
                    "network_units": network.size,
                    "network_depth": network.depth,
                    "verified": verify_network(network, truth),
                }
            )
    frame = pd.DataFrame(rows)
    OUT.parent.mkdir(exist_ok=True)
    frame.to_csv(OUT, index=False)
    print(frame.to_string(index=False))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
