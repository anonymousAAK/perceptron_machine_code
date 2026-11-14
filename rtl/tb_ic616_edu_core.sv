`timescale 1ns/1ps
`include "ic616_edu_core.sv"

module tb_ic616_edu_core;
    logic clk = 0;
    logic reset_n = 0;
    logic halted;
    logic [7:0] accumulator;
    logic [7:0] program_counter;

    ic616_edu_core dut(
        .clk(clk),
        .reset_n(reset_n),
        .halted(halted),
        .accumulator(accumulator),
        .program_counter(program_counter)
    );

    always #5 clk = ~clk;

    initial begin
        // LDI 5; STA 0x10; LDI 3; ADD [0x10]; HLT.
        dut.imem[0] = 12'h105;
        dut.imem[1] = 12'h310;
        dut.imem[2] = 12'h103;
        dut.imem[3] = 12'h410;
        dut.imem[4] = 12'hF00;
        #12 reset_n = 1;
        wait(halted);
        if (accumulator !== 8'd8) $fatal(1, "expected 8, got %0d", accumulator);
        $display("IC616-Edu PASS: accumulator=%0d", accumulator);
        $finish;
    end
endmodule
