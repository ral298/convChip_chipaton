import os
import random
import logging
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, Edge, RisingEdge, FallingEdge, ClockCycles
from cocotb_tools.runner import get_runner

import numpy as np
from skimage import io
from skimage.transform import resize

# --- Configuración de parámetros y tiempos ---
# Frecuencia del reloj: 50 MHz -> Periodo = 20 ns
CLK_PERIOD_NS = 20 

# Baudrate: 3M baudios -> Tiempo por bit
# 1 / 3,000,000 s = 333.333 ns
BIT_TIME_NS = round((1 / 3000000) / 1e-9, 3) 

def binario_a_hexadecimal(binario):
    # Convertir el número binario a entero
    entero = int(binario, 2)

    # Convertir el entero a hexadecimal
    hexadecimal = hex(entero)[2:]

    hexadecimal_completo = hexadecimal.zfill(16)

    return hexadecimal_completo

def decimal_a_binario(numero, escale):
    binario = bin(numero)[2:]
    # if numero < 0:
    #     # Manejo de complemento a 2 simple para 16 bits si es negativo
    #     binario = bin(65535 + numero + 1)[2:]
    return binario.zfill(escale)

# Definición de filtros e imagen (Misma lógica de tu script)
filt = np.array([[[-1,0,1],[-1,0,1],[-1,0,1]],
                 [[2,1,2],[2,1,2],[2,1,2]],
                 [[0,0,0],[0,0,1],[0,0,0]],
                 [[0,0,0],[0,0,0],[0,0,1]],
                 [[0,0,1],[0,0,0],[0,0,0]],
                 [[0,1,0],[0,0,0],[0,0,0]],
                 [[1,0,0],[0,0,0],[0,0,0]],
                 [[0,0,0],[0,0,0],[1,0,0]]], dtype=np.int32)
bias = [0,0,0,0,0,0,0,0,0]

# --- Función Auxiliar Corrutina para enviar un Frame UART completo ---
async def uart_send_instruction(dut, bueno_str):
    """
    Envía una instrucción de 32 bits serializada por el pin RXD.
    Mapea exactamente tu bucle de Python que generaba el texto Verilog.
    """
    # Recorrer la cadena de atrás hacia adelante (LSB a MSB de los bloques de bytes)
    contador = 0
    for f in range(len(bueno_str) - 1, -1, -1):
        if (f + 1) % 8 == 0:
            # Bit de Stop del byte anterior (1) y Start del siguiente (0)
            dut.rxd.value = 1
            await Timer(BIT_TIME_NS, units="ns")
            dut.rxd.value = 0
            await Timer(BIT_TIME_NS, units="ns")
            contador = 0
            
        dut.rxd.value = int(bueno_str[f])
        await Timer(BIT_TIME_NS, units="ns")
        contador += 1
        
        if contador == 8:
            dut.rxd.value = 1
            await Timer(BIT_TIME_NS, units="ns")


# --- Test Principal de Cocotb ---
@cocotb.test()
async def test_uart_convolution(dut):
    """Testbench para el Chipathon: Configuración e Inferencia de la UART"""
    
    # 1. Arrancar el reloj a 50 MHz (Periodo de 20 ns)
    cocotb.start_soon(Clock(dut.clk_ref, CLK_PERIOD_NS, units="ns").start())

    # 2. Secuencia de Reset (Basada en tu bloque initial de Verilog)
    dut.rst.value = 1
    dut.rxd.value = 1
    await Timer(11, units="ns")
    await Timer(1000, units="ns") # Ajustado de ps a ns proporcionalmente
    dut.rst.value = 0
    await Timer(1115, units="ns")
    dut.rst.value = 1
    await Timer(1115, units="ns")
    await Timer(1000, units="ns")

    # 3. Envío de Filtros y Bias
    dut._log.info("Iniciando envío de filtros...")
    for z in range(filt.shape[0]):
        for i in range(filt.shape[1]):
            for j in range(filt.shape[2]):
                dato = decimal_a_binario(z,3) + decimal_a_binario(j,2) + decimal_a_binario(i,2) + '1' + '1'
                
                if filt[z,i,j] < 0:
                    bueno = decimal_a_binario(65535 + filt[z,i,j] + 1, 16) + '0' + '0' + dato.zfill(14)
                else:
                    bueno = decimal_a_binario(filt[z,i,j], 16) + '0' + '0' + dato.zfill(14)
                
                await uart_send_instruction(dut, bueno)

        # Enviar Bias por cada filtro
        dato = decimal_a_binario(z,3) + decimal_a_binario(j,2) + decimal_a_binario(i,2) + '1' + '1'
        if bias[z] < 0:
            bueno = decimal_a_binario(65535 + bias[z] + 1, 16) + '1' + '0' + dato.zfill(14)
        else:
            bueno = decimal_a_binario(bias[z], 16) + '1' + '0' + dato.zfill(14)
            
        await uart_send_instruction(dut, bueno)

    # 4. Envío de la Imagen (Simulada o cargada estáticamente para el TB)
    # Nota: Para evitar dependencias pesadas en el entorno del simulador de cocotb, 
    # puedes usar una matriz dummy o asegurar que skimage esté instalado en esa instancia de python.
    dut._log.info("Iniciando envío de la imagen...")
    # image=io.imread("./prueba.jpg")
    # Escala=2**7-1
    # image_dummy=np.array(resize(image, (16,16))*Escala,dtype=np.uint32)[:,:,0]
    # Generamos una matriz representativa de 16x16
    
    image_dummy = np.load("./prueba.npy")
    
    ren = image_dummy.shape[0]
    col = image_dummy.shape[1]
    dut._log.info(image_dummy)
    for capa_base in range(1):
        for renglon_base in range(ren):
            for j in range(col):
                dato = decimal_a_binario(j, 5) + decimal_a_binario(renglon_base, 5) + '1' + '1'
                bueno = decimal_a_binario(image_dummy[renglon_base, j], 16) + '0' + '1' + dato.zfill(14)
                hexadecimal=binario_a_hexadecimal(bueno)
                # print("Senal renglon: "+str(renglon_base)+"\tcol:"+str(j)+ "\tnum:"+str(image_dummy[renglon_base, j])+"\tHEX:"+hexadecimal)
                
                dut._log.info("Senal renglon: "+str(renglon_base)+"\tcol:"+str(j)+ "\tnum:"+str(image_dummy[renglon_base, j])+"\tHEX:"+hexadecimal)
                #dut._log.info("HEX:",hexadecimal)
                await uart_send_instruction(dut, bueno)

    # 5. Obtención de datos / Lectura de resultados
    dut._log.info("Solicitando lectura de datos calculados...")
    image_fpga_ren = 14 # 16 - 2
    image_fpga_col = 14
    
    for filtro_index in range(1):
        dato = decimal_a_binario(filtro_index, 3) + decimal_a_binario(image_fpga_col - 1, 5) + decimal_a_binario(image_fpga_ren - 1, 5) + '0' + '1'
        bueno = decimal_a_binario(0, 16) + dato.zfill(16)
        
        await uart_send_instruction(dut, bueno)
        
    # Esperar el tiempo final de procesamiento equivalente a tus #6500000000;
    dut._log.info("Esperando procesamiento final...")
    await Timer(6500000, units="ns")
