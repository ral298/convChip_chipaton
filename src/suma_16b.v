
module suma_16b(
    input wire  [15:0] A,
    input  wire [15:0] B,
    output [15:0] result
);
wire cary;

assign {cary,result} = A + B;

endmodule

