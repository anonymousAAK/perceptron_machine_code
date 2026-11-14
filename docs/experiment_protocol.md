# IC 616 Experimental Protocol

## 1. Evidence ladder

Every reported result must be labeled at one of five levels:

- **E0 - mathematical:** proof or solver certificate at the Boolean/function level.
- **E1 - executable:** deterministic software/RTL simulation with regression tests.
- **E2 - mapped:** synthesis and technology mapping with reproducible constraints.
- **E3 - physical:** placed-and-routed extraction, STA, power, DRC/LVS, and corner analysis.
- **E4 - silicon:** measured die data across voltage, frequency, temperature, and samples.

Never present an E0/E1 result as an E3/E4 result.

## 2. Function-level benchmark

Use EPFL and ISCAS/MCNC combinational benchmarks where licensing permits. Compare:

1. A conventional AIG/LUT/standard-cell baseline.
2. Majority-inverter or XOR-majority representations.
3. Fixed threshold cells.
4. Mixed conventional + threshold cells.
5. Programmable threshold cells with configuration storage included.

Report cell count, mapped area, critical delay, total negative slack, dynamic power, leakage, routing wirelength, fan-out, buffer count, and tool runtime. Run multiple synthesis seeds and constraints.

## 3. Cell characterization

For each threshold cell and reference CMOS cell:

- SPICE netlist and schematic.
- Input slew x output load lookup tables.
- PVT corners, Monte Carlo mismatch, aging assumptions.
- Functional margin, metastability behavior, minimum pulse width.
- Energy per transition and short-circuit current.
- Configuration retention/endurance for programmable cells.
- DFT observability and controllability.

The cell is not a usable standard cell until Liberty, LEF, GDS, SPICE/CDL, Verilog models, and DRC/LVS-clean layout exist.

## 4. Processor-level experiment

Implement two functionally equivalent RV32I cores:

- **Baseline:** conventional mapped core.
- **IC616-H:** mixed mapping using threshold cells only when the technology-aware cost model selects them.

Keep ISA, pipeline boundaries, memories, clock constraints, IO, and compiler binaries identical. Run ISA tests first, then CoreMark/Dhrystone only as smoke tests, then architecture-relevant workloads. Report IPC, frequency, energy per instruction, area, branch MPKI, cache MPKI, and timing closure.

## 5. Adaptive-boundary proof

For every learned component, state which signals it may influence. A safe default is:

- may affect fetch direction, prefetch request, replacement preference, or speculative scheduling priority;
- may not alter committed register values, memory ordering, exception behavior, privilege checks, or architectural control state.

Prove that all speculative effects are squashed or validated before retirement. Use assertions that compare the commit stream against a non-adaptive reference model.

## 6. Noise and fault campaign

Sweep device variation, comparator offset, weight drift, supply, temperature, timing jitter, and injected configuration faults. Report both raw logic error rate and system-level silent data corruption. Test ECC/signature detection separately from correction and recovery.

## 7. Reproducibility package

Archive:

- git commit and dependency lockfile;
- exact PDK/library version and license notes;
- tool versions and scripts;
- constraints, seeds, logs, netlists, reports;
- raw CSVs, plotting scripts, and a machine-readable manifest;
- negative results and failed configurations.
