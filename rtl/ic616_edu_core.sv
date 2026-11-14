`ifndef IC616_EDU_CORE_SV
`define IC616_EDU_CORE_SV

`include "ic616_alu.sv"

module ic616_edu_core (
    input  logic clk,
    input  logic reset_n,
    output logic halted,
    output logic [7:0] accumulator,
    output logic [7:0] program_counter
);
    localparam logic [3:0] NOP = 4'h0;
    localparam logic [3:0] LDI = 4'h1;
    localparam logic [3:0] LDA = 4'h2;
    localparam logic [3:0] STA = 4'h3;
    localparam logic [3:0] ADD = 4'h4;
    localparam logic [3:0] SUB = 4'h5;
    localparam logic [3:0] ANDI = 4'h6;
    localparam logic [3:0] ORI  = 4'h7;
    localparam logic [3:0] XORI = 4'h8;
    localparam logic [3:0] SHL = 4'h9;
    localparam logic [3:0] SHR = 4'hA;
    localparam logic [3:0] JMP = 4'hB;
    localparam logic [3:0] JZ  = 4'hC;
    localparam logic [3:0] JN  = 4'hD;
    localparam logic [3:0] THR = 4'hE;
    localparam logic [3:0] HLT = 4'hF;

    logic [11:0] imem [0:255];
    logic [7:0]  dmem [0:255];
    logic [11:0] instruction;
    logic [3:0] opcode;
    logic [7:0] operand;
    logic zero_flag;
    logic negative_flag;
    logic carry_flag;

    logic [2:0] alu_op;
    logic [7:0] alu_b;
    logic [7:0] alu_y;
    logic alu_carry;
    logic alu_zero;
    logic alu_negative;

    function automatic [3:0] popcount8(input logic [7:0] value);
        integer j;
        begin
            popcount8 = 0;
            for (j = 0; j < 8; j = j + 1)
                popcount8 = popcount8 + value[j];
        end
    endfunction

    assign instruction = imem[program_counter];
    assign opcode = instruction[11:8];
    assign operand = instruction[7:0];
    assign alu_b = dmem[operand];

    always_comb begin
        unique case (opcode)
            ADD: alu_op = 3'd0;
            SUB: alu_op = 3'd1;
            ANDI: alu_op = 3'd2;
            ORI: alu_op = 3'd3;
            XORI: alu_op = 3'd4;
            SHL: alu_op = 3'd5;
            SHR: alu_op = 3'd6;
            default: alu_op = 3'd7;
        endcase
    end

    ic616_alu #(.WIDTH(8)) alu (
        .a(accumulator),
        .b(alu_b),
        .op(alu_op),
        .y(alu_y),
        .carry(alu_carry),
        .zero(alu_zero),
        .negative(alu_negative)
    );

    always_ff @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            halted <= 1'b0;
            accumulator <= 8'h00;
            program_counter <= 8'h00;
            zero_flag <= 1'b1;
            negative_flag <= 1'b0;
            carry_flag <= 1'b0;
        end else if (!halted) begin
            program_counter <= program_counter + 8'd1;
            unique case (opcode)
                NOP: ;
                LDI: begin
                    accumulator <= operand;
                    zero_flag <= (operand == 0);
                    negative_flag <= operand[7];
                end
                LDA: begin
                    accumulator <= dmem[operand];
                    zero_flag <= (dmem[operand] == 0);
                    negative_flag <= dmem[operand][7];
                end
                STA: dmem[operand] <= accumulator;
                ADD, SUB, ANDI, ORI, XORI, SHL, SHR: begin
                    accumulator <= alu_y;
                    zero_flag <= alu_zero;
                    negative_flag <= alu_negative;
                    carry_flag <= alu_carry;
                end
                JMP: program_counter <= operand;
                JZ: if (zero_flag) program_counter <= operand;
                JN: if (negative_flag) program_counter <= operand;
                THR: begin
                    accumulator <= (popcount8(accumulator) >= operand[3:0]);
                    zero_flag <= !(popcount8(accumulator) >= operand[3:0]);
                    negative_flag <= 1'b0;
                end
                HLT: halted <= 1'b1;
                default: halted <= 1'b1;
            endcase
        end
    end
endmodule

`endif
