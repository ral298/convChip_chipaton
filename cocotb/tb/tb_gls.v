
`timescale 1ns / 1ps

module tb ();

    // 1. Configuración del volcado de ondas idéntico a tu ejemplo
    initial begin
        $dumpfile("dump_gls.vcd");
        $dumpvars(0, tb); // Al apuntar a 'tb', grabará este módulo y todo lo que instancie adentro
        #1;
    end

    // 2. Declaración de señales que controlará Cocotb desde Python
    reg clk_ref;
    reg rst;
    reg rxd;

    // Cables para monitorear las salidas (si tu diseño las tiene)
    wire rxd_out;
    wire rx_sample_pulse;
    wire tx_busy;
    wire txd;

    // 3. Llamado (Instanciación) de tu módulo principal usando los puertos correctos
    con32_one_instruction user_project (
        .clk_ref         (clk_ref),
        .rst             (rst),
        .rxd             (rxd),
        .rxd_out         (rxd_out),         // Si no usas estas salidas en Python, igual déjalas conectadas a sus wires
        .rx_sample_pulse (rx_sample_pulse),
        .tx_busy         (tx_busy),
        .txd             (txd)
    );

endmodule
