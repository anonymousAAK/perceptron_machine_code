from ic616.branch_predictor import (
    PerceptronPredictor,
    TwoBitCounterPredictor,
    evaluate_predictor,
    generate_long_correlation_trace,
)


def test_perceptron_learns_long_correlation() -> None:
    trace, target_pc = generate_long_correlation_trace(target_events=3_000, noise_probability=0.01)
    baseline = evaluate_predictor(
        TwoBitCounterPredictor(2048), trace, warmup=300, count_pc=target_pc
    )
    neural = evaluate_predictor(
        PerceptronPredictor(entries=2048, history_length=32),
        trace,
        warmup=300,
        count_pc=target_pc,
    )
    assert neural.miss_rate < baseline.miss_rate
