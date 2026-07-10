module punt_mo_seg(
   input [7:0] data1,data2,data4,data5,data6,data7,
                 data8,data9,data10,data11,data12,data13,
                 data14,data15,data16,data17,data18,data19,
   input [15:0]data3,

   input clock,
   input rst,
   input Flat,
    output reg flat_out,
   output  [15:0] out_reg_mult
);

//====================================================
// MULTIPLICACIONES
//====================================================

wire [15:0] mult1_w,mult2_w,mult3_w,mult4_w,mult5_w;
wire [15:0] mult6_w,mult7_w,mult8_w,mult9_w;


mult_16b_bf u_mult1(.A(data1),  .B(data2),  .result(mult1_w));
mult_16b_bf u_mult2(.A(data4),  .B(data5),  .result(mult2_w));
mult_16b_bf u_mult3(.A(data6),  .B(data7),  .result(mult3_w));
mult_16b_bf u_mult4(.A(data8),  .B(data9),  .result(mult4_w));
mult_16b_bf u_mult5(.A(data10), .B(data11), .result(mult5_w));
mult_16b_bf u_mult6(.A(data12), .B(data13), .result(mult6_w));
mult_16b_bf u_mult7(.A(data14), .B(data15), .result(mult7_w));
mult_16b_bf u_mult8(.A(data16), .B(data17), .result(mult8_w));
mult_16b_bf u_mult9(.A(data18), .B(data19), .result(mult9_w));

//====================================================
// REG 0
//====================================================

reg [15:0] mult1_r,mult2_r,mult3_r,mult4_r,mult5_r;
reg [15:0] mult6_r,mult7_r,mult8_r,mult9_r;
reg [15:0] data3_r;


reg flat_r0;

always @(posedge clock or negedge rst) begin
    if(!rst) begin
        mult1_r <= 16'h0;
        mult2_r <= 16'h0;
        mult3_r <= 16'h0;
        mult4_r <= 16'h0;
        mult5_r <= 16'h0;
        mult6_r <= 16'h0;
        mult7_r <= 16'h0;
        mult8_r <= 16'h0;
        mult9_r <= 16'h0;
        flat_r0 <= 1'b0;
        data3_r   <= 16'h0;
    end
    else begin
        if (Flat) begin
            mult1_r <= mult1_w;
            mult2_r <= mult2_w;
            mult3_r <= mult3_w;
            mult4_r <= mult4_w;
            mult5_r <= mult5_w;
            mult6_r <= mult6_w;
            mult7_r <= mult7_w;
            mult8_r <= mult8_w;
            mult9_r <= mult9_w;
            data3_r <=data3;
        end
        flat_r0 <= Flat;
    end
end

//====================================================
// NIVEL 1 SUMAS
//====================================================

wire [15:0] sum1_w,sum2_w,sum3_w,sum4_w;

suma_16b u_sum1(.A(mult1_r), .B(data3_r),   .result(sum1_w));
suma_16b u_sum2(.A(mult2_r), .B(mult3_r), .result(sum2_w));
suma_16b u_sum3(.A(mult4_r), .B(mult5_r), .result(sum3_w));
suma_16b u_sum4(.A(mult6_r), .B(mult7_r), .result(sum4_w));

//====================================================
// REG 1
//====================================================

reg [15:0] sum1_r,sum2_r,sum3_r,sum4_r;
reg [15:0] mult8_rr,mult9_rr;

reg flat_r1;

always @(posedge clock or negedge rst) begin
    if(!rst) begin
        sum1_r <= 16'h0;
        sum2_r <= 16'h0;
        sum3_r <= 16'h0;
        sum4_r <= 16'h0;
        mult8_rr <= 16'h0;
        mult9_rr <= 16'h0;
        flat_r1 <= 1'b0;
    end
    else begin
        if (flat_r0) begin
            sum1_r   <= sum1_w;
            sum2_r   <= sum2_w;
            sum3_r   <= sum3_w;
            sum4_r   <= sum4_w;
    
            mult8_rr <= mult8_r;
            mult9_rr <= mult9_r;
    
            
        end
        flat_r1 <= flat_r0;
    end
end

//====================================================
// NIVEL 2
//====================================================

wire [15:0] sum12_w,sum34_w,summult89_w;

suma_16b u_sum12(.A(sum1_r), .B(sum2_r), .result(sum12_w));
suma_16b u_sum34(.A(sum3_r), .B(sum4_r), .result(sum34_w));
suma_16b u_summult89(.A(mult8_rr), .B(mult9_rr), .result(summult89_w));

//====================================================
// REG 2
//====================================================

reg [15:0] sum12_r,sum34_r,summult89_r;

reg flat_r2;

always @(posedge clock or negedge rst) begin
    if(!rst) begin
        sum12_r <= 16'h0;
        sum34_r <= 16'h0;
        summult89_r <= 16'h0;
        flat_r2 <= 1'b0;
    end
    else begin
        if (flat_r1) begin
            sum12_r     <= sum12_w;
            sum34_r     <= sum34_w;
            summult89_r <= summult89_w;
        end
        flat_r2 <= flat_r1;    
    end
    
end

//====================================================
// NIVEL 3
//====================================================

wire [15:0] sum1234_w;

suma_16b u_sum1234(
    .A(sum12_r),
    .B(sum34_r),
    .result(sum1234_w)
);

//====================================================
// REG 3
//====================================================

reg [15:0] sum1234_r,summult89_rr;



always @(posedge clock or negedge rst) begin
    if(!rst) begin
        sum1234_r   <= 16'h0;
        flat_out    <= 1'b0;
        summult89_rr<= 16'h0;
    end
    else begin 
        if (flat_r2) begin
            sum1234_r   <= sum1234_w;
            summult89_rr<=summult89_r;
        end
        flat_out <= flat_r2;
    end
end

//====================================================
// NIVEL 4
//====================================================

wire [15:0] sumTotal_w;

suma_16b u_sumTotal(
    .A(sum1234_r),
    .B(summult89_rr),
    .result(out_reg_mult)
);





/*


reg [15:0] sum1234_r;

reg flat_r3;

always @(posedge clock or negedge rst) begin
    if(!rst) begin
        sum1234_r <= 16'h0;
        flat_r3 <= 1'b0;
    end
    else begin 
        if (flat_r2)
            sum1234_r <= sum1234_w;
    
        flat_r3 <= flat_r2;
    end
end

//====================================================
// NIVEL 4
//====================================================

wire [15:0] sumTotal_w;

suma_16b u_sumTotal(
    .A(sum1234_r),
    .B(summult89_r),
    .result(sumTotal_w)
);

//====================================================
// OUTPUT
//====================================================

always @(posedge clock or negedge rst) begin
    if(!rst) begin
        out_reg_mult <= 16'h0;
        flat_out<=1'b0;
    end
    else begin 
        if(flat_r3)
            out_reg_mult <= sumTotal_w;
        
        flat_out<=flat_r3;
    end
end
*/

endmodule
