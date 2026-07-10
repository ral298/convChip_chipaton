module four_palabras_uart (
    input wire [7:0] dato,
    input wire rx_flat,
    input wire rst,
    input wire clk,

    output reg [31:0] data_comple,
    output reg flat_comple
);

reg [1:0] con;

reg [7:0] mem0;
reg [7:0] mem1;
reg [7:0] mem2;

always @(posedge clk or negedge rst)
begin
    if(!rst)
    begin
        con <= 2'd0;
        data_comple <= 32'd0;
        flat_comple <= 1'b0;

        mem0 <= 8'd0;
        mem1 <= 8'd0;
        mem2 <= 8'd0;
    end
    else
    begin
        

        if(rx_flat)
        begin
            if(con == 2'd3)
            begin
                data_comple <= {dato, mem2, mem1, mem0};

                flat_comple <= 1'b1;

                con <= 2'd0;
            end
            else
            begin
                case(con)
                    2'd0: mem0 <= dato;
                    2'd1: mem1 <= dato;
                    2'd2: mem2 <= dato;
                endcase

                con <= con + 2'd1;
                flat_comple <= 1'b0;
            end
        end
        else
        	flat_comple <= 1'b0;
    end
end

endmodule
