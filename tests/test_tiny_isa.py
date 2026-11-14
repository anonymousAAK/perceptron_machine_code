from ic616.tiny_isa import IC616Edu, Op, encode


def test_program_adds_and_halts() -> None:
    program = [
        encode(Op.LDI, 5),
        encode(Op.STA, 0x10),
        encode(Op.LDI, 3),
        encode(Op.ADD, 0x10),
        encode(Op.HLT),
    ]
    cpu = IC616Edu(program)
    cpu.run()
    assert cpu.acc == 8
    assert cpu.halted


def test_threshold_instruction() -> None:
    program = [
        encode(Op.LDI, 0b11110000),
        encode(Op.THR, 4),
        encode(Op.HLT),
    ]
    cpu = IC616Edu(program)
    cpu.run()
    assert cpu.acc == 1
