module uart_tx_4in4(
input clk,start,next_uart,rst,
input [15:0] input_dato,
output reg [7:0] Output_dato,
output reg flat_out,
output reg uat_tx_next
);

	reg Flat,First;
	reg [15:0] Dato;
	reg [1:0]Con;
	wire check;
	assign check=(First|next_uart);
	initial
	begin
		Flat<=1'b0;
		Con<=2'h0;
		First<=1'b0;
		flat_out<=1'b0;
		Output_dato<=8'h0;
		Dato<=16'h0;
		uat_tx_next<=1'b0;
	end

	always @(posedge clk,negedge rst)
	begin
		if(!rst)
		begin
			Flat<=1'b0;
			Con<=2'h0;
			First<=1'b0;
			flat_out<=1'b0;
			Output_dato<=8'h0;
			Dato<=16'h0;
			uat_tx_next<=1'b0;
		end
		else
		begin
			if (start)
			begin
				Flat<=1'b1;
				flat_out<=1'b1;
				Dato<=input_dato;
				//Output_dato<=input_dato[7:0];
				First<=1'b1;
				Con<=2'h0;
				
			end
			/*
			if(First)
			begin
				flat_out<=0;
				First<=0;
			end
			*/
			
			if (Flat&check)
			begin
				
				
				First<=1'b0;
				
				if (Con<2'd2)
				begin
					
					Dato<=Dato>>4'd8;
					Con<=Con+2'b01;
					uat_tx_next<=1'b0;
					flat_out<=1'b1;
					Output_dato<=Dato[7:0];
					//flat_out<=1;
				end
				else
				begin
					Flat<=1'b0;
					Con<=2'h0;
					flat_out<=1'b0;
					uat_tx_next<=1'b1;
					//flat_out<=0;
					//Flat_next_dato_conv<=1;
				end
			end
			else
			begin
				
				flat_out<=1'b0;
				uat_tx_next<=1'b0;
				
				//Flat_next_dato_conv<=0;
			end
		end

	end
endmodule 


