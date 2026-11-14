`ifndef IC616_THRESHOLD_PRIMITIVES_SV
`define IC616_THRESHOLD_PRIMITIVES_SV

module t_not(input logic a, output logic y);
    integer score;
    always_comb begin
        score = (a ? -2 : 0) + 1;
        y = (score >= 0);
    end
endmodule

module t_and2(input logic a, b, output logic y);
    integer score;
    // a + b - 1.5 >= 0, represented after multiplying by two.
    always_comb begin
        score = (a ? 2 : 0) + (b ? 2 : 0) - 3;
        y = (score >= 0);
    end
endmodule

module t_or2(input logic a, b, output logic y);
    integer score;
    always_comb begin
        score = (a ? 2 : 0) + (b ? 2 : 0) - 1;
        y = (score >= 0);
    end
endmodule

module t_nand2(input logic a, b, output logic y);
    integer score;
    always_comb begin
        score = (a ? -2 : 0) + (b ? -2 : 0) + 3;
        y = (score >= 0);
    end
endmodule

module t_nor2(input logic a, b, output logic y);
    integer score;
    always_comb begin
        score = (a ? -2 : 0) + (b ? -2 : 0) + 1;
        y = (score >= 0);
    end
endmodule

module t_maj3(input logic a, b, c, output logic y);
    integer score;
    // The carry function of a full adder is one threshold gate.
    always_comb begin
        score = (a ? 2 : 0) + (b ? 2 : 0) + (c ? 2 : 0) - 3;
        y = (score >= 0);
    end
endmodule

module t_xor2(input logic a, b, output logic y);
    // XOR is not linearly separable; this is a two-layer threshold network.
    logic any_one;
    logic not_both;
    t_or2   u_or   (.a(a), .b(b), .y(any_one));
    t_nand2 u_nand (.a(a), .b(b), .y(not_both));
    t_and2  u_and  (.a(any_one), .b(not_both), .y(y));
endmodule

module t_xor3(input logic a, b, c, output logic y);
    logic ab;
    t_xor2 u0 (.a(a), .b(b), .y(ab));
    t_xor2 u1 (.a(ab), .b(c), .y(y));
endmodule

module t_mux2(input logic d0, d1, s, output logic y);
    logic ns;
    logic p0;
    logic p1;
    t_not  u_not (.a(s), .y(ns));
    t_and2 u_a0  (.a(d0), .b(ns), .y(p0));
    t_and2 u_a1  (.a(d1), .b(s),  .y(p1));
    t_or2  u_or  (.a(p0), .b(p1), .y(y));
endmodule

module t_full_adder(
    input  logic a,
    input  logic b,
    input  logic cin,
    output logic sum,
    output logic cout
);
    t_xor3 u_sum   (.a(a), .b(b), .c(cin), .y(sum));
    t_maj3 u_carry (.a(a), .b(b), .c(cin), .y(cout));
endmodule

`endif
