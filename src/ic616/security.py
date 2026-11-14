from __future__ import annotations

from dataclasses import dataclass
from itertools import product

import numpy as np

from .threshold import LinearThresholdFunction


@dataclass(frozen=True)
class FaultCampaignResult:
    trials: int
    semantic_changes: int
    checksum_detections: int
    checksum_misses: int


def configuration_checksum(weights: tuple[float, ...], bias: float) -> int:
    """Pedagogical checksum only; production configuration needs signatures."""
    quantized = tuple(int(round(value * 256)) for value in (*weights, bias))
    state = 0x616
    for value in quantized:
        state = ((state << 5) ^ (state >> 2) ^ value) & 0xFFFFFFFF
    return state


def inject_single_parameter_faults(
    ltf: LinearThresholdFunction,
    *,
    trials: int = 10_000,
    seed: int = 616,
) -> FaultCampaignResult:
    rng = np.random.default_rng(seed)
    inputs = list(product((0, 1), repeat=ltf.n_inputs))
    reference = [ltf(x) for x in inputs]
    baseline_checksum = configuration_checksum(ltf.weights, ltf.bias)
    params = np.asarray((*ltf.weights, ltf.bias), dtype=float)
    semantic_changes = 0
    detections = 0
    misses = 0

    for _ in range(trials):
        faulty = params.copy()
        index = int(rng.integers(0, len(faulty)))
        faulty[index] += float(rng.choice((-1.0, 1.0)))
        candidate = LinearThresholdFunction(
            tuple(faulty[:-1]), float(faulty[-1]), "FAULTY"
        )
        changed = any(
            candidate(x) != expected
            for x, expected in zip(inputs, reference, strict=True)
        )
        detected = (
            configuration_checksum(candidate.weights, candidate.bias)
            != baseline_checksum
        )
        semantic_changes += int(changed)
        detections += int(detected)
        misses += int(changed and not detected)
    return FaultCampaignResult(trials, semantic_changes, detections, misses)
