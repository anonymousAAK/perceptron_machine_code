`ifndef IC616_ALU_SV
`define IC616_ALU_SV

`include "threshold_primitives.sv"

module ic616_alu #(
    parameter int WIDTH = 8
) (
    input  logic [WIDTH-1:0] a,
    input  logic [WIDTH-1:0] b,
    input  logic [2:0]       op,
    output logic [WIDTH-1:0] y,
    output logic             carry,
    output logic             zero,
    output logic             negative
);
    localparam logic [2:0] OP_ADD = 3'd0;
    localparam logic [2:0] OP_SUB = 3'd1;
    localparam logic [2:0] OP_AND = 3'd2;
    localparam logic [2:0] OP_OR  = 3'd3;
    localparam logic [2:0] OP_XOR = 3'd4;
    localparam logic [2:0] OP_SHL = 3'd5;
    localparam logic [2:0] OP_SHR = 3'd6;
    localparam logic [2:0] OP_MOV = 3'd7;

    logic sub;
    logic [WIDTH-1:0] conditioned_b;
    logic [WIDTH-1:0] addsub_y;
    logic [WIDTH:0] carry_chain;
    logic [WIDTH-1:0] and_y;
    logic [WIDTH-1:0] or_y;
    logic [WIDTH-1:0] xor_y;

    assign sub = (op == OP_SUB);
    assign carry_chain[0] = sub;

    genvar i;
    generate
        for (i = 0; i < WIDTH; i = i + 1) begin : bit_slice
            t_xor2 u_condition_b(
                .a(b[i]),
                .b(sub),
                .y(conditioned_b[i])
            );
            t_full_adder u_addsub(
                .a(a[i]),
                .b(conditioned_b[i]),
                .cin(carry_chain[i]),
                .sum(addsub_y[i]),
                .cout(carry_chain[i+1])
            );
            t_and2 u_and(.a(a[i]), .b(b[i]), .y(and_y[i]));
            t_or2  u_or (.a(a[i]), .b(b[i]), .y(or_y[i]));
            t_xor2 u_xor(.a(a[i]), .b(b[i]), .y(xor_y[i]));
        end
    endgenerate

    always_comb begin
        carry = 1'b0;
        unique case (op)
            OP_ADD, OP_SUB: begin
                y = addsub_y;
                carry = carry_chain[WIDTH];
            end
            OP_AND: y = and_y;
            OP_OR:  y = or_y;
            OP_XOR: y = xor_y;
            OP_SHL: begin
                y = a << 1;
                carry = a[WIDTH-1];
            end
            OP_SHR: begin
                y = a >> 1;
                carry = a[0];
            end
            default: y = b;
        endcase
    end

    always_comb begin
        zero = (y == '0);
        negative = y[WIDTH-1];
    end
endmodule

`endif
