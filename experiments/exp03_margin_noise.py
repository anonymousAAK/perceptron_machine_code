from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from ic616.noise import monte_carlo_error_rate
from ic616.threshold import LinearThresholdFunction, primitive_catalog

ROOT = Path(__file__).resolve().parents[1]
CSV_OUT = ROOT / "results" / "margin_noise.csv"
FIG_OUT = ROOT / "figures" / "margin_noise.png"


def main() -> None:
    catalog = primitive_catalog()
    cells = {
        "AND2": catalog["AND2"],
        "MAJ3": catalog["MAJ3"],
        "AT_LEAST_3_OF_5": catalog["AT_LEAST_3_OF_5"],
        "weak_AND2": LinearThresholdFunction((1.0, 1.0), -1.99, "weak_AND2"),
    }
    sigmas = [0.00, 0.02, 0.05, 0.08, 0.12, 0.18, 0.25]
    rows = []
    for name, cell in cells.items():
        for sigma in sigmas:
            result = monte_carlo_error_rate(
                cell,
                trials=3_000,
                weight_sigma=sigma,
                bias_sigma=sigma,
                seed=616,
            )
            rows.append(
                {
                    "cell": name,
                    "sigma": sigma,
                    "absolute_margin": cell.absolute_margin(),
                    "geometric_margin": cell.geometric_margin(),
                    "error_rate": result.error_rate,
                }
            )
    frame = pd.DataFrame(rows)
    CSV_OUT.parent.mkdir(exist_ok=True)
    FIG_OUT.parent.mkdir(exist_ok=True)
    frame.to_csv(CSV_OUT, index=False)

    fig, ax = plt.subplots(figsize=(8, 5))
    for name, group in frame.groupby("cell"):
        ax.plot(group["sigma"], group["error_rate"], marker="o", label=name)
    ax.set_xlabel("Gaussian parameter variation σ")
    ax.set_ylabel("Logic error rate")
    ax.set_title("Threshold-cell error rate versus parameter variation")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_OUT, dpi=220)
    plt.close(fig)
    print(frame.to_string(index=False))
    print(f"wrote {CSV_OUT} and {FIG_OUT}")


if __name__ == "__main__":
    main()
