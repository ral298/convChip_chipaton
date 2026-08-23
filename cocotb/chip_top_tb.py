# SPDX-FileCopyrightText: © 2026 Chipathon 2026 workshop
# SPDX-License-Identifier: Apache-2.0

import os
import random
import logging
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, ValueChange, ClockCycles
from cocotb.types import LogicArray
from cocotb_tools.runner import get_runner

import numpy as np
import matplotlib.pyplot as plt

# --- Configuración del entorno y parámetros temporales ---
sim = os.getenv("SIM", "icarus")
gl = os.getenv("GL", False)
pdk_root = os.getenv("PDK_ROOT", Path(__file__).resolve().parent / "../gf180mcu")
pdk = os.getenv("PDK", "gf180mcuD")
scl = os.getenv("SCL", "gf180mcu_fd_sc_mcu7t5v0")
pad = os.getenv("PAD", "gf180mcu_fd_io")
slot = os.getenv("SLOT", "1x1")


hdl_toplevel = "chip_top"

# Reloj a 20 MHz -> Periodo = 50 ns
CLK_PERIOD_NS = 50
BAUDRATE = 2000000
BIT_TIME_NS = round((1 / BAUDRATE) / 1e-9, 3)

# -----------------------------------------------------------------------------
# Funciones Auxiliares de Señal y Conversión para Cocotb 2.0
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Funciones Auxiliares de Señal y Conversión para Cocotb 2.0
# -----------------------------------------------------------------------------
def set_bidir_bit(dut, bit_index, bit_value):
    """
    Controla el bit indicado (bit 0 = RXD) y mantiene los otros 39 bits en 'z'
    para evitar contención con los drivers bufif1 de las salidas (TXD y LEDs).
    """
    NUM_PADS = 40
    # Creamos un arreglo de 'z' para todo el bus
    pads = ['z'] * NUM_PADS
    # Asignamos el valor deseado únicamente al bit solicitado
    pads[bit_index] = '1' if bit_value else '0'
    # En LogicArray, el orden de string se lee MSB a la izquierda, LSB a la derecha
    dut.bidir_PAD.value = LogicArray("".join(reversed(pads)))

def get_bidir_bit(dut, bit_index):
    """Obtiene el valor lógico de un bit específico del bus bidir_PAD de forma segura."""
    try:
        val_str = str(dut.bidir_PAD.value)
        # Invertir el índice para mapear bit_index 0 al último caracter (LSB)
        char_val = val_str[-(bit_index + 1)]
        if char_val in ('0', '1'):
            return int(char_val)
        return 0
    except Exception:
        return 0
        
async def set_defaults(dut):
    dut.input_PAD.value = 0
    # Inicializar bit 0 (RXD) en reposo '1'
    #set_bidir_bit(dut, 0, 1)

async def enable_power(dut):
    dut.VDD.value = 1
    dut.VSS.value = 0

async def wait_for_falling_edge_bit1(dut):
    """Espera un flanco de bajada en el bit 1 (TXD) de bidir_PAD."""
    while True:
        await ValueChange(dut.bidir_PAD)
        if get_bidir_bit(dut, 1) == 0:
            break

async def uart_receive_byte(dut):
    """Muestrea un byte desde la salida TXD conectada a bidir_PAD[1]."""
    # 1. Esperar bit de Start (Transición a 0 en bit 1)
    await wait_for_falling_edge_bit1(dut)

    # 2. Esperar 1.5 tiempos de bit para centrarse en el LSB
    await Timer(round(BIT_TIME_NS * 1.5, 3), units="ns")
    
    byte_recibido = 0
    for i in range(8):
        bit = get_bidir_bit(dut, 1)
        byte_recibido |= (bit << i)
        if i < 7:
            await Timer(BIT_TIME_NS, units="ns")
            
    # 3. Esperar bit de Stop
    await Timer(BIT_TIME_NS, units="ns")
    return byte_recibido

async def uart_send_instruction(dut, bueno_str):
    """Transmite una trama por el pin RXD conectado a bidir_PAD[0]."""
    contador = 0
    for f in range(len(bueno_str) - 1, -1, -1):
        if (f + 1) % 8 == 0:
            # Bit de Stop del anterior (1) y Start del siguiente (0)
            set_bidir_bit(dut, 0, 1)
            await Timer(BIT_TIME_NS, units="ns")
            set_bidir_bit(dut, 0, 0)
            await Timer(BIT_TIME_NS, units="ns")
            contador = 0
            
        set_bidir_bit(dut, 0, int(bueno_str[f]))
        await Timer(BIT_TIME_NS, units="ns")
        contador += 1
        
        if contador == 8:
            set_bidir_bit(dut, 0, 1)
            await Timer(BIT_TIME_NS, units="ns")

def binario_a_hexadecimal(binario):
    entero = int(binario, 2)
    return hex(entero)[2:].zfill(16)

def decimal_a_binario(numero, escale):
    binario = bin(numero)[2:]
    return binario.zfill(escale)

# Definición de filtros y bias
filt = np.array([[[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]],
                 [[ 2, 1, 2], [ 2, 1, 2], [ 2, 1, 2]],
                 [[ 0, 0, 0], [ 0, 0, 1], [ 0, 0, 0]],
                 [[ 0, 0, 0], [ 0, 0, 0], [ 0, 0, 1]],
                 [[ 0, 0, 1], [ 0, 0, 0], [ 0, 0, 0]],
                 [[ 0, 1, 0], [ 0, 0, 0], [ 0, 0, 0]],
                 [[ 1, 0, 0], [ 0, 0, 0], [ 0, 0, 0]],
                 [[ 0, 0, 0], [ 0, 0, 0], [ 1, 0, 0]]], dtype=np.int32)
bias = [0, 0, 0, 0, 0, 0, 0, 0, 0]


# -----------------------------------------------------------------------------
# Testbench Principal de Cocotb
# -----------------------------------------------------------------------------
@cocotb.test()
async def test_uart_convolution(dut):
    """Verificación de inferencia convolucional sobre el padring de chip_top"""
    
    # 1. Alimentación y arranque de reloj en los pads
    await set_defaults(dut)
    if gl:
        await enable_power(dut)
        
    cocotb.start_soon(Clock(dut.clk_PAD, CLK_PERIOD_NS, units="ns").start())

    # 2. Secuencia de Reset (rst_n_PAD activo en bajo)
    dut._log.info("Aplicando secuencia de Reset en rst_n_PAD...")
    dut.rst_n_PAD.value = 1
    set_bidir_bit(dut, 0, 1)
    await Timer(1000, units="ns")
    dut.rst_n_PAD.value = 0
    await Timer(2000, units="ns")
    dut.rst_n_PAD.value = 1
    await Timer(2000, units="ns")

    # 3. Envío de Filtros y Bias
    dut._log.info("Iniciando envío de filtros...")
    for z in range(filt.shape[0]):
        for i in range(filt.shape[1]):
            for j in range(filt.shape[2]):
                dato = decimal_a_binario(z, 3) + decimal_a_binario(j, 2) + decimal_a_binario(i, 2) + '1' + '1'
                if filt[z, i, j] < 0:
                    bueno = decimal_a_binario(65535 + filt[z, i, j] + 1, 16) + '0' + '0' + dato.zfill(14)
                else:
                    bueno = decimal_a_binario(filt[z, i, j], 16) + '0' + '0' + dato.zfill(14)
                await uart_send_instruction(dut, bueno)

        # Enviar Bias
        dato = decimal_a_binario(z, 3) + decimal_a_binario(j, 2) + decimal_a_binario(i, 2) + '1' + '1'
        if bias[z] < 0:
            bueno = decimal_a_binario(65535 + bias[z] + 1, 16) + '1' + '0' + dato.zfill(14)
        else:
            bueno = decimal_a_binario(bias[z], 16) + '1' + '0' + dato.zfill(14)
        await uart_send_instruction(dut, bueno)

    # 4. Envío de Imagen de Entrada
    dut._log.info("Iniciando envío de imagen...")
    image_dummy_path = Path(__file__).resolve().parent / "tb" / "prueba.npy"
    if not image_dummy_path.exists():
        image_dummy_path = Path(__file__).resolve().parent / "prueba.npy"
        
    image_dummy = np.load(str(image_dummy_path))
    ren, col = image_dummy.shape

    for capa_base in range(1):
        for renglon_base in range(ren):
            for j in range(col):
                dato = decimal_a_binario(j, 5) + decimal_a_binario(renglon_base, 5) + '1' + '1'
                bueno = decimal_a_binario(image_dummy[renglon_base, j], 16) + '0' + '1' + dato.zfill(14)
                hexadecimal=binario_a_hexadecimal(bueno)
                dut._log.info("Senal renglon: "+str(renglon_base)+"\tcol:"+str(j)+ "\tnum:"+str(image_dummy[renglon_base, j])+"\tHEX:"+hexadecimal)
                await uart_send_instruction(dut, bueno)

    # 5. Cálculo del Modelo Dorado (Golden Model)
    con_ima = np.zeros((ren - 2, col - 2), dtype=np.float64)
    z = 0
    for i in range(ren - 2):
        for j in range(col - 2):
            for i_con in range(3):
                for j_con in range(3):
                    con_ima[i, j] += (filt[z, i_con, j_con] * image_dummy[i + i_con, j + j_con])
    con_ima += bias[z]
    con_ima = np.array(con_ima, dtype=np.int16)

    # 6. Solicitud y Recepción de Datos desde TXD
    dut._log.info("Solicitando lectura de datos...")
    image_fpga_ren = 14
    image_fpga_col = 14
    
    for filtro_index in range(1):
        dato = decimal_a_binario(filtro_index, 3) + decimal_a_binario(image_fpga_col - 1, 5) + decimal_a_binario(image_fpga_ren - 1, 5) + '0' + '1'
        bueno = decimal_a_binario(0, 16) + dato.zfill(16)
        await uart_send_instruction(dut, bueno)
    dut._log.info("Esperando procesamiento final...")
    #await Timer(6500000, units="ns")
    dut._log.info("Solicitando y leyendo datos calculados de la salida TXD...")
    
    bytes_salida = []
    for n in range(image_fpga_ren * image_fpga_col):
        dato_8bits = await uart_receive_byte(dut)
        dato_8bits = dato_8bits | ((await uart_receive_byte(dut)) << 8)
        bytes_salida.append(dato_8bits)
        dut._log.info(f"Byte [{n}] recibido de TXD: Hex=0x{dato_8bits:02X}, Dec={dato_8bits}")

    matriz_salida = np.array(bytes_salida, dtype=np.uint16).view(np.int16).reshape((image_fpga_ren, image_fpga_col))

    # 7. Generación de Imagen Comparativa
    fig, axs = plt.subplots(1, 3, figsize=(12, 4))
    axs[0].imshow(image_dummy, cmap='gray')
    axs[0].set_title('Imagen Original')
    
    axs[1].imshow(matriz_salida, cmap='gray')
    axs[1].set_title('Calculada con CHIP')
    
    axs[2].imshow(con_ima, cmap='gray')
    axs[2].set_title('Golden Model (PC)')
    plt.savefig('Completa.png')
    dut._log.info("Imagen generada: Completa.png")

    # 8. Asertos de Verificación Final
    assert np.array_equal(matriz_salida, con_ima), (
        f"TEST FAILED: Matriz del Chip no coincide con el Golden Model."
    )
    dut._log.info("✅ TEST PASSED: Salida de chip_top verificada contra Golden Model.")


# -----------------------------------------------------------------------------
# Runner de Cocotb
# -----------------------------------------------------------------------------
def chip_top_runner():

    proj_path = Path(__file__).resolve().parent

    sources = []
    defines = {f"SLOT_{slot.upper()}": True,"USE_POWER_PINS": True,
        "FUNCTIONAL": True,}
    includes = [proj_path / "../src/"]

# Set the LibreLane PDK/SCL/PAD defines
    defines[f"PDK_{pdk.replace('-','_')}"] = True
    defines[f"SCL_{scl}"] = True
    defines[f"PAD_{pad}"] = True


    
    if gl:
        scl_v = Path(pdk_root) / pdk / "libs.ref" / scl / "verilog" / f"{scl}.v"
        prim_v = Path(pdk_root) / pdk / "libs.ref" / scl / "verilog" / "primitives.v"
        if scl_v.exists():
            sources.append(scl_v)
        if prim_v.exists():
            sources.append(prim_v)

        sources.append(proj_path / f"../final/pnl/{hdl_toplevel}.pnl.v")
        sources.append(proj_path / f"../librelane/build/con32_one_instruction/pnl/con32_one_instruction.pnl.v")
        
        
        defines = {"FUNCTIONAL": True, "USE_POWER_PINS": True}
    else:
        sources.append(proj_path / "../src/chip_top.sv")
        sources.append(proj_path / "../src/chip_core.sv")
        sources.append(proj_path / "../src/con32_one_instruction.v")
        sources.append(proj_path / "../src/acti.v")
        sources.append(proj_path / "../src/con32bits_parall.v")
        sources.append(proj_path / "../src/four_palabras_uart.v")
        sources.append(proj_path / "../src/mult_16b_bf.v")
        sources.append(proj_path / "../src/punt_mo_seg.v")
        sources.append(proj_path / "../src/salida.v")
        sources.append(proj_path / "../src/suma_16b.v")
        sources.append(proj_path / "../src/uart_tx_4in4.v")
        sources.append(proj_path / "../src/uart_ultimo.v")

    sources += [
        #Path(pdk_root) / pdk / "libs.ref/gf180mcu_fd_io/verilog/gf180mcu_fd_io.v",
        Path(pdk_root) / pdk / "libs.ref/gf180mcu_fd_io/verilog/gf180mcu_ws_io.v",
        Path(pdk_root) / pdk / f"libs.ref/{pad}/verilog/{pad}.v",
        proj_path / "../ip/gf180mcu_ws_ip__id/vh/gf180mcu_ws_ip__id.v",
        proj_path / "../ip/gf180mcu_ws_ip__logo/vh/gf180mcu_ws_ip__logo.v",
    ]


    build_args = []

    if sim == "icarus":
        # For debugging
        # build_args = ["-Winfloop", "-pfileline=1"]
        pass

    if sim == "verilator":
        build_args = ["--timing", "--trace", "--trace-fst", "--trace-structs", "--DUSE_POWER_PINS"]

    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel=hdl_toplevel,
        defines=defines,
        always=True,
        includes=includes,
        build_args=build_args,
        waves=True,
    )

    plusargs = []

    runner.test(
        hdl_toplevel=hdl_toplevel,
        test_module="chip_top_tb,",
        plusargs=plusargs,
        waves=True,
    )
if __name__ == "__main__":
    chip_top_runner()
