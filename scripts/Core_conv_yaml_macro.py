#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 15:24:23 2026

@author: ral298
"""

from pathlib import Path
import os
import shutil

import textwrap

HOST_WORKSPACE  = Path.home() / 'eda' / 'designs'
HOST_FORK       = HOST_WORKSPACE / 'convChip' / 'user_macros'
HOST_PDK        = HOST_FORK / 'gf180mcu'
HOST_MULTIMACRO = HOST_WORKSPACE / 'convChip' / 'user_macros'

def patch_top():
    try:
        import yaml
    except ImportError as e:
        raise RuntimeError(
            "PyYAML is not available in the host kernel. "
            "Install it (e.g. `pip install pyyaml`) before flipping "
            "RUN_PATCH_TOP=True. The container side does not need it."
        ) from e

    
    # 2. Cargar el config.yaml de LibreLane de tu proyecto
    cfg_path = HOST_FORK / 'librelane' / 'con32bits_parall_macro.yaml'
    cfg = yaml.safe_load(cfg_path.read_text())

    # Actualizamos el DESIGN_NAME al tuyo real
    cfg['DESIGN_NAME'] = 'con32bits_parall'

    # Lista de Verilog limpia: Quitamos punt_mo_seg.v porque ya es MACRO
    cfg['VERILOG_FILES'] = [
        'dir::../rtl/con32bits_parall.v',
    ]
    cfg['PDN_CFG'] = 'dir::pdn_cfg.tcl'
    # Las 9 esquinas estándar que exige GF180MCU para Signoff de tiempos
    CORNERS = [
        'nom_tt_025C_5v00', 'nom_ss_125C_4v50', 'nom_ff_n40C_5v50',
        'min_tt_025C_5v00', 'min_ss_125C_4v50', 'min_ff_n40C_5v50',
        'max_tt_025C_5v00', 'max_ss_125C_4v50', 'max_ff_n40C_5v50',
    ]
    
    from pathlib import Path
    build = Path('/foss/designs/convChip/user_macros') / 'build'
    
    # Función interna para estructurar las 9 esquinas de las librerías (.lib)
    def macro_entry_multi(name, instances_dict):
        base = build / name
        lib_map = {
            corner: [str(base / 'lib' / corner / f'{name}__{corner}.lib')]
            for corner in CORNERS
        }
        
        # Mapea cada instancia con su nombre en el Verilog y sus coordenadas físicas
        inst_config = {}
        for inst_name, xy in instances_dict.items():
            # Nota: Si tus instancias están directo en el top, se usa inst_name. 
            # Si están dentro de un core intermedio, cámbialo a f'i_chip_core.{inst_name}'
            inst_config[f'{inst_name}'] = {
                'location': xy,
                'orientation': 'N'
            }
            
        return {
            'gds': [str(base / 'gds' / f'{name}.gds')],
            'lef': [str(base / 'lef' / f'{name}.lef')],
            'vh':  [str(base / 'nl'  / f'{name}.nl.v')],
            'lib': lib_map,
            'instances': inst_config,
        }

    cfg.setdefault('MACROS', {})
    
    # 3. Mapear tus 4 instancias del módulo geométrico 'punt_mo_seg'
    # Distribuidas dentro de tu espacio del 36% (0 a 1200 micras)
# Al no tener etiqueta el 'begin', Yosys usa 'genblk1' por defecto para el lazo
    instancias_punt = {
        'genblk1[0].u_punt_mo': [100, 100],   # Primera instancia -> Esquina inferior izq.
        'genblk1[1].u_punt_mo': [100, 900],   # Segunda instancia -> Esquina superior izq.
        'genblk1[2].u_punt_mo': [900, 100],   # Tercera instancia -> Esquina inferior der.
        'genblk1[3].u_punt_mo': [900, 900]    # Cuarta instancia   -> Esquina superior der.
    }
    cfg['MACROS']['punt_mo_seg'] = macro_entry_multi('punt_mo_seg', instancias_punt)
    # 4. Conexiones automáticas de la malla de potencia (PDN v3 Schema)
    cfg['PDN_MACRO_CONNECTIONS'] = ['.*u_punt_.* VDD VSS VDD VSS', ]

    # Guardar el archivo YAML modificado manteniendo el formato limpio
    cfg_path.write_text(yaml.safe_dump(cfg, sort_keys=False, default_flow_style=False))
    print(f'Patched {cfg_path} para el top con32bits_parall exitosamente.')


patch_top()