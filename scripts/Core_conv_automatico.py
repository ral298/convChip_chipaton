
# -*- coding: utf-8 -*-

from pathlib import Path
import subprocess
import textwrap
import time
import shutil
import yaml
import os
from datetime import datetime

# ============================================================
# CONFIG
# ============================================================

CONTAINER_NAME = "gf180"
sync_value = False
shutdown_value = True
PDK_NAME     = "gf180mcuD"
STD_CELL_LIB = "gf180mcu_fd_sc_mcu7t5v0"

HOST_WORKSPACE  = Path.home() / "eda" / "designs"
HOST_MULTIMACRO = HOST_WORKSPACE / "convChip" / "user_macros"

CONTAINER_MULTIMACRO = "/foss/designs/convChip/user_macros"
CONTAINER_FORK       = "/foss/designs/convChip/template"

YAML_PATH = HOST_MULTIMACRO / "librelane" / "con32bits_parall_macro.yaml"

BUILD_ROOT = HOST_MULTIMACRO / "build"

SAFE_KEYS = {
    "FP_SIZING",
    "FP_CORE_UTIL",
    "PL_TARGET_DENSITY_PCT",
    "TOP_MARGIN_MULT",
    "BOTTOM_MARGIN_MULT",
    "LEFT_MARGIN_MULT",
    "RIGHT_MARGIN_MULT",
    "CELL_PADDING",
    "PDN_MULTILAYER",
    "PDN_VWIDTH",
    "PDN_HWIDTH",
    "PDN_VSPACING",
    "PDN_HSPACING",
    "PDN_VPITCH",
    "PDN_HPITCH",
    "CLOCK_PERIOD",
    "SYNTH_STRATEGY",
    "MAX_FANOUT_CONSTRAINT",
    "EXTRA_EXCLUDED_CELLS",
    "CTS_CLK_BUFFERS",
    "CTS_ROOT_BUFFER",
    "CTS_CLK_MAX_WIRE_LENGTH",
    "CTS_DISTANCE_BETWEEN_BUFFERS",
    "CTS_SINK_CLUSTERING_SIZE",
    "CTS_SINK_CLUSTERING_MAX_DIAMETER",
    "GRT_REPAIR_ANTENNAS",
    "RUN_HEURISTIC_DIODE_INSERTION",
    "DIODE_PADDING",
    "GRT_ALLOW_CONGESTION",
    "RT_MIN_LAYER",
    "GPL_CELL_PADDING",
    "DPL_CELL_PADDING",
}
# ============================================================
# CONFIGURACIONES AUTOMÁTICAS
# ============================================================

CONFIGS = [

# ============================================================
# PADDING 8
# ============================================================
{
    "name": "padding_8",

    "GPL_CELL_PADDING": 8,
    "DPL_CELL_PADDING": 8,
},

# ============================================================
# PADDING 4 + HALO GRANDE
# ============================================================
{
    "name": "padding4_halo20",

    "GPL_CELL_PADDING": 4,
    "DPL_CELL_PADDING": 4,

    "TOP_MARGIN_MULT": 4,
    "BOTTOM_MARGIN_MULT": 4,
    "LEFT_MARGIN_MULT": 4,
    "RIGHT_MARGIN_MULT": 4,
},

# ============================================================
# PADDING 8 + HALO GRANDE
# ============================================================
{
    "name": "padding8_halo20",

    "GPL_CELL_PADDING": 8,
    "DPL_CELL_PADDING": 8,

    "TOP_MARGIN_MULT": 4,
    "BOTTOM_MARGIN_MULT": 4,
    "LEFT_MARGIN_MULT": 4,
    "RIGHT_MARGIN_MULT": 4,
},

# ============================================================
# PDN MENOS DENSA
# ============================================================
{
    "name": "padding4_pdn160",

    "GPL_CELL_PADDING": 4,
    "DPL_CELL_PADDING": 4,

    "PDN_VPITCH": 160,
    "PDN_HPITCH": 160,
},

# ============================================================
# UTILIZACION MENOR
# ============================================================
{
    "name": "padding4_util35",

    "FP_CORE_UTIL": 35,
    "PL_TARGET_DENSITY_PCT": 30,

    "GPL_CELL_PADDING": 4,
    "DPL_CELL_PADDING": 4,
},

# ============================================================
# UTILIZACION MENOR + PADDING ALTO
# ============================================================
{
    "name": "padding8_util35",

    "FP_CORE_UTIL": 35,
    "PL_TARGET_DENSITY_PCT": 30,

    "GPL_CELL_PADDING": 8,
    "DPL_CELL_PADDING": 8,
},

    
]

# ============================================================
# FUNCIONES
# ============================================================
def run_shell(cmd, timeout=None):

    subprocess.run(
        ["docker", "start", CONTAINER_NAME],
        capture_output=True
    )

    full_cmd = [
        "docker",
        "exec",
        CONTAINER_NAME,
        "bash",
        "-lc",
        cmd
    ]

    print("\n===================================================")
    print("RUNNING:")
    print(cmd)
    print("===================================================\n")

    proc = subprocess.Popen(
        full_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    output = []

    for line in proc.stdout:
        print(line, end="")
        output.append(line)

    proc.wait()

    proc.stdout_text = "".join(output)
    proc.stderr_text = ""

    return proc

def backup_yaml():

    backup = YAML_PATH.with_suffix(".yaml.bak")

    if not backup.exists():
        shutil.copy(YAML_PATH, backup)
        print(f"Backup creado: {backup}")

    return backup


def restore_yaml():

    backup = YAML_PATH.with_suffix(".yaml.bak")

    if backup.exists():
        shutil.copy(backup, YAML_PATH)
        print("YAML restaurado.")


def load_yaml():

    with open(YAML_PATH, "r") as f:
        return yaml.safe_load(f)


def save_yaml(data):

    with open(YAML_PATH, "w") as f:
        yaml.dump(data, f, sort_keys=False)


def apply_config(cfg):

    data = load_yaml()

    # ========================================================
    # parámetros variables
    # ========================================================
    for key in SAFE_KEYS:
            if key in cfg:
                data[key] = cfg[key]
    

    save_yaml(data)

def build_exists():

    final_gds = (
        BUILD_ROOT
        / "con32bits_parall"
        / "gds"
        / "con32bits_parall.gds"
    )

    final_def = (
        BUILD_ROOT
        / "con32bits_parall"
        / "def"
        / "con32bits_parall.def"
    )

    return final_gds.exists() and final_def.exists()
def shutdown_pc(sync=False,shutdown=False):
    print("\n==========================================")
    print("Sync...")
    print("==========================================\n")
    if sync:
        os.system("bash $HOME/eda/orionsincronizar.sh n")
    time.sleep(10)
    print("\n==========================================")
    print("APAGANDO PC...")
    print("==========================================\n")
    if shutdown:
        os.system("sudo poweroff -f")


def clean_previous_run():

    build_path = BUILD_ROOT / "con32bits_parall"

    if build_path.exists():
        shutil.rmtree(build_path)

    runs_path = HOST_MULTIMACRO / "librelane" / "runs"

    if runs_path.exists():
        shutil.rmtree(runs_path)

    print("Build y runs anteriores borrados.")


# ============================================================
# MAIN
# ============================================================

backup_yaml()

success = False

try:

    for idx, cfg in enumerate(CONFIGS):

        print("\n\n")
        print("################################################")
        print(f"INTENTO {idx+1}")
        print(cfg["name"])
        print("################################################")

        clean_previous_run()

        apply_config(cfg)

        print("\nYAML actualizado.\n")

        cmd = textwrap.dedent(f'''
            cd {CONTAINER_MULTIMACRO}

            source sak-pdk-script.sh {PDK_NAME} {STD_CELL_LIB}

            librelane librelane/con32bits_parall_macro.yaml \\
                --pdk {PDK_NAME} \\
                --pdk-root {CONTAINER_FORK}/gf180mcu \\
                --manual-pdk \\
                --save-views-to {CONTAINER_MULTIMACRO}/build/con32bits_parall
        ''').strip()

        start = datetime.now()

        proc = run_shell(cmd, timeout=28800)

        end = datetime.now()

        print(f"\nDuración: {end - start}")

        # ====================================================
        # GUARDAR LOG
        # ====================================================

        log_file = HOST_MULTIMACRO / f"log_{cfg['name']}.txt"

        with open(log_file, "w") as f:

            f.write(proc.stdout_text)
            f.write("\n\n================ STDERR ================\n\n")
            f.write(proc.stdout_text)

        print(f"Log guardado: {log_file}")

        # ====================================================
        # ÉXITO
        # ====================================================

        if proc.returncode == 0 and build_exists():

            print("\n\n======================================")
            print("GDS GENERADO CORRECTAMENTE")
            print("======================================\n")
        
            # ====================================================
            # guardar YAML ganador
            # ====================================================
        
            success_yaml = YAML_PATH.parent / f"SUCCESS_{cfg['name']}.yaml"
        
            shutil.copy(YAML_PATH, success_yaml)
        
            print(f"YAML exitoso guardado:")
            print(success_yaml)
        
            # ====================================================
            # guardar LOG
            # ====================================================
        
            log_path = HOST_MULTIMACRO / f"SUCCESS_{cfg['name']}.log"
        
            with open(log_path, "w") as f:
                f.write(proc.stdout)
                f.write("\n\nSTDERR:\n\n")
                f.write(proc.stderr)
        
            print(f"LOG guardado:")
            print(log_path)
        
            # ====================================================
            # archivo en escritorio
            # ====================================================
        
            desktop = Path.home() / "Desktop"
        
            marker = desktop / "GDS_EXITOSO.txt"
        
            with open(marker, "w") as f:
                f.write(f"GDS generado correctamente\n")
                f.write(f"Configuracion: {cfg['name']}\n")
                f.write(f"Hora: {datetime.now()}\n")
        
            print(f"Archivo creado en escritorio:")
            print(marker)
        
            success = True
        
            break

        else:

            print("\nNo se encontró GDS/LEF.")
            print("Siguiente intento...\n")

            time.sleep(10)

finally:

    restore_yaml()


# ============================================================
# FINAL
# ============================================================

desktop = Path.home()

if success:

    success_file = desktop / "GDS_EXITOSO.txt"

    with open(success_file, "w") as f:

        f.write("=====================================\n")
        f.write("LIBRELANE TERMINO CORRECTAMENTE\n")
        f.write("=====================================\n\n")

        f.write(f"Configuracion exitosa:\n")
        f.write(f"{cfg['name']}\n\n")

        f.write(f"Hora:\n")
        f.write(f"{datetime.now()}\n\n")

        f.write("GDS generado en:\n")
        f.write(
            str(
                BUILD_ROOT
                / "con32bits_parall"
                / "gds"
                / "con32bits_parall.gds"
            )
        )

    print("\nGDS exitoso.")
    print(f"Archivo creado: {success_file}")

    shutdown_pc(sync=sync_value,shutdown=shutdown_value)

else:

    fail_file = desktop / "FALLO_FLOW.txt"

    with open(fail_file, "w") as f:

        f.write("=====================================\n")
        f.write("NINGUNA CONFIGURACION FUNCIONO\n")
        f.write("=====================================\n\n")

        f.write(f"Hora:\n")
        f.write(f"{datetime.now()}\n\n")

        f.write("Revisar logs en:\n")
        f.write(str(HOST_MULTIMACRO))
        f.write("\n\n")

        f.write("Logs generados:\n\n")

        for c in CONFIGS:

            f.write(f"log_{c['name']}.txt\n")

    print("\nNo funcionó ninguna configuración.")
    print(f"Archivo creado: {fail_file}")

    shutdown_pc(sync=sync_value,shutdown=shutdown_value)

