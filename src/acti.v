module acti(
input wire clk,rst,ena_tx,
output wire ene_out_tx
);

reg last;
reg actual;

//wire ene_out_tx;

initial
begin
	actual<=0;
	last<=0;
end


assign ene_out_tx=(~last)&actual;

always @(posedge clk,negedge rst)
begin
	if(!rst)
	begin
		actual<=0;
		last<=0;
	end
	else
	begin
		actual<=ena_tx;
		last<=actual;
	end
end


endmodule 
