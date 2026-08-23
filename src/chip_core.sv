// SPDX-FileCopyrightText: 2026 Chipathon 2026 workshop
// SPDX-License-Identifier: Apache-2.0
//
// Minimal chip_core for the Chipathon 2026 workshop padring slot.
// The emphasis of this slot is the padring itself (60 analog + 20
// bidir + 4/4 power + clk/rst_n); the core is intentionally trivial:
// a free-running counter whose state drives the 20 bidir pads. The
// 60 analog pads are routed straight through to analog[] and stay
// unconnected at the core level (the intent is that a downstream
// design wires them to custom analog IP later).

`default_nettype none

module chip_core #(
    parameter NUM_INPUT_PADS,
    parameter NUM_BIDIR_PADS,
    parameter NUM_ANALOG_PADS
    )(
    `ifdef USE_POWER_PINS
    inout  wire VDD,
    inout  wire VSS,
    `endif

    input  wire clk,       // clock
    input  wire rst_n,     // reset (active low)

    input  wire [NUM_INPUT_PADS-1:0] input_in,   // Input value
    output wire [NUM_INPUT_PADS-1:0] input_pu,   // Pull-up
    output wire [NUM_INPUT_PADS-1:0] input_pd,   // Pull-down

    input  wire [NUM_BIDIR_PADS-1:0] bidir_in,   // Input value
    output wire [NUM_BIDIR_PADS-1:0] bidir_out,  // Output value
    output wire [NUM_BIDIR_PADS-1:0] bidir_oe,   // Output enable
    output wire [NUM_BIDIR_PADS-1:0] bidir_cs,   // Input type (0=CMOS, 1=Schmitt)
    output wire [NUM_BIDIR_PADS-1:0] bidir_sl,   // Slew rate (0=fast, 1=slow)
    output wire [NUM_BIDIR_PADS-1:0] bidir_ie,   // Input enable
    output wire [NUM_BIDIR_PADS-1:0] bidir_pu,   // Pull-up
    output wire [NUM_BIDIR_PADS-1:0] bidir_pd,   // Pull-down

    inout  wire [NUM_ANALOG_PADS-1:0] analog    // Analog
);

    // Disable pull-up and pull-down on any discrete input pads.
    assign input_pu = '0;
    assign input_pd = '0;

// -------------------------------------------------------------------------
    // Señales de Conexión del Macro
    // -------------------------------------------------------------------------
    wire rxd_wire;
    wire rst_active_high;
    wire txd_wire;
    wire rxd_out_wire;
    wire tx_busy_wire;
    wire rx_sample_pulse_wire;

    // Invertir reset: chip_core recibe rst_n (activo en 0), el macro usa rst (activo en 1)
    assign rxd_wire        = bidir_in[0];



    // Drive the bidir pads as outputs (CMOS buffer, fast slew).
    //assign bidir_oe = '1;
    // Output Enable (1 = Salida, 0 = Entrada/Hi-Z)
    assign bidir_oe[0]   = 1'b0;          // RXD es entrada
    assign bidir_oe[1]   = 1'b1;          // TXD es salida
    assign bidir_oe[2]   = 1'b1;          // rxd_out (LED) es salida
    assign bidir_oe[3]   = 1'b1;          // tx_busy (LED) es salida
    assign bidir_oe[4]   = 1'b1;          // rx_sample_pulse (LED) es salida
    assign bidir_oe[NUM_BIDIR_PADS-1:5] = '1;

//    assign bidir_ie = ~bidir_oe;
// Input Enable (1 = Receptor digital activo)
    assign bidir_ie[0]   = 1'b1;          // Habilitar lectura para RXD
    assign bidir_ie[NUM_BIDIR_PADS-1:1] = '0;
    
    //assign bidir_cs = '0;
    // Schmitt trigger (1 = Schmitt en RXD para eliminar ruido)
    assign bidir_cs[0]   = 1'b0;
    assign bidir_cs[NUM_BIDIR_PADS-1:1] = '0;
//    assign bidir_pu = '0;    
// Pull-up / Pull-down (Pull-up en RXD para mantener UART inactiva en '1' si se desconecta)
    assign bidir_pu[0]   = 1'b0;
    assign bidir_pu[NUM_BIDIR_PADS-1:1] = '0;
    
    //assign bidir_sl = '0;
// Slew rate (0 = rápido para TXD, 1 = lento para los LEDs)
    assign bidir_sl[0]   = 1'b0;
    assign bidir_sl[1]   = 1'b0;          // TXD fast slew
    assign bidir_sl[2]   = 1'b0;          // LED fast slew
    assign bidir_sl[3]   = 1'b0;          // LED fast slew
    assign bidir_sl[4]   = 1'b0;          // LED fat slew
    assign bidir_sl[NUM_BIDIR_PADS-1:5] = '0;
    assign bidir_pd = '0;


    assign bidir_out[0] = 1'b0;                  // Inactivo (bit 0 es entrada)
    assign bidir_out[1] = txd_wire;              // TXD principal
    assign bidir_out[2] = rxd_out_wire;          // LED RXD
    assign bidir_out[3] = tx_busy_wire;          // LED TX Busy
    assign bidir_out[4] = rx_sample_pulse_wire;  // LED RX Sample Pulse
    assign bidir_out[NUM_BIDIR_PADS-1:5] = '0;   // Resto de pines a 0

    // Keep synthesis from optimising bidir_in / input_in away.
    logic _unused;
    assign _unused = &{1'b0, bidir_in[NUM_BIDIR_PADS-1:1], input_in};

    /*
    // Free-running counter, width equal to the number of bidir pads.
    logic [NUM_BIDIR_PADS-1:0] count;
    always_ff @(posedge clk) begin
        if (!rst_n) count <= '0;
        else        count <= count + 1;
    end
    assign bidir_out = count;
    */
    
    con32_one_instruction con32_one_instruction_u (
        .clk_ref          (clk),
        .rst              (rst_n),
        .rxd              (rxd_wire),
        .txd              (txd_wire),
        .rxd_out          (rxd_out_wire),
        .tx_busy          (tx_busy_wire),
        .rx_sample_pulse  (rx_sample_pulse_wire)
    );

endmodule

`default_nettype wire
