set CORNER "ss_125C_4v50"
set PDK_PATH "./gf180mcu/gf180mcuD/libs.ref"

# Librerías
read_lib "$PDK_PATH/gf180mcu_fd_sc_mcu7t5v0/lib/gf180mcu_fd_sc_mcu7t5v0__${CORNER}.lib"
read_lib "$PDK_PATH/gf180mcu_fd_io/lib/gf180mcu_fd_io__${CORNER}.lib"

read_lib "$PDK_PATH/gf180mcu_fd_io/lib/gf180mcu_ws_io__${CORNER}.lib"

# Liberty caracterizada de la Macro
read_lib "./librelane/build/con32_one_instruction/lib/max_${CORNER}/con32_one_instruction__max_${CORNER}.lib"

# Top Level Design
read_db "./final/odb/chip_top.odb"
read_spef "./final/spef/max/chip_top.max.spef"
read_sdc "./final/sdc/chip_top.sdc"

puts "\n========================================================"
puts "       REPORTE TOP-LEVEL (PADS <-> FRONTERA CORE)       "
puts "========================================================"
report_checks -path_delay min_max -format full_clock_expanded -digits 4
report_wns
report_tns
report_clock_min_period
exit
