from itertools import product

from ic616.synthesis import (
    exact_pattern_detector,
    find_real_ltf,
    find_small_integer_ltf,
    synthesize_two_layer_exact,
    verify_network,
)


def test_xor_requires_layers() -> None:
    truth = {x: x[0] ^ x[1] for x in product((0, 1), repeat=2)}
    assert find_real_ltf(truth) is None
    assert find_small_integer_ltf(truth, max_abs_weight=5) is None
    network = synthesize_two_layer_exact(truth)
    assert network.depth == 2
    assert verify_network(network, truth)


def test_majority_is_one_ltf() -> None:
    truth = {x: int(sum(x) >= 2) for x in product((0, 1), repeat=3)}
    ltf = find_small_integer_ltf(truth, max_abs_weight=3)
    assert ltf is not None
    assert all(ltf(x) == y for x, y in truth.items())


def test_exact_pattern_detector() -> None:
    gate = exact_pattern_detector((1, 0, 1, 1))
    for x in product((0, 1), repeat=4):
        assert gate(x) == int(x == (1, 0, 1, 1))
