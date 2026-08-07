###############################################################################
# Created by write_sdc
###############################################################################
current_design con32_one_instruction
###############################################################################
# Timing Constraints
###############################################################################
create_clock -name clk_ref -period 25.0000 [get_ports {clk_ref}]
set_clock_transition 0.1500 [get_clocks {clk_ref}]
set_clock_uncertainty 0.2500 clk_ref
set_propagated_clock [get_clocks {clk_ref}]
set_input_delay 5.0000 -clock [get_clocks {clk_ref}] -add_delay [get_ports {rst}]
set_input_delay 5.0000 -clock [get_clocks {clk_ref}] -add_delay [get_ports {rxd}]
set_output_delay 5.0000 -clock [get_clocks {clk_ref}] -add_delay [get_ports {rx_sample_pulse}]
set_output_delay 5.0000 -clock [get_clocks {clk_ref}] -add_delay [get_ports {rxd_out}]
set_output_delay 5.0000 -clock [get_clocks {clk_ref}] -add_delay [get_ports {tx_busy}]
set_output_delay 5.0000 -clock [get_clocks {clk_ref}] -add_delay [get_ports {txd}]
###############################################################################
# Environment
###############################################################################
set_load -pin_load 0.0729 [get_ports {rx_sample_pulse}]
set_load -pin_load 0.0729 [get_ports {rxd_out}]
set_load -pin_load 0.0729 [get_ports {tx_busy}]
set_load -pin_load 0.0729 [get_ports {txd}]
set_driving_cell -lib_cell gf180mcu_fd_sc_mcu7t5v0__inv_4 -pin {ZN} -input_transition_rise 0.0000 -input_transition_fall 0.0000 [get_ports {clk_ref}]
set_driving_cell -lib_cell gf180mcu_fd_sc_mcu7t5v0__inv_1 -pin {ZN} -input_transition_rise 0.0000 -input_transition_fall 0.0000 [get_ports {rst}]
set_driving_cell -lib_cell gf180mcu_fd_sc_mcu7t5v0__inv_1 -pin {ZN} -input_transition_rise 0.0000 -input_transition_fall 0.0000 [get_ports {rxd}]
###############################################################################
# Design Rules
###############################################################################
set_max_transition 2.5000 [current_design]
set_max_capacitance 0.2000 [current_design]
set_max_fanout 24.0000 [current_design]
