#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ford Mondeo Mk4 2007 TDCi Full Diagnostics Tool
"""

import obd
import serial.tools.list_ports
import os
from time import sleep

# NerdFont Icons
NF = {
    "car": "󰄋",
    "link": "",
    "error": "",
    "check": "󱐋",
    "ok": "󰄴",
    "warning": "",
    "broom": "󰃢",
    "exit": "󰿅",
    "reconnect": "󰴽"
}

# Set log level (change to DEBUG if you want verbose logs)
obd.logger.setLevel(obd.logging.ERROR)

# === Utility ===
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    input(f"\n⏸️  Press Enter to continue...")

# === Serial Port Listing ===
def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    if not ports:
        print(f"{NF['error']} No serial ports found.")
    else:
        print("Available serial ports:")
        for i, port in enumerate(ports):
            print(f"  [{i}] {port.device} - {port.description}")
    return ports

# === OBD Connection with port selection ===
def connect():
    print(f"{NF['link']} Connecting to OBD-II...")

    ports = list_serial_ports()
    if not ports:
        return None

    port = None
    if len(ports) > 1:
        choice = input("Select serial port index or press Enter to auto-connect: ").strip()
        if choice.isdigit() and int(choice) < len(ports):
            port = ports[int(choice)].device
    else:
        port = ports[0].device

    try:
        if port:
            print(f"Trying port {port} ...")
            conn = obd.OBD(port)  # connect to chosen port, default baudrate 9600
        else:
            print("Auto-connecting...")
            conn = obd.OBD()  # auto connect

        if conn.is_connected():
            print(f"{NF['ok']} Connected to {conn.port_name()}")
            return conn
        else:
            print(f"{NF['error']} No connection. Check ignition and adapter.")
    except Exception as e:
        print(f"{NF['error']} Failed to connect: {e}")

    return None

# === Diagnostics ===
def read_codes(conn):
    if conn:
        print(f"{NF['check']} Reading Diagnostic Trouble Codes...")
        codes = conn.get_dtc()
        if codes and codes.value:
            print(f"{NF['warning']} Active DTCs:")
            for code, desc in codes.value:
                print(f"  {NF['error']} {code}: {desc}")
        else:
            print(f"{NF['ok']} No trouble codes detected.")
    else:
        print(f"{NF['error']} Not connected.")
    pause()

def clear_codes(conn):
    if conn:
        print(f"{NF['broom']} Clearing DTCs...")
        response = conn.clear_dtc()
        if response.is_successful():
            print(f"{NF['ok']} DTCs cleared!")
        else:
            print(f"{NF['error']} Failed to clear DTCs.")
    else:
        print(f"{NF['error']} Not connected.")
    pause()

# === Menu ===
def menu(conn):
    while True:
        clear()
        print(f"{NF['car']} Ford Mondeo Mk4 1.8 TDCi Diagnostics\n")
        print(f"{NF['link']} Connection: {'Connected' if conn and conn.is_connected() else '❌ Not Connected'}\n")
        print(f"1. {NF['check']}  Read DTCs")
        print(f"2. {NF['broom']}  Clear DTCs")
        print(f"3. {NF['reconnect']}  Reconnect")
        print(f"4. {NF['exit']}  Exit\n")

        choice = input("Choose an option (1–4): ").strip()
        if choice == '1':
            read_codes(conn)
        elif choice == '2':
            clear_codes(conn)
        elif choice == '3':
            conn = connect()
        elif choice == '4':
            print(f"{NF['exit']} Exiting. Drive safe!")
            break
        else:
            print(f"{NF['error']} Invalid option.")
            pause()

# === Start ===
if __name__ == "__main__":
    connection = connect()
    menu(connection)

