from __future__ import annotations

import json
from pathlib import Path

from ic616.tiny_isa import IC616Edu, Op, encode

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "ic616_edu_run.json"


def main() -> None:
    # Compute 5 + 3, then test whether the four high/low set bits of 0xF0
    # meet a population threshold. The first result remains in memory[0x20].
    program = [
        encode(Op.LDI, 5),
        encode(Op.STA, 0x10),
        encode(Op.LDI, 3),
        encode(Op.ADD, 0x10),
        encode(Op.STA, 0x20),
        encode(Op.LDI, 0xF0),
        encode(Op.THR, 4),
        encode(Op.HLT),
    ]
    cpu = IC616Edu(program)
    cpu.run()
    result = {
        "cycles": cpu.cycles,
        "halted": cpu.halted,
        "accumulator": cpu.acc,
        "memory_0x20": cpu.data[0x20],
        "zero": cpu.zero,
        "negative": cpu.negative,
        "carry": cpu.carry,
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
