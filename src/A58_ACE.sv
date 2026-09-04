// SPDX-FileCopyrightText: 2026 Chipathon 2026 workshop
// SPDX-License-Identifier: Apache-2.0
//
// Padframe-facing top wrapper for A58_ACE.
// Wraps con32_one_instruction and exposes exactly the pin set + names 
// required by A58_ACE.def.

`default_nettype none

module A58_ACE (
    `ifdef USE_POWER_PINS
        inout VSS,
        inout VDD,
    `endif
    // Inputs puros
    input  logic rst,
    output logic rst_PU,
    output logic rst_PD,

    input  logic clk_ref,
    output logic clk_ref_PU,
    output logic clk_ref_PD,

    // Bidir: rx_sample_pulse (Salida)
    input  logic rx_sample_pulse_IN,
    output logic rx_sample_pulse_OUT,
    output logic rx_sample_pulse_OE,
    output logic rx_sample_pulse_CS,
    output logic rx_sample_pulse_SL,
    output logic rx_sample_pulse_IE,
    output logic rx_sample_pulse_PU,
    output logic rx_sample_pulse_PD,

    // Bidir: rxd (Entrada)
    input  logic rxd_IN,
    output logic rxd_out, 
    output logic rxd_OE,
    output logic rxd_CS,
    output logic rxd_SL,
    output logic rxd_IE,
    output logic rxd_PU,
    output logic rxd_PD,

    // Bidir: rxd_out (Salida)
    input  logic rxd_out_IN,
    output logic rxd_out_OUT,
    output logic rxd_out_OE,
    output logic rxd_out_CS,
    output logic rxd_out_SL,
    output logic rxd_out_IE,
    output logic rxd_out_PU,
    output logic rxd_out_PD,

    // Bidir: tx_busy (Salida)
    input  logic tx_busy_IN,
    output logic tx_busy_OUT,
    output logic tx_busy_OE,
    output logic tx_busy_CS,
    output logic tx_busy_SL,
    output logic tx_busy_IE,
    output logic tx_busy_PU,
    output logic tx_busy_PD,

    // Bidir: txd (Salida)
    input  logic txd_IN,
    output logic txd_OUT,
    output logic txd_OE,
    output logic txd_CS,
    output logic txd_SL,
    output logic txd_IE,
    output logic txd_PU,
    output logic txd_PD
);

    // -------------------------------------------------------------------------
    // Configuración de Entradas Puras (Inputs)
    // -------------------------------------------------------------------------
    assign rst_PU     = 1'b0;
    assign rst_PD     = 1'b0;

    assign clk_ref_PU = 1'b0;
    assign clk_ref_PD = 1'b0;

    // -------------------------------------------------------------------------
    // Configuración de Pads Bidireccionales
    // -------------------------------------------------------------------------

    // 1. rxd (ENTRADA DEDICADA)
    assign rxd_OE                  = 1'b0; // Output Enable OFF
    assign rxd_IE                  = 1'b1; // Input Enable ON
    assign rxd_CS                  = 1'b0; // CMOS
    assign rxd_SL                  = 1'b1;
    assign rxd_PU                  = 1'b0; // Pull-up activo para mantener línea UART en alto si se desconecta
    assign rxd_PD                  = 1'b0;
    assign rxd_out                 = 1'b0;

    // 2. txd (SALIDA DEDICADA)
    assign txd_OE                  = 1'b1; // Output Enable ON
    assign txd_IE                  = 1'b0; // Input Enable OFF
    assign txd_CS                  = 1'b0;
    assign txd_SL                  = 1'b0; // Slew rate rápido
    assign txd_PU                  = 1'b0;
    assign txd_PD                  = 1'b0;

    // 3. rxd_out (SALIDA DEDICADA)
    assign rxd_out_OE              = 1'b1;
    assign rxd_out_IE              = 1'b0;
    assign rxd_out_CS              = 1'b0;
    assign rxd_out_SL              = 1'b0;
    assign rxd_out_PU              = 1'b0;
    assign rxd_out_PD              = 1'b0;

    // 4. tx_busy (SALIDA DEDICADA)
    assign tx_busy_OE              = 1'b1;
    assign tx_busy_IE              = 1'b0;
    assign tx_busy_CS              = 1'b0;
    assign tx_busy_SL              = 1'b0;
    assign tx_busy_PU              = 1'b0;
    assign tx_busy_PD              = 1'b0;

    // 5. rx_sample_pulse (SALIDA DEDICADA)
    assign rx_sample_pulse_OE      = 1'b1;
    assign rx_sample_pulse_IE      = 1'b0;
    assign rx_sample_pulse_CS      = 1'b0;
    assign rx_sample_pulse_SL      = 1'b0;
    assign rx_sample_pulse_PU      = 1'b0;
    assign rx_sample_pulse_PD      = 1'b0;

    // -------------------------------------------------------------------------
    // Manejo de Entradas no utilizadas de los Pads Bidireccionales
    // -------------------------------------------------------------------------
    logic _unused_in;
    assign _unused_in = ^ {
        rx_sample_pulse_IN,
        rxd_out_IN,
        tx_busy_IN,
        txd_IN
    };

    // -------------------------------------------------------------------------
    // Instancia del Macro de Usuario (con32_one_instruction)
    // -------------------------------------------------------------------------
    con32_one_instruction con32_one_instruction_u (
        .clk_ref          (clk_ref),
        .rst              (rst),
        .rxd              (rxd_IN),               // Proviene de la entrada del pad rxd
        .txd              (txd_OUT),              // Salida hacia el pad txd
        .rxd_out          (rxd_out_OUT),          // Salida hacia el pad rxd_out
        .tx_busy          (tx_busy_OUT),          // Salida hacia el pad tx_busy
        .rx_sample_pulse  (rx_sample_pulse_OUT)   // Salida hacia el pad rx_sample_pulse
    );

endmodule

`default_nettype wire
