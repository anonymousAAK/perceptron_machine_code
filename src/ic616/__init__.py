"""Reference models and experiments for The Perceptron Machine / IC 616."""

from .threshold import LinearThresholdFunction, ThresholdNetwork, primitive_catalog
from .synthesis import (
    exact_pattern_detector,
    find_real_ltf,
    find_small_integer_ltf,
    synthesize_two_layer_exact,
)

__all__ = [
    "LinearThresholdFunction",
    "ThresholdNetwork",
    "primitive_catalog",
    "exact_pattern_detector",
    "find_real_ltf",
    "find_small_integer_ltf",
    "synthesize_two_layer_exact",
]
