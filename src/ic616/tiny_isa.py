from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum


class Op(IntEnum):
    NOP = 0x0
    LDI = 0x1
    LDA = 0x2
    STA = 0x3
    ADD = 0x4
    SUB = 0x5
    AND = 0x6
    OR = 0x7
    XOR = 0x8
    SHL = 0x9
    SHR = 0xA
    JMP = 0xB
    JZ = 0xC
    JN = 0xD
    THR = 0xE
    HLT = 0xF


def encode(op: Op, operand: int = 0) -> int:
    if not 0 <= operand <= 0xFF:
        raise ValueError("operand must fit in eight bits")
    return (int(op) << 8) | operand


@dataclass
class IC616Edu:
    """Complete reference simulator for the 8-bit IC616-Edu core.

    Instructions are 12 bits: four opcode bits and an eight-bit operand.
    The THR instruction demonstrates a threshold-native operation:
    ACC <- 1[popcount(ACC) >= immediate threshold].
    """

    program: list[int]
    data: bytearray = field(default_factory=lambda: bytearray(256))
    acc: int = 0
    pc: int = 0
    zero: bool = True
    negative: bool = False
    carry: bool = False
    halted: bool = False
    cycles: int = 0

    def _set_accumulator(self, value: int) -> None:
        self.acc = value & 0xFF
        self.zero = self.acc == 0
        self.negative = bool(self.acc & 0x80)

    def step(self) -> None:
        if self.halted:
            return
        if not 0 <= self.pc < len(self.program):
            raise RuntimeError(f"program counter {self.pc:#04x} is out of range")
        instruction = self.program[self.pc]
        self.pc = (self.pc + 1) & 0xFF
        op = Op((instruction >> 8) & 0xF)
        operand = instruction & 0xFF
        self.cycles += 1

        if op == Op.NOP:
            return
        if op == Op.LDI:
            self._set_accumulator(operand)
        elif op == Op.LDA:
            self._set_accumulator(self.data[operand])
        elif op == Op.STA:
            self.data[operand] = self.acc
        elif op == Op.ADD:
            total = self.acc + self.data[operand]
            self.carry = total > 0xFF
            self._set_accumulator(total)
        elif op == Op.SUB:
            total = self.acc - self.data[operand]
            self.carry = total >= 0
            self._set_accumulator(total)
        elif op == Op.AND:
            self._set_accumulator(self.acc & self.data[operand])
        elif op == Op.OR:
            self._set_accumulator(self.acc | self.data[operand])
        elif op == Op.XOR:
            self._set_accumulator(self.acc ^ self.data[operand])
        elif op == Op.SHL:
            self.carry = bool(self.acc & 0x80)
            self._set_accumulator(self.acc << 1)
        elif op == Op.SHR:
            self.carry = bool(self.acc & 0x01)
            self._set_accumulator(self.acc >> 1)
        elif op == Op.JMP:
            self.pc = operand
        elif op == Op.JZ:
            if self.zero:
                self.pc = operand
        elif op == Op.JN:
            if self.negative:
                self.pc = operand
        elif op == Op.THR:
            threshold = operand & 0x0F
            self._set_accumulator(int(self.acc.bit_count() >= threshold))
        elif op == Op.HLT:
            self.halted = True

    def run(self, max_cycles: int = 10_000) -> None:
        while not self.halted and self.cycles < max_cycles:
            self.step()
        if not self.halted:
            raise TimeoutError(f"program did not halt within {max_cycles} cycles")
