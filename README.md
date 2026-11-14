# IC 616 Book Labs

Executable companion to **The Perceptron Machine: Threshold Logic, Adaptive Hardware, and the Architecture of IC 616** by Adarsh Keshri.

This repository separates four different claims that are often collapsed into one:

1. A Boolean function can be represented by a threshold network.
2. The representation can be synthesized and verified automatically.
3. A threshold cell can be realized as physical circuitry.
4. A processor built with those cells can improve a measurable design objective.

The Python modules and experiments establish the first two claims for small and medium examples, provide an executable teaching processor, and demonstrate a practical adaptive use case in branch prediction. The SystemVerilog directory is a readable reference RTL model. Physical PPA, transistor-level robustness, and tapeout claims require the external EDA flow described in `docs/experiment_protocol.md`; no silicon result is fabricated here.

## Repository map

- `src/ic616/threshold.py` - exact linear-threshold functions, margins, perturbations, networks.
- `src/ic616/synthesis.py` - LP separability test, compact integer-weight search, universal two-layer synthesis.
- `src/ic616/noise.py` - Monte Carlo parameter-variation analysis.
- `src/ic616/branch_predictor.py` - 2-bit and perceptron branch predictors plus an interleaved correlation trace.
- `src/ic616/tiny_isa.py` - complete IC616-Edu 8-bit processor simulator and threshold-native instruction.
- `src/ic616/security.py` - configuration fault-injection demonstrator.
- `experiments/` - reproducible experiments that generate CSV evidence and plots.
- `rtl/` - threshold primitives, an 8-bit ALU, and IC616-Edu reference RTL.
- `formal/` - primitive equivalence properties for a SymbiYosys/Yosys flow.
- `tests/` - Python unit tests.
- `docs/figure_prompts.md` - image-generation prompt atlas.

## Run

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
export PYTHONPATH="$PWD/src"         # Windows PowerShell: $env:PYTHONPATH="$PWD/src"
pytest -q
make experiments
```

The reference run in the book was executed with Python 3, NumPy, SciPy, pandas, matplotlib, and pytest. It produced:

- 14 of the 16 two-input Boolean functions as single linear-threshold functions; XOR and XNOR are the exceptions.
- 104 of the 256 three-input Boolean functions as single linear-threshold functions.
- an exact two-layer construction for any supplied truth table.
- a margin/noise curve showing why physical robustness is a synthesis objective, not an afterthought.
- a perceptron predictor that learns a cross-branch long-history correlation that a local two-bit counter cannot.
- a complete IC616-Edu program run whose stored arithmetic result is 8 and whose threshold instruction returns 1.

## RTL and formal flow

The RTL uses SystemVerilog for readability. A general behavioral `threshold_gate` and concrete primitives are included. XOR is deliberately a multi-layer network, while full-adder carry is a single majority gate. The included environment did not contain Icarus Verilog, Verilator, Yosys, or SymbiYosys, so the Python models and tests were executed here, while HDL compilation and formal proof remain commands for the reader's EDA installation:

```bash
iverilog -g2012 -I rtl -o build/ic616_edu rtl/tb_ic616_edu_core.sv
vvp build/ic616_edu
cd formal && sby -f threshold_equiv.sby
```

For an ASIC research flow, use Yosys/EQY/SymbiYosys for synthesis and formal equivalence, and OpenROAD with a suitable PDK for place, route, extraction, and timing. A real threshold-cell library must provide Liberty timing/power models, LEF abstracts, GDS, SPICE, and characterized PVT corners.

## Research integrity

- Synthetic branch traces demonstrate mechanism, not application-wide speedup.
- Monte Carlo perturbation is a cell-model experiment, not foundry-qualified yield analysis.
- The configuration checksum is pedagogical; deploy cryptographic signatures, ECC, secure boot, rollback protection, and runtime integrity monitors in a real programmable fabric.
- A conventional SRAM/flip-flop implementation remains the baseline for exact architectural state unless a new cell is shown to beat it under measured PPA and reliability constraints.

## License

Code in this companion is released for research and educational use under the MIT License. The book text and figure prompts remain copyright Adarsh Keshri.
