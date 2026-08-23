# ==============================================================================
# Script TCL nativo para OpenROAD (API de Resizer)
# ==============================================================================

puts "\[INFO-USER\] Ejecutando optimizacion de fanout en la red de entrada..."

# En OpenROAD, repair_design es el comando encargado de meter buffers de puerto
# y dividir redes con fanout elevado.
if { [info commands repair_design] != "" } {

    # 2. Divide las redes que superen el fanout especificado
    repair_design -max_fanout 16

    puts "\[INFO-USER\] repair_design ejecutado correctamente con max_fanout 16."
} else {
    puts "\[WARNING-USER\] El comando repair_design no esta disponible en este paso."
}
