# ==============================================================================
# SDC Adaptado para LibreLane / OpenROAD (GF180MCU - 50 MHz)
# ==============================================================================

set_units -time ns -resistance kOhm -capacitance pF -voltage V -current mA

# ------------------------------------------------------------------------------
# 1. Definición del Reloj Principal
# ------------------------------------------------------------------------------
create_clock [get_ports clk_ref] -period 20.0 -waveform {0.0 10.0}

# Incertidumbre realista (200 ps es estándar y suficiente para 50 MHz en GF180)
set_clock_uncertainty -setup 0.2 [get_clocks clk_ref]
set_clock_uncertainty -hold 0.1  [get_clocks clk_ref]

# Reloj con propensión real (CTS propaga el reloj real automáticamente)
set_propagated_clock [get_clocks clk_ref]

# ------------------------------------------------------------------------------
# 2. Delays de Entrada y Salida (4 ns max es el 20% del periodo de 20 ns)
# ------------------------------------------------------------------------------
set_input_delay  -clock clk_ref -max 4.0 [get_ports {rxd rst}]
set_input_delay  -clock clk_ref -min 0.5 [get_ports {rxd rst}]

set_output_delay -clock clk_ref -max 4.0 [get_ports {txd rxd_out tx_busy rx_sample_pulse}]
set_output_delay -clock clk_ref -min 0.5 [get_ports {txd rxd_out tx_busy rx_sample_pulse}]

# ------------------------------------------------------------------------------
# 3. Transiciones y Cargas en Pines
# ------------------------------------------------------------------------------
# Relajamos suavemente la transición de entrada del reloj para evitar pesimismo en SS
set_input_transition -max 0.5 [get_ports {rxd rst clk_ref}]
set_input_transition -min 0.1 [get_ports {rxd rst clk_ref}]

# Carga externa prudente en salidas (40 fF)
set_load -pin_load 0.04 [get_ports {txd rxd_out tx_busy rx_sample_pulse}]
