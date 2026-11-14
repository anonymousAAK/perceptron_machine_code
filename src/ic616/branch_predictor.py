from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol

import numpy as np


class BranchPredictor(Protocol):
    def predict(self, pc: int) -> int: ...
    def update(self, pc: int, outcome: int) -> None: ...


@dataclass
class PredictionStats:
    predictions: int = 0
    misses: int = 0

    @property
    def miss_rate(self) -> float:
        return self.misses / self.predictions if self.predictions else 0.0

    @property
    def accuracy(self) -> float:
        return 1.0 - self.miss_rate


class TwoBitCounterPredictor:
    """A direct-mapped table of classic 2-bit saturating counters."""

    def __init__(self, entries: int = 256) -> None:
        if entries <= 0:
            raise ValueError("entries must be positive")
        self.entries = entries
        self.table = np.full(entries, 2, dtype=np.uint8)  # weakly taken

    def predict(self, pc: int) -> int:
        return int(self.table[pc % self.entries] >= 2)

    def update(self, pc: int, outcome: int) -> None:
        idx = pc % self.entries
        value = int(self.table[idx])
        self.table[idx] = (
            min(3, value + 1) if outcome else max(0, value - 1)
        )


class PerceptronPredictor:
    """Hashed global-history perceptron predictor.

    The update rule follows the classic insight: train after a miss or when
    the prediction magnitude is below a confidence threshold. History is
    bipolar (-1/+1), and weights saturate to a fixed bit width.
    """

    def __init__(
        self,
        entries: int = 64,
        history_length: int = 32,
        weight_bits: int = 8,
    ) -> None:
        if entries <= 0 or history_length <= 0 or weight_bits < 2:
            raise ValueError("invalid predictor dimensions")
        self.entries = entries
        self.history_length = history_length
        self.maximum = (1 << (weight_bits - 1)) - 1
        self.minimum = -(1 << (weight_bits - 1))
        self.weights = np.zeros(
            (entries, history_length + 1), dtype=np.int16
        )
        self.history = np.ones(history_length, dtype=np.int8)
        self.theta = int(1.93 * history_length + 14)

    def _index(self, pc: int) -> int:
        return ((pc >> 2) ^ (pc >> 11)) % self.entries

    def score(self, pc: int) -> int:
        row = self.weights[self._index(pc)].astype(np.int32)
        return int(row[0] + np.dot(row[1:], self.history.astype(np.int32)))

    def predict(self, pc: int) -> int:
        return int(self.score(pc) >= 0)

    def update(
        self,
        pc: int,
        outcome: int,
        prediction: int | None = None,
        score: int | None = None,
    ) -> None:
        if prediction is None:
            prediction = self.predict(pc)
        if score is None:
            score = self.score(pc)
        target = 1 if outcome else -1
        if prediction != outcome or abs(score) <= self.theta:
            idx = self._index(pc)
            row = self.weights[idx].astype(np.int32)
            row[0] = np.clip(row[0] + target, self.minimum, self.maximum)
            row[1:] = np.clip(
                row[1:] + target * self.history.astype(np.int32),
                self.minimum,
                self.maximum,
            )
            self.weights[idx] = row.astype(np.int16)
        self.history[1:] = self.history[:-1]
        self.history[0] = target


def evaluate_predictor(
    predictor: BranchPredictor,
    trace: Iterable[tuple[int, int]],
    warmup: int = 0,
    count_pc: int | None = None,
) -> PredictionStats:
    """Evaluate a predictor while optionally scoring only one static branch.

    All trace events still update global history. This lets experiments use
    interleaved context branches but report accuracy for the target branch.
    """
    stats = PredictionStats()
    scored = 0
    for pc, outcome in trace:
        prediction = int(predictor.predict(pc))
        score = predictor.score(pc) if isinstance(predictor, PerceptronPredictor) else None
        should_count = count_pc is None or pc == count_pc
        if should_count:
            if scored >= warmup:
                stats.predictions += 1
                stats.misses += int(prediction != outcome)
            scored += 1
        if isinstance(predictor, PerceptronPredictor):
            predictor.update(pc, outcome, prediction, score)
        else:
            predictor.update(pc, outcome)
    return stats


def generate_long_correlation_trace(
    target_events: int = 8_000,
    history_length: int = 32,
    noise_probability: float = 0.02,
    seed: int = 616,
) -> tuple[list[tuple[int, int]], int]:
    """Interleave random context branches with a linearly predictable target.

    Each episode emits ``history_length`` random context branches followed by
    one target branch. The target outcome is the sign of a sparse weighted sum
    over the immediately preceding global-history bits. Its marginal taken rate
    is close to balanced, so a local two-bit counter has little signal, while a
    perceptron can learn the cross-branch correlation.
    """
    if target_events <= 0 or history_length < 32:
        raise ValueError("target_events must be positive and history_length >= 32")
    rng = np.random.default_rng(seed)
    target_pc = 0x6160
    context_pcs = [0x1000 + 4 * i for i in range(history_length)]
    taps = np.array([0, 3, 7, 15, 23, 31], dtype=int)
    coefficients = np.array([2, -1, 2, 1, -2, 2], dtype=int)
    trace: list[tuple[int, int]] = []

    for _ in range(target_events):
        context = rng.choice((-1, 1), size=history_length).astype(np.int8)
        for pc, bipolar in zip(context_pcs, context, strict=True):
            trace.append((pc, int(bipolar > 0)))
        # The predictor stores newest history at index zero.
        predictor_order = context[::-1]
        score = int(np.dot(coefficients, predictor_order[taps]))
        outcome = int(score >= 0)
        if rng.random() < noise_probability:
            outcome ^= 1
        trace.append((target_pc, outcome))
    return trace, target_pc
