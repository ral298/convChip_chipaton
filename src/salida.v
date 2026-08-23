module salida(
	input wire datos,
	input wire clk,
	output reg datos_out
);

always @(posedge clk)
begin
datos_out<=datos;
end
endmodule 
