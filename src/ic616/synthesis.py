from __future__ import annotations

from fractions import Fraction
from itertools import product
from math import gcd
from typing import Mapping, Sequence

import numpy as np
from scipy.optimize import linprog

from .threshold import LinearThresholdFunction, ThresholdNetwork

TruthMap = Mapping[tuple[int, ...], int]


def all_inputs(n: int) -> list[tuple[int, ...]]:
    if n < 1:
        raise ValueError("n must be positive")
    return list(product((0, 1), repeat=n))


def normalize_truth_map(
    truth: TruthMap | Sequence[int], n: int | None = None
) -> dict[tuple[int, ...], int]:
    if isinstance(truth, Mapping):
        result = {tuple(int(v) for v in x): int(y) for x, y in truth.items()}
        if not result:
            raise ValueError("truth map cannot be empty")
        inferred = len(next(iter(result)))
        if n is not None and inferred != n:
            raise ValueError("truth-map width does not match n")
        n = inferred
        expected = set(all_inputs(n))
        if set(result) != expected:
            raise ValueError("truth map must cover the full Boolean cube")
    else:
        values = [int(v) for v in truth]
        if n is None:
            log = np.log2(len(values))
            if not float(log).is_integer():
                raise ValueError("truth-vector length must be a power of two")
            n = int(log)
        if len(values) != 2**n:
            raise ValueError("truth-vector length does not equal 2**n")
        result = dict(zip(all_inputs(n), values, strict=True))
    if any(v not in (0, 1) for v in result.values()):
        raise ValueError("truth outputs must be binary")
    return result


def find_real_ltf(
    truth: TruthMap | Sequence[int], n: int | None = None
) -> LinearThresholdFunction | None:
    """Find a maximum-margin real LTF by linear programming.

    Scale ambiguity is removed with an L1 bound on weights and bias.
    A positive optimum margin proves strict linear separability.
    """
    table = normalize_truth_map(truth, n)
    n = len(next(iter(table)))

    # Variables: w[0:n], bias, gamma, u[0:n+1] for absolute values.
    b_idx = n
    g_idx = n + 1
    u0 = n + 2
    total_vars = 2 * n + 3
    c = np.zeros(total_vars)
    c[g_idx] = -1.0
    rows: list[np.ndarray] = []
    rhs: list[float] = []

    for x, y in table.items():
        row = np.zeros(total_vars)
        if y:
            row[:n] = -np.asarray(x, dtype=float)
            row[b_idx] = -1.0
            row[g_idx] = 1.0
        else:
            row[:n] = np.asarray(x, dtype=float)
            row[b_idx] = 1.0
            row[g_idx] = 1.0
        rows.append(row)
        rhs.append(0.0)

    for j in range(n + 1):
        variable = j if j < n else b_idx
        absolute = u0 + j
        positive = np.zeros(total_vars)
        positive[variable] = 1.0
        positive[absolute] = -1.0
        rows.append(positive)
        rhs.append(0.0)
        negative = np.zeros(total_vars)
        negative[variable] = -1.0
        negative[absolute] = -1.0
        rows.append(negative)
        rhs.append(0.0)

    norm_row = np.zeros(total_vars)
    norm_row[u0 : u0 + n + 1] = 1.0
    rows.append(norm_row)
    rhs.append(1.0)

    bounds = [(None, None)] * (n + 1) + [(0.0, None)] + [(0.0, None)] * (n + 1)
    result = linprog(
        c,
        A_ub=np.asarray(rows),
        b_ub=np.asarray(rhs),
        bounds=bounds,
        method="highs",
    )
    if not result.success or result.x[g_idx] <= 1e-9:
        return None
    return LinearThresholdFunction(
        tuple(float(v) for v in result.x[:n]),
        float(result.x[b_idx]),
        "LP_LTF",
    )


def find_small_integer_ltf(
    truth: TruthMap | Sequence[int],
    n: int | None = None,
    max_abs_weight: int = 4,
) -> LinearThresholdFunction | None:
    """Search compact exact integer weights for small fan-in cells."""
    if max_abs_weight < 1:
        raise ValueError("max_abs_weight must be at least 1")
    table = normalize_truth_map(truth, n)
    n = len(next(iter(table)))
    positives = [np.asarray(x, dtype=int) for x, y in table.items() if y]
    negatives = [np.asarray(x, dtype=int) for x, y in table.items() if not y]
    if not positives:
        return LinearThresholdFunction((0.0,) * n, -0.5, "CONST0")
    if not negatives:
        return LinearThresholdFunction((0.0,) * n, 0.5, "CONST1")

    best: tuple[tuple[int, int, int], LinearThresholdFunction] | None = None
    values = range(-max_abs_weight, max_abs_weight + 1)
    for weights in product(values, repeat=n):
        if all(v == 0 for v in weights):
            continue
        w = np.asarray(weights, dtype=int)
        highest_negative = max(int(np.dot(w, x)) for x in negatives)
        lowest_positive = min(int(np.dot(w, x)) for x in positives)
        if highest_negative >= lowest_positive:
            continue
        threshold = Fraction(highest_negative + lowest_positive, 2)
        bias = -threshold
        scale = bias.denominator
        scaled_w = tuple(scale * int(v) for v in w)
        scaled_b = int(scale * bias)
        common = 0
        for value in (*scaled_w, scaled_b):
            common = gcd(common, abs(value))
        if common > 1:
            scaled_w = tuple(value // common for value in scaled_w)
            scaled_b //= common
        candidate = LinearThresholdFunction(
            tuple(float(v) for v in scaled_w), float(scaled_b), "INTEGER_LTF"
        )
        if any(candidate(x) != y for x, y in table.items()):
            continue
        cost = (
            max(abs(v) for v in scaled_w),
            sum(abs(v) for v in scaled_w) + abs(scaled_b),
            sum(v != 0 for v in scaled_w),
        )
        if best is None or cost < best[0]:
            best = (cost, candidate)
    return None if best is None else best[1]


def exact_pattern_detector(pattern: Sequence[int]) -> LinearThresholdFunction:
    """Return one threshold gate that recognizes exactly one bit pattern."""
    p = tuple(int(v) for v in pattern)
    if not p or any(v not in (0, 1) for v in p):
        raise ValueError("pattern must be a non-empty binary vector")
    weights = tuple(1.0 if bit else -1.0 for bit in p)
    bias = 0.5 - sum(p)
    return LinearThresholdFunction(weights, bias, f"MATCH_{''.join(map(str, p))}")


def synthesize_two_layer_exact(
    truth: TruthMap | Sequence[int], n: int | None = None
) -> ThresholdNetwork:
    """Universal exact two-layer construction using positive minterms.

    This is a constructive proof, not an efficient synthesis algorithm: one
    hidden unit is used for each positive row in the truth table.
    """
    table = normalize_truth_map(truth, n)
    n = len(next(iter(table)))
    positives = [x for x, y in table.items() if y]
    if not positives:
        hidden = (LinearThresholdFunction((0.0,) * n, -0.5, "CONST0_H"),)
        output = (LinearThresholdFunction((1.0,), -1.5, "CONST0_O"),)
        return ThresholdNetwork((hidden, output), "CONST0_NETWORK")
    hidden = tuple(exact_pattern_detector(x) for x in positives)
    output = (LinearThresholdFunction((1.0,) * len(hidden), -0.5, "OR_MINTERMS"),)
    return ThresholdNetwork((hidden, output), "TWO_LAYER_EXACT")


def verify_network(
    network: ThresholdNetwork, truth: TruthMap | Sequence[int]
) -> bool:
    table = normalize_truth_map(truth, network.n_inputs)
    return all(network(x) == y for x, y in table.items())
