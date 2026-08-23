
`ifndef GF180MCU_WS_IO_STUBS_V
`define GF180MCU_WS_IO_STUBS_V
module gf180mcu_ws_io__dvdd (
`ifdef USE_POWER_PINS
    inout DVDD,
    inout DVSS,
    inout VSS
`endif
);
endmodule

module gf180mcu_ws_io__dvss (
`ifdef USE_POWER_PINS
    inout DVDD,
    inout DVSS,
    inout VDD
`endif
);
endmodule
`endif
