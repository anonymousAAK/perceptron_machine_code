from __future__ import annotations

import importlib

EXPERIMENTS = [
    "exp01_gate_catalog",
    "exp02_ltf_enumeration",
    "exp03_margin_noise",
    "exp04_universal_synthesis",
    "exp05_branch_prediction",
    "exp06_fault_injection",
    "exp07_ic616_edu",
]


def main() -> None:
    for module_name in EXPERIMENTS:
        print(f"\n=== {module_name} ===")
        module = importlib.import_module(module_name)
        module.main()


if __name__ == "__main__":
    main()
