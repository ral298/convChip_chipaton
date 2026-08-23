import os
import glob
import pandas as pd

def buscar_archivos_csv():
    # Busca archivos .csv en el directorio actual y subcarpetas adyacentes
    patrones = [
        './**/*.csv'
    ]
    archivos = []
    for p in patrones:
        archivos.extend(glob.glob(p, recursive=True))
    
    # Normalizar rutas y eliminar duplicados
    archivos_unicos = sorted(list(set([os.path.normpath(f) for f in archivos])))
    return archivos_unicos

def analizar_csv(ruta_csv):
    lineas_salida = []
    
    # Función auxiliar para imprimir en consola y almacenar para el archivo
    def log(texto=""):
        print(texto)
        lineas_salida.append(texto)

    log("\n" + "="*60)
    log(f" 📄 ANALIZANDO: {ruta_csv}")
    log("="*60 + "\n")
    
    try:
        df = pd.read_csv(ruta_csv)
    except Exception as e:
        log(f"❌ Error al leer el archivo: {e}")
        escribir_reporte(lineas_salida)
        return

    if 'Metric' not in df.columns or 'Value' not in df.columns:
        log("❌ El CSV seleccionado no contiene las columnas necesarias ('Metric', 'Value').")
        escribir_reporte(lineas_salida)
        return

    # Extraer las esquinas (corners) presentes
    corners = df[df['Metric'].str.contains('corner:', na=False)]['Metric'].apply(lambda x: x.split('corner:')[1]).unique()

    reporte = []

    for c in corners:
        def get_val(m):
            sub = df[df['Metric'] == f"{m}__corner:{c}"]
            if not sub.empty:
                try:
                    return float(sub['Value'].values[0])
                except ValueError:
                    return 0.0
            return 0.0

        setup_ws = get_val('timing__setup__ws')
        setup_vios = int(get_val('timing__setup_vio__count'))
        hold_ws = get_val('timing__hold__ws')
        hold_vios = int(get_val('timing__hold_vio__count'))
        slew_vios = int(get_val('design__max_slew_violation__count'))
        cap_vios = int(get_val('design__max_cap_violation__count'))

        # Filtrar solo esquinas con violaciones o slack negativo
        if setup_ws < 0 or setup_vios > 0 or hold_ws < 0 or hold_vios > 0 or slew_vios > 0 or cap_vios > 0:
            reporte.append({
                'Corner': c,
                'Setup WS (ns)': setup_ws,
                'Setup Vios': setup_vios,
                'Hold WS (ns)': hold_ws,
                'Hold Vios': hold_vios,
                'Slew Vios': slew_vios,
                'Cap Vios': cap_vios
            })

    df_reporte = pd.DataFrame(reporte)

    if df_reporte.empty:
        log("✅ ¡Excelente! No se encontraron violaciones críticas en esta ejecución.")
    else:
        log("⚠️  VIOLACIONES DETECTADAS EN ESTA EJECUCIÓN:")
        log(df_reporte.to_string(index=False))
        
    escribir_reporte(lineas_salida)

def escribir_reporte(lineas):
    nombre_archivo = "report_check.txt"
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write("\n".join(lineas) + "\n")
        print(f"\n📁 Reporte exportado exitosamente en: {os.path.abspath(nombre_archivo)}")
    except Exception as e:
        print(f"❌ No se pudo guardar el archivo {nombre_archivo}: {e}")

def main():
    archivos = buscar_archivos_csv()
    
    if not archivos:
        print("❌ No se encontraron archivos .csv en el directorio o sus alrededores.")
        return

    print("=== ARCHIVOS CSV ENCONTRADOS EN LOS DIRECTORIOS ===")
    for idx, ruta in enumerate(archivos, 1):
        print(f" [{idx}] {ruta}")
    
    try:
        opcion = int(input("\nIngresa el número del archivo que deseas revisar: "))
        if 1 <= opcion <= len(archivos):
            analizar_csv(archivos[opcion - 1])
        else:
            print("❌ Número de opción no válido.")
    except ValueError:
        print("❌ Entrada inválida. Por favor ingresa un número.")

if __name__ == "__main__":
    main()
