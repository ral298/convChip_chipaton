# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 16:05:56 2024

@author: raulp
"""

import numpy as np 
from skimage import io
from skimage.transform import rescale, resize, downscale_local_mean
import matplotlib.pyplot as plt

import subprocess
#import serial
import time

# Configura el puerto serial, asegúrate de ajustar el puerto y la velocidad adecuadamente
# puerto_serial = serial.Serial('COM7', 115200, timeout=0)

tiempos=round ((1/3000000)/1e-12,3)

frecuencia=1/(2*100e6)

def binario_a_hexadecimal(binario):
    # Convertir el número binario a entero
    entero = int(binario, 2)

    # Convertir el entero a hexadecimal
    hexadecimal = hex(entero)[2:]

    hexadecimal_completo = hexadecimal.zfill(16)

    return hexadecimal_completo
def dividir_en_bloques(cadena, tamano_bloque):
    return [cadena[i:i + tamano_bloque] for i in range(0, len(cadena), tamano_bloque)]

# Función para enviar un byte al puerto serial
def print_byte(byte):
    print(decimal_a_binario(byte,16)[-8:])

        
def decimal_a_binario(numero,escale):
    # Convertir el número decimal a binario
    binario = bin(numero)

    # Eliminar el prefijo '0b' de la representación binaria
    binario = binario[2:]

    # Rellenar con ceros a la izquierda si es necesario para completar 32 bits
    binario_completo = binario.zfill(escale)

    return binario_completo
filt=np.array([[[-1,0,1],[-1,0,1],[-1,0,1]],[[2,1,2],[2,1,2],[2,1,2]],[[0,0,0],[0,0,1],[0,0,0]],[[0,0,0],[0,0,0],[0,0,1]],[[0,0,1],[0,0,0],[0,0,0]],[[0,1,0],[0,0,0],[0,0,0]],[[1,0,0],[0,0,0],[0,0,0]],[[0,0,0],[0,0,0],[1,0,0]]],dtype=np.int32)
bias=[0,0,0,0,0,0,0,0,0]
# image=io.imread("./ironman.jpg")[:,:,0]
image=io.imread("./prueba.jpg")
Escala=2**7-1
image=np.array(resize(image, (16,16))*Escala,dtype=np.uint32)[:,:,0]
plt.close('all')
plt.figure(20)
plt.imshow(image,cmap=plt.cm.gray)


new_image=np.zeros((image.shape[0]-2,image.shape[1]-2),dtype=np.uint32)
con=0
for i in range(2):
    print("time:",i+1)
    bueno= 32*"0"
    cadena_bits=bueno
    bloques = dividir_en_bloques(cadena_bits, 8)
    for bloque in bloques[::-1]:
        byte = int(bloque, 2)  
        # print(i)
        time.sleep(0.1)  # Pausa de medio segundo entre cada envío
        


time_puase=0.00005
with open("./linas_uno_pixel.txt", "w") as archivo:
    print("filtro\n\n\n")
    
    
    
    for z in range (filt.shape[0]):
        for i in range(filt.shape[1]):
            for j in range(filt.shape[2]):
                # print("dato",i,j)
                # print( decimal_a_binario(filt[i,j],32))
                #dato=decimal_a_binario(0,3)+'0'+decimal_a_binario(i,5)+decimal_a_binario(j,5)+'0'+'1'+'1'
                dato=decimal_a_binario(z,3)+decimal_a_binario(j,2)+decimal_a_binario(i,2)+'1'+'1'
                # print("ubicaciones")
                # print( dato.zfill(32))
                
                if filt[ z,i,j]<0:
                    bueno= decimal_a_binario(65535+filt[ z,i,j]+1,16)+'0'+'0'+dato.zfill(14)
                else:
                    bueno= decimal_a_binario(filt[ z,i,j],16)+'0'+'0'+dato.zfill(14)
                cadena_bits=bueno
                bloques = dividir_en_bloques(cadena_bits, 8)
                
                for bloque in bloques[::-1]:
                    byte = int(bloque, 2)  
                    # print(i)
                    time.sleep(time_puase)  # Pausa de medio segundo entre cada envío
                    
                hexadecimal=binario_a_hexadecimal(bueno)        
                archivo.write("//binario: "+(bueno)+"\n")
                # # print((bueno)+";#8680555;")
                archivo.write("//hexadecimal:"+hexadecimal+"\n")
                
                # archivo.write("instruction=32'b"+(bueno)+";#86705550;\n")
                # archivo.write("#50000;flat_comple=1;\n")
                # archivo.write("#50000;flat_comple=0;\n")
                archivo.write("//filtro\n")
                    
                # print("binario",bueno)
                # print("hexadecimal",hexadecimal)
                
                
                
                contador=0
                for f in range(len(bueno)-1,-1,-1):
                    if((f+1)%8==0):
                        archivo.write("rxd=1;#"+str(tiempos)+";\n")
                        archivo.write("rxd=0;#"+str(tiempos)+";\n\n")
                        contador=0
                    archivo.write("rxd="+bueno[f]+";#"+str(tiempos)+";\n")
                    contador+=1
                    if(contador==8):

                        # archivo.write("\nrxd=0;#8680555;\n")
                        archivo.write("rxd=1;#"+str(tiempos)+";\n\n\n\n")
                
                archivo.write("//"+hexadecimal + "\n")
                con+=1
        dato=decimal_a_binario(z,3)+decimal_a_binario(j,2)+decimal_a_binario(i,2)+'1'+'1'
        # bueno= decimal_a_binario(bias[z],16)+'1'+'0'+dato.zfill(14)
        
        if bias[z]<0:
            bueno= decimal_a_binario(65535+bias[z]+1,16)+'1'+'0'+dato.zfill(14)
        else:
            bueno= decimal_a_binario(bias[z],16)+'1'+'0'+dato.zfill(14)
        
        # print((bueno))
        # archivo.write("//binario: "+(bueno)+"\n")
        
        archivo.write("\n\n\n//filtro bias\n")
        
        
        hexadecimal=binario_a_hexadecimal(bueno)            
        #print("bias filtro")
        archivo.write("//binario: "+(bueno)+"\n")
        #print((bueno)+";#8680555;")
        archivo.write("//hexadecimal:"+hexadecimal+"\n")
        # archivo.write("instruction=32'b"+(bueno)+";#86705550;\n")
        # archivo.write("#50000;flat_comple=1;\n")
        # archivo.write("#50000;flat_comple=0;\n")
        #print("hexadecimal",hexadecimal)
        cadena_bits=bueno
        bloques = dividir_en_bloques(cadena_bits, 8)
        
        for bloque in bloques[::-1]:
            byte = int(bloque, 2)  
            # print(i)
            time.sleep(time_puase)  # Pausa de medio segundo entre cada envío
            
        
        
        for f in range(len(bueno)-1,-1,-1):
            if((f+1)%8==0):
                archivo.write("rxd=1;#"+str(tiempos)+";\n")
                archivo.write("rxd=0;#"+str(tiempos)+";\n\n")
                contador=0
            archivo.write("rxd="+bueno[f]+";#"+str(tiempos)+";\n")
            contador+=1
            if(contador==8):

                # archivo.write("\nrxd=0;#8680555;\n")
                archivo.write("rxd=1;#"+str(tiempos)+";\n\n\n\n")



        con+=1
            
    ren=image.shape[0]
    col=image.shape[1]
    print("\n\n\n\n//imagen\n\n\n")
    
    for capa_base in range(1):
    
        for renglon_base in range(ren):
        
            rengl=renglon_base
            for j in range(col):#image.shape[1]
                # print("dato",renglon_base,j)
                # print( decimal_a_binario(filt[i,j],32))
                # ch=decimal_a_binario(capa_base,3)
                dato=decimal_a_binario(j,5)+decimal_a_binario(rengl,5)+'1'+'1'
                
                bueno= decimal_a_binario(image[rengl,j],16)+'0'+'1'+dato.zfill(14)
                # print("ubicaciones")
                # print( dato.zfill(32))
                
                hexadecimal=binario_a_hexadecimal(bueno)
                print((bueno)+",")
                archivo.write("\n\n\n//imagen\n")
                archivo.write("//hexadecimal"+hexadecimal+"\n")
                
                cadena_bits=bueno
                bloques = dividir_en_bloques(cadena_bits, 8)
                archivo.write("//binario: "+(bueno)+"\n")
                
                # archivo.write("instruction=32'b"+(bueno)+";#86705550;\n")
                # archivo.write("#50000;flat_comple=1;\n")
                # archivo.write("#50000;flat_comple=0;\n")
                for bloque in bloques[::-1]:
                    byte = int(bloque, 2)  
                    # print(i)
                    time.sleep(time_puase)  # Pausa de medio segundo entre cada envío
                    
                
                # print("binario:",(bueno))
                
                for f in range(len(bueno)-1,-1,-1):
                    if((f+1)%8==0):
                        archivo.write("rxd=1;#"+str(tiempos)+";\n")
                        archivo.write("rxd=0;#"+str(tiempos)+";\n\n")
                        contador=0
                    archivo.write("rxd="+bueno[f]+";#"+str(tiempos)+";\n")
                    contador+=1
                    if(contador==8):
    
                        # archivo.write("\nrxd=0;#8680555;\n")
                        archivo.write("rxd=1;#"+str(tiempos)+";\n\n")
                
                
                # print("//hexadecimal"+hexadecimal)
                # archivo.write(hexadecimal + "\n")
                con+=1
            
            
            # for j in range(new_image.shape[1]):
            #     dato=(decimal_a_binario(j,5)+'0'+'1').zfill(64)
            #     print("dato",dato)
            #     hexadecimal=binario_a_hexadecimal(dato)
            #     # print(hexadecimal)
            #     archivo.write(hexadecimal + "\n")
            #     con+=1
            #     print('j',j,'dato:',hexadecimal)
        
    # print("\t\t\tobtener imagen \n\n\n\n")
    image_fpga=np.zeros((image.shape[0]-2,image.shape[1]-2),dtype=np.uint32)
    ren=image_fpga.shape[0]
    col=image_fpga.shape[1]
        
    for filtro_index in range(1):
        dato=decimal_a_binario(filtro_index,3)+decimal_a_binario(col-1,5)+decimal_a_binario(ren-1,5)+'0'+'1'
        bueno= decimal_a_binario(0,16)+dato.zfill(16)
        archivo.write("\n\n//obtencion de datos\n")
        hexadecimal=binario_a_hexadecimal(bueno)
        archivo.write("//hexadecimal"+hexadecimal+"\n")
        print("//hexadecimal"+hexadecimal+"\n")
        for f in range(len(bueno)-1,-1,-1):
            if((f+1)%8==0):
                archivo.write("rxd=1;#"+str(tiempos)+";\n")
                archivo.write("rxd=0;#"+str(tiempos)+";\n\n")
                contador=0
            archivo.write("rxd="+bueno[f]+";#"+str(tiempos)+";\n")
            contador+=1
            if(contador==8):
    
                # archivo.write("\nrxd=0;#8680555;\n")
                archivo.write("rxd=1;#"+str(tiempos)+";\n\n")
        archivo.write("\n#6500000000;\n\n")
    # archivo.write("instruction=32'b"+(bueno)+";#86705550;\n")
    # archivo.write("#50000;flat_comple=1;\n")
    # archivo.write("#50000;flat_comple=0;\n")
    # archivo.write("#3906249750;\n")
    
    
    for z in range (1):
        for i in range(ren):
            for j in range(col):
                # print("dato obtencion",z,i,j)
                #dato=(decimal_a_binario(z,3)+'0'+decimal_a_binario(i,5)+decimal_a_binario(j,5)+'0'+'0'+'1').zfill(64)
                
                dato=decimal_a_binario(z,3)+decimal_a_binario(j,5)+decimal_a_binario(i,5)+'0'+'1'
                bueno= decimal_a_binario(0,16)+dato.zfill(16)
                cadena_bits=bueno
                bloques = dividir_en_bloques(cadena_bits, 8)
                
                for bloque in bloques[::-1]:
                    byte = int(bloque, 2)  
                    # print(i)
                    time.sleep(time_puase)  # Pausa de medio segundo entre cada envío
                    
                
                
                
                # archivo.write("\n\n\n//binario: "+(bueno)+"\n")
                # archivo.write("//obtencion de datos\n")
                # archivo.write("//hexadecimal"+hexadecimal+"\n")
                # for f in range(len(bueno)-1,-1,-1):
                #     if((f+1)%8==0):
                #         archivo.write("rxd=1;#8680555;\n")
                #         archivo.write("rxd=0;#8680555;\n\n")
                #         contador=0
                #     archivo.write("rxd="+bueno[f]+";#8680555;\n")
                #     contador+=1
                #     if(contador==8):

                #         archivo.write("\nrxd=0;#8680555;\n")
                #         archivo.write("rxd=1;#8680555;\n\n")
                
                # print("dato",dato)
                hexadecimal=binario_a_hexadecimal(bueno)
                # archivo.write("instruction=32b'"+(bueno)+";#86805550;\n")
                # print((bueno)+",")
                
                
                time.sleep(time_puase)
                
                # print("//hexadecimal"+hexadecimal)
                # print(hexadecimal)
                # archivo.write(hexadecimal + "\n")
                con+=1
                # print('j',j,'dato:',hexadecimal)
            
    

    # for z in range (1):
    #     for i in range(image_fpga.shape[0]):
    #         for j in range(image_fpga.shape[1]):
    #             # print("dato obtencion",z,i,j)
    #             #dato=(decimal_a_binario(z,3)+'0'+decimal_a_binario(i,5)+decimal_a_binario(j,5)+'0'+'0'+'1').zfill(64)
                
    #             dato=decimal_a_binario(z,3)+decimal_a_binario(j,5)+decimal_a_binario(i,5)+'0'+'1'
    #             bueno= decimal_a_binario(0,16)+dato.zfill(16)
    #             cadena_bits=bueno
    #             bloques = dividir_en_bloques(cadena_bits, 8)
                
    #             for bloque in bloques[::-1]:
    #                 byte = int(bloque, 2)  
    #                 # print(i)
    #                 time.sleep(time_puase)  # Pausa de medio segundo entre cada envío
                    
                
                
                
                
                
                #time.sleep(time_puase)
                # con+=1
            
        
            
            
    
            
            
    dato=('0').zfill(32)
    # print("dato",dato)
    hexadecimal=binario_a_hexadecimal(dato)
    # print(hexadecimal)
    # archivo.write(hexadecimal + "\n")
                
    dato=('0').zfill(32)
    # print("dato",dato)
    hexadecimal=binario_a_hexadecimal(dato)
    # print(hexadecimal)
    # archivo.write(hexadecimal + "\n")
                
    dato=('0').zfill(32)
    # print("dato",dato)
    hexadecimal=binario_a_hexadecimal(dato)
    # print(hexadecimal)
    # archivo.write(hexadecimal + "\n")
            
            
            
            # dato=decimal_a_binario(rengl,8)+decimal_a_binario(j,8)+'1'+'1'+'1'
print("con:",con)

tam_fil=filt.shape[2]
con_ima=np.zeros((image.shape[0]-2,image.shape[1]-2),dtype=np.float64)
# sub_capas_ima=np.zeros((tam_fil,image.shape[0]-2,image.shape[1]-2),dtype=np.float64)
z=0
for i in range(image.shape[0]-2):
    for j in range(image.shape[1]-2):
        for i_con in range(3):
            for j_con in range(3):
                # print(i,j,i_con,j_con)
                con_ima[i,j]+=(filt[z,i_con,j_con]*image[i+i_con,j+j_con])#*(5/255)*(5/255)*(1/10)*(1/2.5)
                # sub_capas_ima[z,i,j]+=(filt[z,i_con,j_con]*image[i+i_con,j+j_con,z])#*(5/255)*(5/255)*(1/10)*(1/2.5)
    # con_ima[i,j,z]+=bias[0]
        # print(z,i,j,con_ima[z,i,j])
con_ima+=bias[z]
plt.figure(2)
plt.imshow(con_ima,vmin=con_ima.min(),vmax=con_ima.max(),cmap=plt.cm.gray)
plt.title("la conv2d")
# sub_capas_ima+=bias[0]
# for z in range(tam_fil):
#     plt.figure(3+z)
#     plt.imshow(sub_capas_ima[z,:,:])#,vmin=sub_capas_ima[z,:,:].min(),vmax=sub_capas_ima[z,:,:].max(),cmap=plt.cm.gray)
#     plt.title("la conv"+str(z+1))
# np.sum(sub_capas_ima,axis=0).shape
# np.sum(np.sum(sub_capas_ima,axis=0)+bias[0]==con_ima)==con_ima.shape[0]*con_ima.shape[1]
# plt.figure(3)
# plt.imshow(image_fpga,vmin=image_fpga.min(),vmax=image_fpga.max(),cmap=plt.cm.gray)
# imag_a=image[:,:,0]
# imag_a=image[:,:,1]
# imag_a=image[:,:,2]
# imag_conv2d=np.sum(sub_capas_ima[0:2,:,:],axis=0)+bias[0]

archivo = './linas_uno_pixel.txt'
print(frecuencia/1e-12)
# Comando para abrir gedit con el archivo
subprocess.run(['gedit', archivo])

# plt.figure(3)
# plt.imshow(con_ima[1,:,:],vmin=0,cmap=plt.cm.gray)
# plt.figure(4)
# plt.imshow(con_ima[2,:,:],vmin=0,cmap=plt.cm.gray)

