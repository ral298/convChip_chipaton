# ConvChip - Chipathon 2026

Hardware accelerator for convolution operations designed for the Chipathon 2026 GF180MCU workshop.

The project implements a custom digital accelerator capable of performing parallel convolution operations and transmitting the results through a UART interface. The complete RTL was integrated using the Wafer Space GF180MCU project template and synthesized with LibreLane.

---

## Features

- Parallel convolution engine
- 32-bit convolution datapath
- UART output interface
- Fully synthesizable RTL
- Integrated into the Chipathon GF180MCU workshop padring
- Compatible with LibreLane flow

---

## Repository Structure

```
.
├── src/                 RTL source files
├── cocotb/              Testbench and simulation environment
├── librelane/           Physical design configuration
├── ip/                  Workshop IP blocks
├── docs/                Documentation
├── scripts/             Utility scripts
└── README.md
```

---

## RTL Modules

| File | Description |
|------|-------------|
| con32_one_instruction.v | Top Convolution controller |
| con32bits_parall.v | Parallel convolution datapath |
| mult_16b_bf.v | 16-bit multiplier |
| suma_16b.v | 16-bit adder |
| acti.v | Activation for a bit |
| salida.v | Activation for a bit |
| uart_tx_4in4.v | UART, bit unpacking for transmission |
| uart_ultimo.v | UART communication |
| four_palabras_uart.v | UART, bit concatenation for reception |
| punt_mo_seg.v | Dot Product Pipeline. |

---

## Simulation

The verification environment is located in

```
cocotb/tb/
```

Main files:

```
Cocotb testbench
tb.v                 Verilog wrapper
simulation.sh        Simulation script
Makefile             Cocotb Makefile
```

To run the simulation:

```bash
cd cocotb/tb
make
./simulation.sh
```

Waveforms are generated in VCD format and can be inspected using GTKWave.

---

## Physical Design

Physical implementation is performed using LibreLane.

Configuration files are located in

```
librelane/
```

Main configuration:

- config.yaml
- chip_top.sdc
- pdn_cfg.tcl

To build the chip:

```bash
SLOT=workshop make librelane
```

---

## Design Overview

The architecture consists of:

- Parallel convolution engine
- Arithmetic units
- Activation stage
- Output formatter
- UART communication module

The design receives convolution data, processes it in hardware, applies the activation function, and transmits the results through UART.

---

## Tools

- SystemVerilog / Verilog
- Cocotb
- Icarus Verilog
- LibreLane
- GF180MCU PDK
- GTKWave

---

## Authors

Raúl Pérez Núñez

Centro de Investigación en Computación (CIC-IPN)

Chipathon 2026

---

## License

Apache-2.0 (inherits the project template license).
