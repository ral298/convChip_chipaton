# ==============================================================================
# SCRIPT DE GENERACIÓN DE CLOCK MESH PARA OPENROAD / LIBRELANE
# ==============================================================================

set block [::ord::get_db_block]
set tech [::ord::get_db_tech]

puts "==> Iniciando construcción de Clock Mesh..."

# 1. Definir la red de reloj principal
set clk_net [array get ::env CLOCK_NET]
if {$clk_net == ""} {
    set clk_net "clk_ref"
}

# 2. Especificar las capas metálicas de la Malla (GF180MCU)
set horiz_layer [$tech findLayer "Metal4"]
set vert_layer  [$tech findLayer "Metal5"]

# 3. Crear las líneas de la malla (Straps) cruzadas sobre el Die
# Ancho de pista: 1.2 um, Espaciado/Paso (Pitch): 100 um
set die_area [$block getDieArea]
set x_min [$die_area xMin]
set y_min [$die_area yMin]
set x_max [$die_area xMax]
set y_max [$die_area yMax]

set pitch 100000; # 100 um en unidades de base de datos (DBUs)
set width 1000;   # 1.2 um

# Generar tiras horizontales en Metal4
for {set y [expr {$y_min + $pitch}]} {$y < $y_max} {incr y $pitch} {
    gui::add_wire_grid -net $clk_net -layer $horiz_layer -width $width -y $y
}

# Generar tiras verticales en Metal5
for {set x [expr {$x_min + $pitch}]} {$x < $x_max} {incr x $pitch} {
    gui::add_wire_grid -net $clk_net -layer $vert_layer -width $width -x $x
}

# 4. Rutear las conexiones cortas (Leaves) desde la malla a las terminales de los FF
puts "==> Conectando sinks y drivers a la rejilla de reloj..."
global_route
detailed_route -output_drc mesh_drc.rpt

puts "==> Clock Mesh construido exitosamente."
