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


async def uart_receive_byte(dut):
    """
    Espera el bit de Start en la línea TXD y muestrea los 8 bits de datos
    a 3M Baudios, devolviendo un valor entero entre 0 y 255.
    """
    # 1. Esperar al bit de START (flanco de bajada: la línea pasa de 1 a 0)
    await FallingEdge(dut.txd)
    
    # 2. Esperar 1.5 tiempos de bit para muestrear justo en el CENTRO del primer bit de datos (LSB)
    await Timer(round(BIT_TIME_NS * 1.5, 3), units="ns")
    
    byte_recibido = 0
    
    # 3. Muestrear los 8 bits de datos (asumiendo formato estándar LSB first)
    for i in range(8):
        bit = int(dut.txd.value)
        byte_recibido |= (bit << i)  # Empaquetar bit en la posición i
        
        # Esperar 1 tiempo de bit completo para caer en el centro del siguiente bit
        if i < 7:
            await Timer(BIT_TIME_NS, units="ns")
            
    # 4. Esperar a que pase el bit de STOP (1)
    await Timer(BIT_TIME_NS, units="ns")
    
    return byte_recibido

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
    #await Timer(6500000, units="ns")
    dut._log.info("Solicitando y leyendo datos calculados de la salida TXD...")
    
    # Si sabes cuántos bytes esperas recibir (por ejemplo, 14x14 pixeles resultantes)
    bytes_salida = []
    
    # Supongamos que tu módulo responde transmitiendo bytes tras procesar:
    for n in range(image_fpga_ren * image_fpga_col):
        # Llama a la corrutina y se congela hasta que la UART mande el byte completo
        dato_8bits = await uart_receive_byte(dut)
        dato_8bits = dato_8bits | ((await uart_receive_byte(dut))<<8)
        bytes_salida.append(dato_8bits)
        
        # Imprime en la consola de cocotb en tiempo real
        dut._log.info(f"Byte [{n}] recibido de TXD: Hex=0x{dato_8bits:02X}, Dec={dato_8bits}")

    # Si quieres reconstruir tu matriz resultante de la convolución:
    matriz_salida = np.array(bytes_salida, dtype=np.uint16).view(np.int16).reshape((image_fpga_ren, image_fpga_col))
    
    # dut._log.info(f"\n{bytes_salida}, len: {len(bytes_salida)}")
    dut._log.info("Matriz recibida desde el chip:")
    dut._log.info(f"\n{matriz_salida}")
    await Timer(100000, units="ns")
    tam_fil=filt.shape[2]
    con_ima=np.zeros((image_dummy.shape[0]-2,image_dummy.shape[1]-2),dtype=np.float64)
    # sub_capas_ima=np.zeros((tam_fil,image.shape[0]-2,image.shape[1]-2),dtype=np.float64)
    z=0
    for i in range(image_dummy.shape[0]-2):
        for j in range(image_dummy.shape[1]-2):
            for i_con in range(3):
                for j_con in range(3):
                    # print(i,j,i_con,j_con)
                    con_ima[i,j]+=(filt[z,i_con,j_con]*image_dummy[i+i_con,j+j_con])#*(5/255)*(5/255)*(1/10)*(1/2.5)
                    # sub_capas_ima[z,i,j]+=(filt[z,i_con,j_con]*image[i+i_con,j+j_con,z])#*(5/255)*(5/255)*(1/10)*(1/2.5)
        # con_ima[i,j,z]+=bias[0]
            # print(z,i,j,con_ima[z,i,j])
    con_ima+=bias[z]
    con_ima= np.array(con_ima,dtype=np.int16)
    dut._log.info("Matriz calculada con al convolucion clasica:")
    dut._log.info(f"\n{con_ima}")
    imagen_comparativa= (con_ima==matriz_salida)
    dut._log.info("Matriz de comparacion de los valores numericos:")
    dut._log.info(f"\n{imagen_comparativa}")
    
    if (np.sum(imagen_comparativa*1)==image_fpga_ren * image_fpga_col):
        dut._log.info(f"\nLa imagen fue calculada correctamente")
        import matplotlib.pyplot as plt
        from multiprocessing import Process
        # plt.figure()
        fig, axs = plt.subplots(1, 3, figsize=(12, 4))
        axs[0].imshow(image_dummy, cmap='gray')
        axs[0].set_title('Imagen Original')
        
        axs[1].imshow(matriz_salida, cmap='gray')
        axs[1].set_title('Imagen calculada con CHIP')
        ren_pc, col_pc = matriz_salida.shape
        for i in range(ren_pc):
            for j in range(col_pc):
                val = matriz_salida[i, j]
                # Cambiar color de texto según la intensidad del fondo para mejor contraste
                color_texto = "white" if val < (matriz_salida.max() + matriz_salida.min()) / 2 else "black"
                axs[1].text(j, i, str(val), ha='center', va='center', 
                            color=color_texto, fontsize=6)
        axs[2].imshow(con_ima, cmap='gray')
        axs[2].set_title('Imagen calculada con PC')
        ren_chip, col_chip = con_ima.shape
        for i in range(ren_chip):
            for j in range(col_chip):
                val = con_ima[i, j]
                color_texto = "white" if val < (con_ima.max() + con_ima.min()) / 2 else "black"
                axs[2].text(j, i, str(val), ha='center', va='center', 
                            color=color_texto, fontsize=6)
        # plt.tight_layout()
        plt.savefig('Completa.png')
        # plt.show()
        plt.show(block=False)
        plt.pause(2)
        dut._log.info(f"\nSe creo la imagen resultante: Completa.png")
    else:
        dut._log.error(f"Error la cantidad de  valores fue {np.sum(imagen_comparativa*1)} deberia de ser {image_fpga_ren * image_fpga_col}")
        
    
    
    
