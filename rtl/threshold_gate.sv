// General behavioural model of a binary-input linear-threshold cell.
// A physical library implementation would replace this module during mapping.
module threshold_gate #(
    parameter int N = 2,
    parameter int signed W [0:N-1] = '{default: 1},
    parameter int signed BIAS = -1
) (
    input  logic [N-1:0] x,
    output logic         y
);
    integer i;
    integer signed sum;

    always_comb begin
        sum = BIAS;
        for (i = 0; i < N; i = i + 1) begin
            if (x[i]) sum = sum + W[i];
        end
        y = (sum >= 0);
    end
endmodule
