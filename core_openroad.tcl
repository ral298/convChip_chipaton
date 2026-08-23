set CORNER "ss_125C_4v50"
set PDK_PATH "./gf180mcu/gf180mcuD/libs.ref"

# Librerías
read_lib "$PDK_PATH/gf180mcu_fd_sc_mcu7t5v0/lib/gf180mcu_fd_sc_mcu7t5v0__${CORNER}.lib"

# Macro Core Design
read_db "./librelane/build/con32_one_instruction/odb/con32_one_instruction.odb"
read_spef "./librelane/build/con32_one_instruction/spef/max/con32_one_instruction.max.spef"
read_sdc "./librelane/build/con32_one_instruction/sdc/con32_one_instruction.sdc"

puts "\n========================================================"
puts "       REPORTE INTERNO DEL CORE (REG -> REG)            "
puts "========================================================"
report_checks -path_delay max -endpoint_count 50 -format full_clock_expanded -digits 4
report_checks -path_delay min -endpoint_count 20 -format full_clock_expanded -digits 4
report_wns
report_tns
report_clock_min_period
exit
