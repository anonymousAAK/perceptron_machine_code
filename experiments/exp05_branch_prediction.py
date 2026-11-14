from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from ic616.branch_predictor import (
    PerceptronPredictor,
    TwoBitCounterPredictor,
    evaluate_predictor,
    generate_long_correlation_trace,
)

ROOT = Path(__file__).resolve().parents[1]
CSV_OUT = ROOT / "results" / "branch_prediction.csv"
FIG_OUT = ROOT / "figures" / "branch_prediction.png"


def main() -> None:
    rows = []
    for noise in (0.00, 0.01, 0.02, 0.05, 0.10, 0.15):
        trace, target_pc = generate_long_correlation_trace(
            target_events=5_000,
            history_length=32,
            noise_probability=noise,
            seed=616,
        )
        predictors = {
            "2-bit counter": TwoBitCounterPredictor(entries=2048),
            "perceptron": PerceptronPredictor(entries=2048, history_length=32),
        }
        for name, predictor in predictors.items():
            stats = evaluate_predictor(
                predictor, trace, warmup=500, count_pc=target_pc
            )
            rows.append(
                {
                    "predictor": name,
                    "trace_noise": noise,
                    "predictions": stats.predictions,
                    "misses": stats.misses,
                    "miss_rate": stats.miss_rate,
                }
            )
    frame = pd.DataFrame(rows)
    CSV_OUT.parent.mkdir(exist_ok=True)
    FIG_OUT.parent.mkdir(exist_ok=True)
    frame.to_csv(CSV_OUT, index=False)

    fig, ax = plt.subplots(figsize=(8, 5))
    for name, group in frame.groupby("predictor"):
        ax.plot(group["trace_noise"], group["miss_rate"], marker="o", label=name)
    ax.set_xlabel("Injected outcome noise probability")
    ax.set_ylabel("Misprediction rate")
    ax.set_title("Synthetic long-correlation branch")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_OUT, dpi=220)
    plt.close(fig)
    print(frame.to_string(index=False))
    print(f"wrote {CSV_OUT} and {FIG_OUT}")


if __name__ == "__main__":
    main()
