# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from pathlib import Path
import os
import shutil
import subprocess
import textwrap


# ---- run flags ---------------------------------------------------------
RUN_STAGE_FORK    = True   # 1.2: copy in-repo workshop padring into the bind-mount (~200 KB)
RUN_CLONE_PDK     = False   # 1.3: clone wafer-space GF180 PDK @ 1.8.0 (~500 MB)
RUN_STAGE_FILES   = True   # 2:   copy rtl/ + tb/ + librelane/ into bind-mount
RUN_COCOTB        = True   # 3:   ~15 s, counter + alu tests (RTL)

RUN_GLSIM         = True   # 5b:  ~15 s, post-synth GL sim (optional)
RUN_PATCH_TOP     = True   # 6:   write chip_core_multi.sv + patched config.yaml into fork copy
RUN_CHIP_TOP      = True   # 7:   ~60-90 min, SLOT=workshop full chip flow
RUN_HARDEN_four_palabras= False
RUN_HARDEN_Uart= False
RUN_HARDEN_Uart_tx=False

RUN_HARDEN_salida= False
RUN_HARDEN_acti= False
# ---- container ---------------------------------------------------------
CONTAINER_NAME = 'gf180'

# ---- upstream references (Apache-2.0) ---------------------------------
# Padring template is vendored next to this notebook so the flow runs
# offline. Upstream of record (for attribution): Mauricio-xx/chipathon-2026-gf180mcu-padring.
PDK_FORK_URL = 'https://github.com/wafer-space/gf180mcu.git'
PDK_FORK_TAG = '1.8.0'




# ---- host paths --------------------------------------------------------
# The fork gets its own dedicated path for this example so we never
# corrupt another workspace (e.g. the chipathon_padring/template/
# baseline used by notebook 03).
HOST_WORKSPACE  = Path.home() / 'eda' / 'designs'
HOST_FORK       = HOST_WORKSPACE / 'convChip' / 'template'
HOST_PDK        = HOST_FORK / 'gf180mcu'
HOST_MULTIMACRO = HOST_WORKSPACE / 'convChip' / 'user_macros'

# ---- container paths ---------------------------------------------------
CONTAINER_FORK       = '/foss/designs/convChip/template'
CONTAINER_MULTIMACRO = '/foss/designs/convChip/user_macros'

# ---- PDK identifiers ---------------------------------------------------
PDK_NAME     = 'gf180mcuD'
STD_CELL_LIB = 'gf180mcu_fd_sc_mcu7t5v0'

print(f'Bind-mount destination: {HOST_MULTIMACRO}  (container: {CONTAINER_MULTIMACRO})')
print(f'Dedicated fork copy:    {HOST_FORK}  (container: {CONTAINER_FORK})')





def run_or_print(cmd, do_it, *, shell_on_container=False, timeout=None):
    """Print a command in dry-run mode; execute it when ``do_it`` is True.

    When ``shell_on_container=True`` the command is a shell snippet to
    run inside ``docker exec gf180 bash -lc ...``; otherwise it is an
    argv list executed on the host. Returns the ``CompletedProcess``
    when executed, ``None`` otherwise.
    """
    if shell_on_container:
        print(f"$ docker exec {CONTAINER_NAME} bash -lc '<script>'")
        print(textwrap.indent(cmd, '  | '))
    else:
        print('$ ' + ' '.join(str(x) for x in cmd))
    if not do_it:
        print('  (skipped -- flip the RUN_* flag to execute)\n')
        return None
    args = (
        ['docker', 'exec', CONTAINER_NAME, 'bash', '-lc', cmd]
        if shell_on_container else list(cmd)
    )
    proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    if proc.stdout.strip():
        print(proc.stdout[-4000:])
    if proc.returncode != 0 and proc.stderr.strip():
        print('STDERR (tail):')
        print(proc.stderr[-2000:])
    print(f'  returncode={proc.returncode}\n')
    return proc



def ok(label, cond, detail=''):
    tag = 'OK ' if cond else '!! '
    print(f'{tag}{label}' + (f'  -- {detail}' if detail else ''))
    return cond


def sintesis(modulo,RUN_HARDEN):
    
    
    harden_modulo = textwrap.dedent(f'''
        cd {CONTAINER_MULTIMACRO}
        source sak-pdk-script.sh {PDK_NAME} {STD_CELL_LIB}
        librelane librelane/{modulo}_macro.yaml \\
            --pdk {PDK_NAME} \\
            --pdk-root {CONTAINER_FORK}/gf180mcu \\
            --manual-pdk \\
            --save-views-to {CONTAINER_MULTIMACRO}/build/{modulo}
    ''').strip()
    
    
    print(harden_modulo)
    
    print(f"k build/{modulo}/gds/{modulo}.gds &")
    
    run_or_print(harden_modulo, RUN_HARDEN,
                 shell_on_container=True, timeout=900)


proc = subprocess.run(
    ['docker', 'ps', '--filter', f'name={CONTAINER_NAME}', '--format', '{{.Names}}'],
    capture_output=True, text=True,
)
container_up = CONTAINER_NAME in proc.stdout
ok(f"Container '{CONTAINER_NAME}' running", container_up)



if not HOST_PDK.exists():
    clone_pdk = ['git', 'clone', '--depth', '1', '--branch', PDK_FORK_TAG,
                 PDK_FORK_URL, str(HOST_PDK)]
    run_or_print(clone_pdk, RUN_CLONE_PDK, timeout=600)
ok('wafer-space PDK fork present', HOST_PDK.exists(), str(HOST_PDK))




harden_uart_ultimo = textwrap.dedent(f'''
    set -e
    cd {CONTAINER_MULTIMACRO}
    source sak-pdk-script.sh {PDK_NAME} {STD_CELL_LIB}
    librelane librelane/uart_ultimo_macro.yaml \\
        --pdk {PDK_NAME} \\
        --pdk-root {CONTAINER_FORK}/gf180mcu \\
        --manual-pdk \\
        --save-views-to {CONTAINER_MULTIMACRO}/build/uart_ultimo
''').strip()


print(harden_uart_ultimo)


run_or_print(harden_uart_ultimo, RUN_HARDEN_Uart,
             shell_on_container=True, timeout=900)


import csv

metrics_path = HOST_MULTIMACRO / "build" / "uart_ultimo" / "metrics.csv"
wanted = [
    "design__die__area__um2",
    "design__instance__count__stdcell",
    "timing__setup_vio__count",
    "timing__hold_vio__count",
    "magic__drc_error__count",
    "klayout__drc_error__count",
    "design__lvs_error__count",
    "power__total",
]

if not metrics_path.exists():
    print(f"metrics.csv not found: {metrics_path}")
    print("Did Step 5 complete? Set RUN_LIBRELANE = True and re-run.")
else:
    print(f"Reading {metrics_path}\n")
    found = {}
    with metrics_path.open() as fh:
        for row in csv.reader(fh):
            if row and row[0] in wanted:
                found[row[0]] = row[1] if len(row) > 1 else ""
    for key in wanted:
        print(f"  {key:45s} {found.get(key, '(missing)')}")




harden_four_palabras_uart = textwrap.dedent(f'''
    cd {CONTAINER_MULTIMACRO}
    source sak-pdk-script.sh {PDK_NAME} {STD_CELL_LIB}
    librelane librelane/four_palabras_uart_macro.yaml \\
        --pdk {PDK_NAME} \\
        --pdk-root {CONTAINER_FORK}/gf180mcu \\
        --manual-pdk \\
        --save-views-to {CONTAINER_MULTIMACRO}/build/four_palabras_uart
''').strip()


print(harden_four_palabras_uart)



run_or_print(harden_uart_ultimo, RUN_HARDEN_four_palabras,
             shell_on_container=True, timeout=900)





import csv

metrics_path = HOST_MULTIMACRO / "build" / "four_palabras_uart" / "metrics.csv"
wanted = [
    "design__die__area__um2",
    "design__instance__count__stdcell",
    "timing__setup_vio__count",
    "timing__hold_vio__count",
    "magic__drc_error__count",
    "klayout__drc_error__count",
    "design__lvs_error__count",
    "power__total",
]

if not metrics_path.exists():
    print(f"metrics.csv not found: {metrics_path}")
    print("Did Step 5 complete? Set RUN_LIBRELANE = True and re-run.")
else:
    print(f"Reading {metrics_path}\n")
    found = {}
    with metrics_path.open() as fh:
        for row in csv.reader(fh):
            if row and row[0] in wanted:
                found[row[0]] = row[1] if len(row) > 1 else ""
    for key in wanted:
        print(f"  {key:45s} {found.get(key, '(missing)')}")



harden_uart_tx_4in4 = textwrap.dedent(f'''
    cd {CONTAINER_MULTIMACRO}
    source sak-pdk-script.sh {PDK_NAME} {STD_CELL_LIB}
    librelane librelane/uart_tx_4in4_macro.yaml \\
        --pdk {PDK_NAME} \\
        --pdk-root {CONTAINER_FORK}/gf180mcu \\
        --manual-pdk \\
        --save-views-to {CONTAINER_MULTIMACRO}/build/uart_tx_4in4
''').strip()


print(harden_uart_tx_4in4)



run_or_print(harden_four_palabras_uart, RUN_HARDEN_Uart_tx,
             shell_on_container=True, timeout=900)




sintesis("four_palabras_uart",False)
sintesis("uart_tx_4in4",False)
sintesis("salida",False)
sintesis("acti",False)

sintesis("con32bits_parall",False)
sintesis("mult_16b_bf",False)
sintesis("suma_16b",False)
sintesis("punt_mo_seg",False)

# cd /foss/designs/convChip/user_macros
# source sak-pdk-script.sh gf180mcuD gf180mcu_fd_sc_mcu7t5v0
# librelane librelane/con32bits_parall_macro.yaml \
#     --pdk gf180mcuD \
#     --pdk-root /foss/designs/convChip/template/gf180mcu \
#     --manual-pdk \
#     --save-views-to /foss/designs/convChip/user_macros/build/con32bits_parall
# k build/con32bits_parall/gds/con32bits_parall.gds &