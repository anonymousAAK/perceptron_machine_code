from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Iterable, Sequence

import numpy as np


def _binary_vector(x: Sequence[int], n: int) -> np.ndarray:
    arr = np.asarray(x, dtype=float)
    if arr.shape != (n,):
        raise ValueError(f"expected {n} inputs, received shape {arr.shape}")
    if not np.all(np.isin(arr, (0, 1))):
        raise ValueError("inputs must be binary values in {0, 1}")
    return arr


@dataclass(frozen=True)
class LinearThresholdFunction:
    """Boolean linear-threshold function y = 1[w·x + b >= 0]."""

    weights: tuple[float, ...]
    bias: float
    name: str = "LTF"

    def __post_init__(self) -> None:
        if not self.weights:
            raise ValueError("an LTF requires at least one input")
        values = np.asarray((*self.weights, self.bias), dtype=float)
        if not np.all(np.isfinite(values)):
            raise ValueError("weights and bias must be finite")

    @property
    def n_inputs(self) -> int:
        return len(self.weights)

    def score(self, x: Sequence[int]) -> float:
        arr = _binary_vector(x, self.n_inputs)
        return float(np.dot(np.asarray(self.weights, dtype=float), arr) + self.bias)

    def __call__(self, x: Sequence[int]) -> int:
        return int(self.score(x) >= 0.0)

    def evaluate_many(self, xs: Iterable[Sequence[int]]) -> np.ndarray:
        return np.asarray([self(x) for x in xs], dtype=np.uint8)

    def truth_table(self) -> list[tuple[tuple[int, ...], int, float]]:
        return [(x, self(x), self.score(x)) for x in product((0, 1), repeat=self.n_inputs)]

    def absolute_margin(self) -> float:
        return min(abs(score) for _, _, score in self.truth_table())

    def geometric_margin(self) -> float:
        norm = float(np.linalg.norm(np.asarray(self.weights, dtype=float)))
        if norm == 0.0:
            return float("inf") if self.absolute_margin() > 0 else 0.0
        return self.absolute_margin() / norm

    def scaled(self, factor: float) -> "LinearThresholdFunction":
        if factor <= 0:
            raise ValueError("logical scaling factor must be positive")
        return LinearThresholdFunction(
            tuple(factor * v for v in self.weights),
            factor * self.bias,
            f"{self.name}_scaled",
        )

    def perturbed(
        self,
        rng: np.random.Generator,
        weight_sigma: float = 0.0,
        bias_sigma: float = 0.0,
    ) -> "LinearThresholdFunction":
        w = np.asarray(self.weights, dtype=float)
        wp = w + rng.normal(0.0, weight_sigma, size=w.shape)
        bp = float(self.bias + rng.normal(0.0, bias_sigma))
        return LinearThresholdFunction(tuple(wp.tolist()), bp, f"{self.name}_perturbed")


@dataclass(frozen=True)
class ThresholdNetwork:
    """Feed-forward layers of threshold units.

    Every unit in a layer consumes the complete output vector from the
    preceding layer. The final layer may contain one or more outputs.
    """

    layers: tuple[tuple[LinearThresholdFunction, ...], ...]
    name: str = "ThresholdNetwork"

    def __post_init__(self) -> None:
        if not self.layers or any(not layer for layer in self.layers):
            raise ValueError("network must contain non-empty layers")
        first_width = self.layers[0][0].n_inputs
        if any(unit.n_inputs != first_width for unit in self.layers[0]):
            raise ValueError("first-layer units need equal fan-in")
        previous_width = len(self.layers[0])
        for layer in self.layers[1:]:
            if any(unit.n_inputs != previous_width for unit in layer):
                raise ValueError("layer fan-in must equal previous layer width")
            previous_width = len(layer)

    @property
    def n_inputs(self) -> int:
        return self.layers[0][0].n_inputs

    @property
    def depth(self) -> int:
        return len(self.layers)

    @property
    def size(self) -> int:
        return sum(len(layer) for layer in self.layers)

    def forward(self, x: Sequence[int]) -> tuple[int, ...]:
        values = tuple(int(v) for v in x)
        if len(values) != self.n_inputs:
            raise ValueError(f"expected {self.n_inputs} inputs")
        for layer in self.layers:
            values = tuple(unit(values) for unit in layer)
        return values

    def __call__(self, x: Sequence[int]) -> int | tuple[int, ...]:
        out = self.forward(x)
        return out[0] if len(out) == 1 else out

    def truth_table(self) -> list[tuple[tuple[int, ...], int | tuple[int, ...]]]:
        return [(x, self(x)) for x in product((0, 1), repeat=self.n_inputs)]


def primitive_catalog() -> dict[str, LinearThresholdFunction]:
    """Canonical exact fixed-weight threshold primitives."""
    return {
        "NOT": LinearThresholdFunction((-1.0,), 0.5, "NOT"),
        "AND2": LinearThresholdFunction((1.0, 1.0), -1.5, "AND2"),
        "OR2": LinearThresholdFunction((1.0, 1.0), -0.5, "OR2"),
        "NAND2": LinearThresholdFunction((-1.0, -1.0), 1.5, "NAND2"),
        "NOR2": LinearThresholdFunction((-1.0, -1.0), 0.5, "NOR2"),
        "MAJ3": LinearThresholdFunction((1.0, 1.0, 1.0), -1.5, "MAJ3"),
        "AT_LEAST_2_OF_4": LinearThresholdFunction((1.0, 1.0, 1.0, 1.0), -1.5, "AT_LEAST_2_OF_4"),
        "AT_LEAST_3_OF_5": LinearThresholdFunction((1.0,) * 5, -2.5, "AT_LEAST_3_OF_5"),
    }
