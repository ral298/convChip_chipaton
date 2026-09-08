
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
    input  wire rst_n,     // reset (activo en bajo)

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

    inout  wire [NUM_ANALOG_PADS-1:0] analog     // Analog
);

    // -------------------------------------------------------------------------
    // Configuración de Entradas Puras Generales (input_pu, input_pd)
    // -------------------------------------------------------------------------
    // El puerto de reset dedicado usa la posición input_in[0] si aplica, 
    // pero los controles PU/PD son gestionados por A58_ACE.
    assign input_pu[0] = 0;
    assign input_pd[0] = 0;

    generate
        if (NUM_INPUT_PADS > 1) begin : g_unused_input_pads
            assign input_pu[NUM_INPUT_PADS-1:1] = '0;
            assign input_pd[NUM_INPUT_PADS-1:1] = '0;
        end
    endgenerate

    // -------------------------------------------------------------------------
    // Cables intermedios para mapear A58_ACE a las señales de chip_core
    // -------------------------------------------------------------------------
    wire rst_pu_w, rst_pd_w;
    wire clk_ref_pu_w, clk_ref_pd_w;

    // -------------------------------------------------------------------------
    // Instancia del top A58_ACE
    // -------------------------------------------------------------------------
    A58_ACE A58_ACE_u (
        `ifdef USE_POWER_PINS
            .VDD                  (VDD),
            .VSS                  (VSS),
        `endif

        // Entradas Dedicadas (Control)
        .rst                  (rst_n),             // Conectado directamente a rst_n del testbench
        .rst_PU               (rst_pu_w),
        .rst_PD               (rst_pd_w),

        .clk_ref              (clk),               // Conectado directamente al reloj clk
        .clk_ref_PU           (clk_ref_pu_w),
        .clk_ref_PD           (clk_ref_pd_w),

        // Pad Bidireccional: rx_sample_pulse -> Indice 4
        .rx_sample_pulse_IN   (bidir_in[4]),
        .rx_sample_pulse_OUT  (bidir_out[4]),
        .rx_sample_pulse_OE   (bidir_oe[4]),
        .rx_sample_pulse_CS   (bidir_cs[4]),
        .rx_sample_pulse_SL   (bidir_sl[4]),
        .rx_sample_pulse_IE   (bidir_ie[4]),
        .rx_sample_pulse_PU   (bidir_pu[4]),
        .rx_sample_pulse_PD   (bidir_pd[4]),

        // Pad Bidireccional: rxd -> Indice 0 (Entrada RXD)
        .rxd_IN               (bidir_in[0]),
        .rxd_out              (bidir_out[0]),
        .rxd_OE               (bidir_oe[0]),
        .rxd_CS               (bidir_cs[0]),
        .rxd_SL               (bidir_sl[0]),
        .rxd_IE               (bidir_ie[0]),
        .rxd_PU               (bidir_pu[0]),
        .rxd_PD               (bidir_pd[0]),

        // Pad Bidireccional: rxd_out -> Indice 2 (Salida monitoreo rxd_out_OUT)
        .rxd_out_IN           (bidir_in[2]),
        .rxd_out_OUT          (bidir_out[2]),
        .rxd_out_OE           (bidir_oe[2]),
        .rxd_out_CS           (bidir_cs[2]),
        .rxd_out_SL           (bidir_sl[2]),
        .rxd_out_IE           (bidir_ie[2]),
        .rxd_out_PU           (bidir_pu[2]),
        .rxd_out_PD           (bidir_pd[2]),

        // Pad Bidireccional: tx_busy -> Indice 3
        .tx_busy_IN           (bidir_in[3]),
        .tx_busy_OUT          (bidir_out[3]),
        .tx_busy_OE           (bidir_oe[3]),
        .tx_busy_CS           (bidir_cs[3]),
        .tx_busy_SL           (bidir_sl[3]),
        .tx_busy_IE           (bidir_ie[3]),
        .tx_busy_PU           (bidir_pu[3]),
        .tx_busy_PD           (bidir_pd[3]),

        // Pad Bidireccional: txd -> Indice 1 (Salida TXD)
        .txd_IN               (bidir_in[1]),
        .txd_OUT              (bidir_out[1]),
        .txd_OE               (bidir_oe[1]),
        .txd_CS               (bidir_cs[1]),
        .txd_SL               (bidir_sl[1]),
        .txd_IE               (bidir_ie[1]),
        .txd_PU               (bidir_pu[1]),
        .txd_PD               (bidir_pd[1])
    );

    // -------------------------------------------------------------------------
    // Mapeo por defecto para los pads bidireccionales no utilizados (> 4)
    // -------------------------------------------------------------------------
    generate
        if (NUM_BIDIR_PADS > 5) begin : g_unused_bidir_pads
            assign bidir_out[NUM_BIDIR_PADS-1:5] = '0;
            assign bidir_oe[NUM_BIDIR_PADS-1:5]  = '0; // Hi-Z por seguridad
            assign bidir_cs[NUM_BIDIR_PADS-1:5]  = '0;
            assign bidir_sl[NUM_BIDIR_PADS-1:5]  = '0;
            assign bidir_ie[NUM_BIDIR_PADS-1:5]  = '0;
            assign bidir_pu[NUM_BIDIR_PADS-1:5]  = '0;
            assign bidir_pd[NUM_BIDIR_PADS-1:5]  = '0;
        end
    endgenerate

    // Prevenir advertencias de síntesis por entradas de pads no leídas
    wire _unused_signals;
    assign _unused_signals = ^{
        clk_ref_pu_w,
        clk_ref_pd_w,
        input_in,
        rst_pu_w,
        rst_pd_w
    };

endmodule

`default_nettype wire
