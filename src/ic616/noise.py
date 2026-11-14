from __future__ import annotations

from dataclasses import dataclass
from itertools import product

import numpy as np

from .threshold import LinearThresholdFunction


@dataclass(frozen=True)
class NoiseResult:
    trials: int
    vector_evaluations: int
    errors: int

    @property
    def error_rate(self) -> float:
        return self.errors / self.vector_evaluations if self.vector_evaluations else 0.0


def monte_carlo_error_rate(
    ltf: LinearThresholdFunction,
    *,
    trials: int = 10_000,
    weight_sigma: float = 0.05,
    bias_sigma: float = 0.05,
    seed: int = 616,
) -> NoiseResult:
    if trials <= 0:
        raise ValueError("trials must be positive")
    rng = np.random.default_rng(seed)
    xs = list(product((0, 1), repeat=ltf.n_inputs))
    reference = [ltf(x) for x in xs]
    errors = 0
    for _ in range(trials):
        perturbed = ltf.perturbed(rng, weight_sigma, bias_sigma)
        errors += sum(
            perturbed(x) != expected
            for x, expected in zip(xs, reference, strict=True)
        )
    return NoiseResult(trials, trials * len(xs), errors)
