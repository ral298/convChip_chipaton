set CORNER "ss_125C_4v50"

read_lib ./gf180mcu/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/lib/gf180mcu_fd_sc_mcu7t5v0__ss_125C_4v50.lib
read_lib ./gf180mcu/gf180mcuD/libs.ref/gf180mcu_fd_io/lib/gf180mcu_fd_io__ss_125C_4v50.lib
read_lib ./gf180mcu/gf180mcuD/libs.ref/gf180mcu_fd_io/lib/gf180mcu_ws_io__ss_125C_4v50.lib



read_db ./final/odb/chip_top.odb
read_spef ./final/spef/max/chip_top.max.spef
read_sdc ./final/sdc/chip_top.sdc
read_lib "./librelane/build/con32_one_instruction/lib/max_${CORNER}/con32_one_instruction__max_${CORNER}.lib"


read_verilog "./final/nl/chip_top.nl.v"

# 3.2 Netlist estructural interno de tu macro diseñada
read_verilog "./librelane/build/con32_one_instruction/nl/con32_one_instruction.nl.v"
#link_design "chip_top"
puts [get_full_name [get_cells -hierarchical *con32_one_instruction*]]
#read_db ./librelane/build/con32_one_instruction/odb/con32_one_instruction.odb
#read_db "./librelane/build/con32_one_instruction/odb/con32_one_instruction.odb"
#read_sdc -path "i_chip_core.con32_one_instruction_u" "./librelane/build/con32_one_instruction/sdc/con32_one_instruction.sdc"
read_spef -path "i_chip_core.con32_one_instruction_u" "./librelane/build/con32_one_instruction/spef/max/con32_one_instruction.max.spef"
#read_spef ./librelane/build/con32_one_instruction/spef/max/con32_one_instruction.max.spef
#read_sdc ./librelane/build/con32_one_instruction/sdc/con32_one_instruction.sdc
