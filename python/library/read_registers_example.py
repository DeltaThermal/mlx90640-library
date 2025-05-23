#!/usr/bin/env python3
"""
Example script demonstrating how to read MLX90640 registers using the new read_registers function.
This example uses register addresses from register_layout.csv.
"""

import sys
import csv
import os
import json
from datetime import datetime
sys.path.insert(0, "./build/lib.linux-armv7l-2.7")

import MLX90640 as mlx

# Function to get Raspberry Pi serial number
def get_pi_serial():
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.startswith('Serial'):
                    return line.split(':')[1].strip()
    except:
        pass
    return "unknown"

# Load register definitions from CSV
register_map = {}
csv_path = os.path.join(os.path.dirname(__file__), '../../register_layout.csv')
with open(csv_path, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) >= 2:
            addr = int(row[0], 16)
            name = row[1]
            register_map[addr] = name

# Initialize the sensor
print("Setting up MLX90640 sensor...")
mlx.setup(16)  # 16 FPS

print("\nReading registers from MLX90640 (using register_layout.csv):")

# Dictionary to store register data for JSON output
register_data = {}

# Read all EEPROM registers defined in CSV
print("\nEEPROM Registers:")
for addr, name in sorted(register_map.items()):
    reg_value = mlx.read_registers(addr, 1)
    if reg_value:
        print(f"   0x{addr:04X} ({name}): 0x{reg_value[0]:04X}")
        # Store in dictionary with hex format
        register_data[f"0x{addr:04X}"] = {
            'name': name,
            'value': reg_value[0]
        }
    else:
        print(f"   0x{addr:04X} ({name}): Read failed")

# Read all EEPROM data as a block (more efficient)
print("\nEEPROM Data (block read from 0x2400-0x240F):")
eeprom_start = min(register_map.keys())
eeprom_end = max(register_map.keys())
eeprom_size = eeprom_end - eeprom_start + 1

eeprom_data = mlx.read_registers(eeprom_start, eeprom_size)
if eeprom_data:
    for i, val in enumerate(eeprom_data):
        addr = eeprom_start + i
        if addr in register_map:
            name = register_map[addr]
            print(f"   0x{addr:04X} ({name}): 0x{val:04X}")

# Get Raspberry Pi serial number
pi_serial = get_pi_serial()

# Save register data to JSON file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
json_filename = f"mlx90640_registers_{pi_serial}_{timestamp}.json"

with open(json_filename, 'w') as f:
    json.dump(register_data, f, indent=2)

print(f"\nRegister data saved to: {json_filename}")

# Cleanup
mlx.cleanup()
print("\nDone!")