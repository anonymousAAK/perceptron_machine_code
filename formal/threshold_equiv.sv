`include "../rtl/threshold_primitives.sv"

module threshold_equiv;
    (* anyconst *) logic a;
    (* anyconst *) logic b;
    (* anyconst *) logic c;
    logic and_y, or_y, xor_y, maj_y;

    t_and2 u_and(.a(a), .b(b), .y(and_y));
    t_or2  u_or (.a(a), .b(b), .y(or_y));
    t_xor2 u_xor(.a(a), .b(b), .y(xor_y));
    t_maj3 u_maj(.a(a), .b(b), .c(c), .y(maj_y));

    always_comb begin
        assert(and_y == (a & b));
        assert(or_y == (a | b));
        assert(xor_y == (a ^ b));
        assert(maj_y == ((a & b) | (a & c) | (b & c)));
    end
endmodule
