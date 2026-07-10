module con32_one_instruction(
	input rxd,clk_ref,rst,
	//input [31:0] instruction,
	output txd,
	
	output rxd_out,
	
	//output [63:0]instruction,
	//output flat_comple,
	//input ena_tx,
	//output  tx_rdy,
	output  tx_busy,
	output  rx_sample_pulse
	//input [7:0] tx_data,
	//output [ 31:0]convolucion_salida,
	//output locked
	//output  bit_convolucion_salida
	
	//input flat_comple
	
);


//rx
wire      rx_ready;
wire [7:0]rx_data ;
wire [31:0] instruction;
wire flat_comple;

//tx 
wire ena_tx;
wire [7:0]tx_data;			

//wire      tx_busy;			
wire      tx_rdy;
//wire      rx_sample_pulse;


//convolucion
wire [15:0]convolucion_salida_inter;


wire bit_convolucion_salida;

wire ene_out_tx;

wire uat_tx_next;

//wire locked;
wire clk;
assign clk=clk_ref;
/*
clk_wiz_0 ppl_u0(
		.clk_in1  (clk_ref), //  refclk.clk
		.reset     (!rst), //   reset.reset
		.clk_out1(clk), // outclk0.clk
		.locked  (locked) //  locked.export
	);
*/


uart_ultimo uart0(
.clk(clk),
.rxd(rxd),
.rst(rst),
.rx_rdy (rx_ready), 
.rx_data(rx_data ),


.ena_tx(ene_out_tx),
.tx_data			 (tx_data			),
.txd				 (txd					),
.tx_busy			 (tx_busy			),
.tx_rdy			 (tx_rdy				),
.rx_sample_pulse(rx_sample_pulse )

//
);

acti actiu0(
.clk(clk),
.rst(rst),
.ena_tx(ena_tx),
.ene_out_tx(ene_out_tx)
);


four_palabras_uart uart_rx(
.rx_flat		(rx_ready),
.rst			(rst),
.clk			(clk),
.dato			(rx_data),
.data_comple(instruction),
.flat_comple(flat_comple)
);


con32bits_parall con_mod_u0(
	.clock(clk),
	.rst(rst),
	.datos_in(instruction[31:16]),
	.col(instruction[10:7]),//11:7
	.ren(instruction[5:2]),//6:2
	.ind_filtro(instruction[14:12]),
	.ind_filtro_fil(instruction[8:6]),
	.uat_tx_next(uat_tx_next),
	.col_fil(instruction[5:4]),
	.ren_fil(instruction[3:2]),
   .cual(instruction[14]),
	.ren_bias(instruction[15]),
	.run_uart_4(flat_comple),	
	.traba(instruction[0]),
	.wr(instruction[1]),
	.salida(convolucion_salida_inter),
	.out(bit_convolucion_salida)
);


uart_tx_4in4 tx_sum(
.clk				(clk),
.rst				(rst),
.uat_tx_next	(uat_tx_next),
.start			(bit_convolucion_salida),
.next_uart		(tx_rdy),
.input_dato		(convolucion_salida_inter),
.Output_dato	(tx_data),
.flat_out		(ena_tx)
);

salida out1(
	.datos(rxd),
	.clk(clk),
	.datos_out(rxd_out)
);




endmodule 
