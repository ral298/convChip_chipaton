
// Definición del módulo prodpun con puertos de entrada y salida
module con32bits_parall (
	 input clock,rst,
     input  [15:0] datos_in,//signed
	 input [3:0] col,
	 input [3:0] ren,
	 input [1:0] col_fil,
	 input [1:0] ren_fil,
	 input [2:0] ind_filtro,
	 input [2:0] ind_filtro_fil,
	 input ren_bias,
	 //input [4:0] dato_obt,
     input cual,
	 input traba,
	 input wr, // Habilitación de escritura
	 input run_uart_4,
	 input uat_tx_next,
     output reg  [15:0] salida, // Salida de 32 bits//signed
	 output reg out
);

//`include "function_fijo.vh"



parameter operation=16;

parameter operation_max=operation*operation;
parameter operation_lees_2=operation-2;
parameter operation_lees_1=operation-1;
//Primero tenemos el ancho de los datos que son 8 bits, como luego se tiene que multiplicar por 8, se opto por hacer corrimiento de 3.
parameter ancho_bits_datos=8;
parameter bits_input=3;


parameter N_dot_product=4;

// Declaraciones de la memoria RAM y señales
reg  [9*8*ancho_bits_datos-1:0] filtro; // Memoria RAM de 4x8 para el vector 1   %(7*7)-1
reg  [((operation)*(operation))*ancho_bits_datos-1:0] senal; // Memoria RAM de 4x8 para el vector 2
integer i; // Variable de iteración para el bucle
reg Flat;
wire [N_dot_product-1:0] flat_procesar;
reg First;
reg Flat_tx;
reg first_calculo;
reg [3:0] con_tx;
//reg signed [15:0] var_n;
reg  [8*16-1:0] bias;
reg  [(operation)*16-1:0] mem_out;
integer j;
integer i_bias;
integer i_ima;
integer i_ima_mem;
reg [3:0]i_reng;
reg Flat_anterior;
reg [2:0] ind_filtro_punto_mo;
reg [2:0] Contador_secciones;
reg [2:0] Contador_sec_post_calculos;
//reg [4:0]i_colu;	
//reg [4:0] col_usar;
//reg [4:0] ren_usar;
//reg [1:0]long_resi;
//reg [1:0]long_brinco;
//reg [2:0] longuse;
//reg [1:0] long;
//reg [9:0] sum_reg;
reg [3:0] i_reng_tree [operation-1-2:0];

integer i_reng_index;

initial 
begin
	ind_filtro_punto_mo<=3'd0;
		out<=1'h0;
		//var_n=16'b0;
		salida <= 16'b0;
		Flat<=1'h0;
		First<=1'h0;
		Flat_tx<=1'h0;
		con_tx<=4'h0;
		i_reng<=4'h0;
		first_calculo<=1'h0;
		Contador_secciones<=3'h0;
		Contador_sec_post_calculos<=3'h0;
		for (i_reng_index=0; i_reng_index<(operation-2);i_reng_index=i_reng_index+1)
					   i_reng_tree[i_reng_index]<=4'h0;
		//i_colu=5'h0;
		for (j = 0; j < 8*9*ancho_bits_datos; j = j + 1) begin
			filtro[j]<=1'h0;
		end
		for (i_bias=0; i_bias<8*16;i_bias=i_bias+1)
		begin
			bias[i_bias]<=1'h0;
		end
		
		for (i_ima=0; i_ima<((operation)*(operation)*ancho_bits_datos);i_ima=i_ima+1)
		begin
			senal[i_ima]<=1'h0;
		end
		Flat_anterior<=1'h0;
end



/*
wire clk_buf1;



BUFG u_baud_clkbuf1 (
    .I(clock),
    .O(clk_buf1)
);
    */
    
    

wire [6:0] inde_filtro_wr =(ind_filtro_fil*7'd9+(col_fil%7'd3)*7'd3+(ren_fil%7'd3));// << 4;
//wire [6:0] inde_filtro_wr =(ind_filtro_fil*7'd9+(col_fil%7'd3)*7'd3+(ren_fil%7'd3));// << 4;
wire [2:0]  inde_bias_wr=ind_filtro_fil;// << 4; 
//wire [2:0]  inde_bias_wr=ind_filtro_fil;// << 4; 
wire [7:0] inde_senal_wr=((col)*operation+ren);// << 4;
//wire [7:0] inde_senal_wr=((col%operation)*operation+ren%operation);// << 4;
integer i_senal_indx,i_bias_indx,i_filtro_indx;
// Proceso de escritura en los dos vectores
always @(posedge clock,negedge rst) begin //datos_in1 or datos_in2 or wr or cual or filtro or senal or dato_obt
   
	
	if(!rst)
	begin
	    ind_filtro_punto_mo<=3'd0;
		out<=1'h0;
		//var_n=16'b0;
		salida <= 16'b0;
		Flat<=1'h0;
		First<=1'h0;
		Flat_tx<=1'h0;
		con_tx<=4'h0;
		i_reng<=4'h0;
		first_calculo<=1'h0;
		Contador_secciones<=3'h0;
		Contador_sec_post_calculos<=3'h0;
		for (i_reng_index=0; i_reng_index<(operation-2);i_reng_index=i_reng_index+1)
					   i_reng_tree[i_reng_index]<=4'h0;
		//i_colu=5'h0;
		for (j = 0; j < 8*9*ancho_bits_datos; j = j + 1) begin
			filtro[j]<=1'h0;
		end
		for (i_bias=0; i_bias<8*16;i_bias=i_bias+1)
		begin
			bias[i_bias]<=1'h0;
		end
		
		for (i_ima=0; i_ima<((operation)*(operation)*ancho_bits_datos);i_ima=i_ima+1)
		begin
			senal[i_ima]<=1'h0;
		end
		Flat_anterior<=1'h0;
	end
	
	else
	begin
		if (run_uart_4)
		begin
			if (traba)
			begin
				 if (wr) 
				 begin
					if (!cual) 
					begin
						
						if(!ren_bias) begin
						
						    
							//filtro[inde_filtro_wr +: 16]<= datos_in; // Escritura en el vector 1
							for(i_filtro_indx=7'd0; i_filtro_indx<9*8; i_filtro_indx=i_filtro_indx+7'd1) begin

                                if(inde_filtro_wr == i_filtro_indx)
                                    filtro[({i_filtro_indx,{bits_input{1'd0}}}) +: ancho_bits_datos] <= datos_in;
    
                            end
                        end
						else
						    
							//bias[inde_bias_wr +: 16]<=datos_in;//{{16{datos_in[15]}},datos_in};
						    for(i_bias_indx=3'd0; i_bias_indx<8; i_bias_indx=i_bias_indx+3'd1) begin

                                if(inde_bias_wr == i_bias_indx)
                                    bias[({i_bias_indx,4'h0}) +: 16] <= datos_in;
    
                            end
					end
					else begin
					    
						//senal[inde_senal_wr +: 16]<= datos_in; // Escritura en el vector 2
						
						for(i_senal_indx=8'd0; i_senal_indx<(operation_max); i_senal_indx=i_senal_indx+8'd1) begin

							if(inde_senal_wr == i_senal_indx)
							    senal[({i_senal_indx,{bits_input{1'd0}}}) +: ancho_bits_datos] <= datos_in;

						end
					end
					
					//out<=0;
				 end
				 
				 else
				 begin
				    Flat_anterior<=1'h1;
					Flat<=1'h0;
					first_calculo<=1'h1;
					//out<=0;
					con_tx<=4'h0;
					i_reng<=4'h0;
					Contador_secciones<=3'h0;
					Contador_sec_post_calculos<=3'h0;
					for (i_reng_index=0; i_reng_index<(operation-2);i_reng_index=i_reng_index+1)begin
					       i_reng_tree[i_reng_index]<=4'h0;
					    end
					ind_filtro_punto_mo<=ind_filtro;
				 end
			end
			out<=1'h0;
		end
		
		else if(Flat_tx &(First | uat_tx_next))
		begin
			First<=1'h0;
			out<=1'h1;
			salida<=mem_out[{con_tx,4'h0} +: 16];
			
			
			if(i_reng<=ren)
			begin
			
				if(con_tx<col)
					con_tx<=con_tx+4'h1;
					
				else
				begin
					con_tx<=4'h0;
					if(i_reng==ren)
					begin
						Flat_tx<=1'h0;//Al terminar de mandar toda la imagen resultante mande a 0 Flat_tx para ya no seguir mandando mensajes
						i_reng<=4'h0;
						for (i_reng_index=0; i_reng_index<(operation-2);i_reng_index=i_reng_index+1)begin
					       i_reng_tree[i_reng_index]<=4'h0;
					    end
					end
					else
					begin
					   for (i_reng_index=0; i_reng_index<(operation-2);i_reng_index=i_reng_index+1)begin
					       i_reng_tree[i_reng_index]<=i_reng_tree[i_reng_index]+4'h1;
						end
						i_reng<=i_reng+4'h1;
						//Flat<=1'h0;
						Flat_anterior<=1'h1;
						Contador_secciones<=3'h0;
						Contador_sec_post_calculos<=3'h0;
					end
				end
				
			end
		end
		else
			out<=1'h0;
		
		if(Flat_anterior)begin
		  
		  Flat<=1'h1;
		  
		  Contador_secciones<=Contador_secciones+3'h1;
		  
		  if (Contador_secciones>=3'd3)
		      Flat_anterior<=1'h0;
		  
		end
		
		if(Flat)
		begin
		  if (Contador_sec_post_calculos>=3'd3)
			Flat<=1'h0;
			
		end
		
		if (|flat_procesar)
		begin
		    Contador_sec_post_calculos<=Contador_sec_post_calculos+3'h1;
		    if (Contador_sec_post_calculos>=3'd3)
		          Contador_sec_post_calculos<=3'h0;
		    
		    
		    if(first_calculo)
			begin
				first_calculo<=1'h0;
				First<=1'h1;
				Flat_tx<=1'h1;
				
			end
		      
		end
        
	end
end



/*
genvar col_i;
generate
	for (col_i = 0; col_i < operation-2; col_i = col_i + 1) begin : mem_write
		always @(posedge clock,negedge rst) begin
			if(!rst)
				mem_out[col_i]<=16'h0;
			else if(Flat)
			begin
				var_n=16'h0;
				for (i = 0; i <9 ; i = i + 1) 
				begin
					var_n= var_n + (senal[(operation*( col_i%operation) +i_reng%operation+  i%5'h3   +   operation*((i - i%5'h3)/5'h3)) ] * filtro[ind_filtro*5'h9+i]);  //32*dato_obt  +  long_resi   +   32*long_brinco
					
				end
				mem_out[col_i]<= var_n+bias[ind_filtro];
			end
		end
	end
endgenerate
*/


// El 8 es por la cantidad de nodos que se necesitan para llevar acabo la combinacion de todos los elementos,
// ya que hacer la combinacion de los elementos de las sumas, para no hacer sumas en cascada.
//reg [15:0] cables_sum[8*(operation-2)-1:0];




/*
integer i_reng_index;
reg [3:0] i_reng_tree [operation-2:0];
always@(posedge clock,negedge rst) 
begin
    
    
        for (i_reng_index=0; i_reng_index<(operation-2);i_reng_index=i_reng_index+1) 
        begin
            if ( (!rst) | (run_uart_4 & traba  & (!wr))) begin
                i_reng_tree[i_reng_index]<=4'h0;
            end
            else if ( (Flat_tx &(First | uat_tx_next)) & (i_reng<=ren)&(!(con_tx<col)))
            begin
                if (i_reng==ren)
                    i_reng_tree[i_reng_index]<=4'h0;
                else 
                    i_reng_tree[i_reng_index]<=i_reng+4'h1;
            
            end
            
        end
    
end
*/




    
        
/*
wire clk_buf2;



BUFG u_baud_clkbuf2 (
    .I(clock),
    .O(clk_buf2)
);
*/
    
    
    wire [operation-2-1:0] clk_buf_dot;

    

reg signed [ancho_bits_datos-1:0] senal_segmentada [3*(N_dot_product+2)-1:0];//[3*operation-1:0];
reg signed [ancho_bits_datos-1:0] filtro_segmentada [(N_dot_product)*3*3-1:0];//[(operation-2)*3*3-1:0];
//integer i_rst_cables_sum;
//(* keep = "true" *) wire [operation-2:0] buffer_gen;



//reg signed [15:0]var_n0,var_n1,var_n2,var_n3,var_n4,var_n5,var_n6,var_n7,datoi_index;
//reg signed datoi_index;
//reg signed [15:0]Res_var[operation-2-1:0];
localparam operation_less2=operation*(N_dot_product);//*( (operation-2));//operation*( (operation-2));
localparam operation_less1=operation*(N_dot_product+1);//*( (operation-1));//operation*( (operation-1));
wire [10:0] ind_filtro_secction={5'h0,ind_filtro,3'h0}+{8'h0,ind_filtro};//ind_filtro*11'h9;
wire [(operation-2)*12-1:0] semilla_senal;
wire [11:0]semilla_senal_lees_2,semilla_senal_lees_1;
assign semilla_senal_lees_2=operation_less2 +i_reng_tree[N_dot_product]+{Contador_secciones,6'h0};
assign semilla_senal_lees_1=operation_less1 +i_reng_tree[N_dot_product+4'h1]+{Contador_secciones,6'h0};
//reg [6:0] semilla_filtro_segmentada[operation-3:0];

localparam [5:0]oper_less2_mu_3=6'h3*( (N_dot_product));//6'h3*( (operation-2));
localparam [5:0]oper_less1_mu_3=6'h3*( (N_dot_product+1));//6'h3*( (operation-1));


//wire [N_dot_product*16-1:0] mem_pre_out;
wire [15:0] mem_pre_out [N_dot_product-1:0];

wire [N_dot_product-1:0]columna_i_comparador;



reg [N_dot_product-1:0] Flat_col_i;
genvar col_i;
genvar i_mem;
generate
	for (col_i = 0; col_i < N_dot_product; col_i = col_i + 1) begin
	    //assign buffer_gen[col_i]= clk_buf2;
	    localparam [6:0] semilla_filtro_segmentada0 = col_i*9;
        localparam [6:0] semilla_filtro_segmentada1 = col_i*9 + 1;
        localparam [6:0] semilla_filtro_segmentada2 = col_i*9 + 2;
        localparam [6:0] semilla_filtro_segmentada3 = col_i*9 + 3;
        localparam [6:0] semilla_filtro_segmentada4 = col_i*9 + 4;
        localparam [6:0] semilla_filtro_segmentada5 = col_i*9 + 5;
        localparam [6:0] semilla_filtro_segmentada6 = col_i*9 + 6;
        localparam [6:0] semilla_filtro_segmentada7 = col_i*9 + 7;
        localparam [6:0] semilla_filtro_segmentada8 = col_i*9 + 8;
        
        localparam [5:0] semilla_senal_segmentada0 = 3*(col_i);
        localparam [5:0] semilla_senal_segmentada1 = 3*(col_i) + 1;
        localparam [5:0] semilla_senal_segmentada2 = 3*(col_i) + 2;
        localparam [5:0] semilla_senal_segmentada3 = 3*(col_i) + 3;
        localparam [5:0] semilla_senal_segmentada4 = 3*(col_i) + 4;
        localparam [5:0] semilla_senal_segmentada5 = 3*(col_i) + 5;
        localparam [5:0] semilla_senal_segmentada6 = 3*(col_i) + 6;
        localparam [5:0] semilla_senal_segmentada7 = 3*(col_i) + 7;
        localparam [5:0] semilla_senal_segmentada8 = 3*(col_i) + 8;
        
        localparam [5:0]semilla_senal_segmentada_lees2_0=6'd3*operation_lees_2;
        localparam [5:0]semilla_senal_segmentada_lees2_1=6'd3*operation_lees_2+6'h1;
        localparam [5:0]semilla_senal_segmentada_lees2_2=6'd3*operation_lees_2+6'h2;
        localparam [5:0]semilla_senal_segmentada_lees1_0=6'd3*operation_lees_1;
        localparam [5:0]semilla_senal_segmentada_lees1_1=6'd3*operation_lees_1+6'h1;
        localparam [5:0]semilla_senal_segmentada_lees1_2=6'd3*operation_lees_1+6'h2;
        
        localparam [7:0] semilla_mem_out =col_i*8'd16;
        localparam [7:0]col_mul_12=col_i*8'd12;
	  //assign semilla_filtro_segmentada[col_i]={col_i,3'd0}+{3'd0,col_i};//col_i*7'd9;//
	  localparam [11:0] opera_mul_col_i=operation*( col_i);
	  /*BUFG u_bufg (
		  .I(clk_buf2),
		  .O(clk_buf_dot[col_i])
        );*/
        
        //BUFG u_bufg (
        //.I(clk_buf2),
        //.O(clk_buf_dot[col_i])
        //);
        //gf180mcu_fd_sc_mcu7t5v0__clkbuf_2 u_bufg (
		  //.I(clk_buf2),
		  //.Z(clk_buf_dot[col_i])
        //);
        
       assign semilla_senal[col_mul_12 +: 12]=opera_mul_col_i +i_reng_tree[col_i]+{Contador_secciones,6'h0};
       assign columna_i_comparador[col_i]=({Contador_secciones,2'h0}+col_i <=(col+4'd2));
	   //punt_mo u_punt_mo(
	   punt_mo_seg u_punt_mo(
				    .data1(senal_segmentada[semilla_senal_segmentada0]),
                    .data2(filtro_segmentada[semilla_filtro_segmentada0]),//filtro[ind_filtro*10'h9+0]),
                    .data3(bias[{ind_filtro,4'h0} +: 16]),
                    
                    
                    .data6(senal_segmentada[semilla_senal_segmentada2 ]),
                    .data7(filtro_segmentada[semilla_filtro_segmentada2]),//filtro[ind_filtro*10'h9+(10'h1+10'h1)]),
                    .data4(senal_segmentada[semilla_senal_segmentada1]),
                    .data5(filtro_segmentada[semilla_filtro_segmentada1]),//filtro[ind_filtro*10'h9+10'h1]),
                    
                    
                    
                    .data10(senal_segmentada[semilla_senal_segmentada4]),
                    .data11(filtro_segmentada[semilla_filtro_segmentada4]),//filtro[ind_filtro*10'h9+(10'h3+10'h1)]),
                    .data8(senal_segmentada[semilla_senal_segmentada3]),
                    .data9(filtro_segmentada[semilla_filtro_segmentada3]),//filtro[ind_filtro*10'h9+10'h3]),
                    
                    
                    
                    .data14(senal_segmentada[semilla_senal_segmentada6]),
                    .data15(filtro_segmentada[semilla_filtro_segmentada6]),//filtro[ind_filtro*10'h9+(10'h5+10'h1)]),
                    .data12(senal_segmentada[semilla_senal_segmentada5]),
                    .data13(filtro_segmentada[semilla_filtro_segmentada5]),//filtro[ind_filtro*10'h9+10'h5]),
                    
                    
                    
                    .data18(senal_segmentada[semilla_senal_segmentada8]),
                    .data19(filtro_segmentada[semilla_filtro_segmentada8]),//filtro[ind_filtro*10'h9+(10'h7+10'h1)]),
                    .data16(senal_segmentada[semilla_senal_segmentada7]),
                    .data17(filtro_segmentada[semilla_filtro_segmentada7]),//filtro[ind_filtro*10'h9+10'h7])
                    .clock(clock),//clk_buf_dot[col_i]),
                    .rst(rst),
                    .Flat(Flat & Flat_col_i[col_i]),
                    //.out_reg_mult(mem_pre_out[semilla_mem_out +: 16]),//col_i*8'd16
                    .out_reg_mult(mem_pre_out[col_i]),//col_i*8'd16
                    .flat_out(flat_procesar[col_i])
				);
				
		//always @(posedge buffer_gen[col_i],negedge rst) begin
		always @(posedge clock,negedge rst) begin
			if (!rst)
			begin
				//mem_out[col_i]<=16'h0;
				senal_segmentada[semilla_senal_segmentada0]<={ancho_bits_datos{1'h0}};//5'd3*( col_i%operation_lees_2)+5'd0
				senal_segmentada[semilla_senal_segmentada1]<={ancho_bits_datos{1'h0}};//5'd3*( col_i%operation_lees_2)+5'd1
				senal_segmentada[semilla_senal_segmentada2]<={ancho_bits_datos{1'h0}};//5'd3*( col_i%operation_lees_2)+5'd2
				if(col_i==N_dot_product-1)begin
				
                    senal_segmentada[semilla_senal_segmentada_lees2_0]<={ancho_bits_datos{1'h0}};
                    senal_segmentada[semilla_senal_segmentada_lees2_1]<={ancho_bits_datos{1'h0}};
                    senal_segmentada[semilla_senal_segmentada_lees2_2]<={ancho_bits_datos{1'h0}};
                    senal_segmentada[semilla_senal_segmentada_lees1_0]<={ancho_bits_datos{1'h0}};
                    senal_segmentada[semilla_senal_segmentada_lees1_1]<={ancho_bits_datos{1'h0}};
                    senal_segmentada[semilla_senal_segmentada_lees1_2]<={ancho_bits_datos{1'h0}};
                end
                //if(col_i==0)begin    
                    filtro_segmentada[semilla_filtro_segmentada0]<={ancho_bits_datos{1'h0}};
                    filtro_segmentada[semilla_filtro_segmentada1]<={ancho_bits_datos{1'h0}};
                    filtro_segmentada[semilla_filtro_segmentada2]<={ancho_bits_datos{1'h0}};
                    filtro_segmentada[semilla_filtro_segmentada3]<={ancho_bits_datos{1'h0}};
                    filtro_segmentada[semilla_filtro_segmentada4]<={ancho_bits_datos{1'h0}};
                    filtro_segmentada[semilla_filtro_segmentada5]<={ancho_bits_datos{1'h0}};
                    filtro_segmentada[semilla_filtro_segmentada6]<={ancho_bits_datos{1'h0}};
                    filtro_segmentada[semilla_filtro_segmentada7]<={ancho_bits_datos{1'h0}};
                    filtro_segmentada[semilla_filtro_segmentada8]<={ancho_bits_datos{1'h0}};
                    
				//end
				Flat_col_i[col_i]<=1'b0;
			end 
			
			else if (Flat_anterior & columna_i_comparador[col_i])
                begin
                    Flat_col_i[col_i]<=({Contador_secciones,2'h0}+col_i <=(col));//1'h1;
                //semilla_filtro_segmentada[col_i]={col_i,3'd0}+{3'd0,col_i};//col_i*7'd9;//
                    senal_segmentada[semilla_senal_segmentada0]         <=senal[((semilla_senal[col_mul_12 +: 12]<<bits_input)      ) +: ancho_bits_datos ];
                    senal_segmentada[semilla_senal_segmentada1]         <=senal[((semilla_senal[col_mul_12 +: 12]<<bits_input)+  {8'd1,{bits_input{1'd0}}}  ) +: ancho_bits_datos ];
                    senal_segmentada[semilla_senal_segmentada2]         <=senal[((semilla_senal[col_mul_12 +: 12]<<bits_input)+  {8'd2,{bits_input{1'd0}}}  ) +: ancho_bits_datos ];
                    if(col_i==N_dot_product-1)// & (col_i+{Contador_secciones,2'h0}<operation-2))
                    begin                                         
                        senal_segmentada[oper_less2_mu_3      ]         <=senal[({semilla_senal_lees_2[7:0],{bits_input{1'd0}}}      ) +: ancho_bits_datos ];
                        senal_segmentada[oper_less2_mu_3+ 6'h1]         <=senal[({semilla_senal_lees_2[7:0],{bits_input{1'd0}}}+ {8'd1,{bits_input{1'd0}}}  ) +: ancho_bits_datos ];
                        senal_segmentada[oper_less2_mu_3+ 6'h2]         <=senal[({semilla_senal_lees_2[7:0],{bits_input{1'd0}}}+ {8'd2,{bits_input{1'd0}}} ) +: ancho_bits_datos ];
                        
                        senal_segmentada[oper_less1_mu_3      ]         <=senal[({semilla_senal_lees_1[7:0],{bits_input{1'd0}}}     ) +: ancho_bits_datos ];
                        senal_segmentada[oper_less1_mu_3+ 6'h1]         <=senal[({semilla_senal_lees_1[7:0],{bits_input{1'd0}}}+ {8'd1,{bits_input{1'd0}}}  ) +: ancho_bits_datos ];
                        senal_segmentada[oper_less1_mu_3+ 6'h2]         <=senal[({semilla_senal_lees_1[7:0],{bits_input{1'd0}}}+ {8'd2,{bits_input{1'd0}}}  ) +: ancho_bits_datos ];
                        
                        
                    end
                    
                    //if(col_i==0)begin
                    
                        filtro_segmentada[semilla_filtro_segmentada0] <= filtro[({ind_filtro_secction[6:0],{bits_input{1'd0}}}) +: ancho_bits_datos];
                        filtro_segmentada[semilla_filtro_segmentada1] <= filtro[(({ind_filtro_secction[6:0],{bits_input{1'd0}}}+{7'd1,{bits_input{1'd0}}})) +: ancho_bits_datos];
                        filtro_segmentada[semilla_filtro_segmentada2] <= filtro[(({ind_filtro_secction[6:0],{bits_input{1'd0}}}+{7'd2,{bits_input{1'd0}}})) +: ancho_bits_datos];
                        filtro_segmentada[semilla_filtro_segmentada3] <= filtro[(({ind_filtro_secction[6:0],{bits_input{1'd0}}}+{7'd3,{bits_input{1'd0}}})) +: ancho_bits_datos];
                        filtro_segmentada[semilla_filtro_segmentada4] <= filtro[(({ind_filtro_secction[6:0],{bits_input{1'd0}}}+{7'd4,{bits_input{1'd0}}})) +: ancho_bits_datos];
                        filtro_segmentada[semilla_filtro_segmentada5] <= filtro[(({ind_filtro_secction[6:0],{bits_input{1'd0}}}+{7'd5,{bits_input{1'd0}}})) +: ancho_bits_datos];
                        filtro_segmentada[semilla_filtro_segmentada6] <= filtro[(({ind_filtro_secction[6:0],{bits_input{1'd0}}}+{7'd6,{bits_input{1'd0}}})) +: ancho_bits_datos];
                        filtro_segmentada[semilla_filtro_segmentada7] <= filtro[(({ind_filtro_secction[6:0],{bits_input{1'd0}}}+{7'd7,{bits_input{1'd0}}})) +: ancho_bits_datos];
                        filtro_segmentada[semilla_filtro_segmentada8] <= filtro[(({ind_filtro_secction[6:0],{bits_input{1'd0}}}+{7'd8,{bits_input{1'd0}}})) +: ancho_bits_datos];
                    
                    
                
                end
                else
                    Flat_col_i[col_i]<=1'h0;
                    
                /*if (flat_procesar[col_i])begin
			        mem_out[({Contador_sec_post_calculos,6'h0}+semilla_mem_out) +: 16]<=mem_pre_out[col_i];//{Contador_secciones,6'h0}+
			        //mem_out[({Contador_sec_post_calculos,6'h0}+semilla_mem_out) +: 16]<=mem_pre_out[semilla_mem_out +: 16];//{Contador_secciones,6'h0}+
			        
			        
			    end
			end*/
		end
		
		
		for(i_mem=0;i_mem<4;i_mem=i_mem+1)begin

			localparam index_mem_out= (semilla_mem_out+i_mem*16*4);
			localparam comaparador_mem_out=(col_i+i_mem*4);
			always @(posedge clock) begin//clk_buf_dot[0]) begin
              
            
                
                    
                    if (flat_procesar[col_i])begin
			             if(comaparador_mem_out==({Contador_sec_post_calculos,2'h0}+col_i))
			             begin
			                 mem_out[index_mem_out +: 16]<=mem_pre_out[col_i];
			             end
			             //mem_out[({Contador_sec_post_calculos,6'h0}+semilla_mem_out) +: 16]<=mem_pre_out[col_i];//{Contador_secciones,6'h0}+
			             //mem_out[({Contador_sec_post_calculos,6'h0}+semilla_mem_out) +: 16]<=mem_pre_out[semilla_mem_out +: 16];//{Contador_secciones,6'h0}+
			        end
			    
			  end
            
		end
	end
endgenerate


endmodule
