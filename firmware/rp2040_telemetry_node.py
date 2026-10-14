"""
MicroPython / CircuitPython Telemetry Node Firmware for RP2040
Target: Raspberry Pi RP2040 / Pico / Feather RP2040
Author: Gregory A. Narcisi <gregnarcisi@gmail.com>
"""

import time
import json

# Hardware ring buffer implementation to prevent telemetry loss during network dropouts
BUFFER_MAX_SIZE = 1000
ring_buffer = []

def read_simulated_hardware_sensors():
    """
    Simulates analog thermistor ADC readings, supply manifold voltage, and barometric pressure.
    In physical deployment, replaces with machine.ADC(26) and machine.I2C(0) calls.
    """
    timestamp = time.time()
    # Emulates 3.3V ADC reading scaled to Celsius
    supply_temp_c = 22.4 + (hash(str(timestamp)) % 10) * 0.05
    return_temp_c = 38.6 + (hash(str(timestamp + 1)) % 15) * 0.08
    pressure_hpa = 1013.25 - (hash(str(timestamp + 2)) % 8) * 0.1
    flow_rate_lpm = 112.5

    return {
        "timestamp_epoch": timestamp,
        "supply_temp_c": round(supply_temp_c, 2),
        "return_temp_c": round(return_temp_c, 2),
        "pressure_hpa": round(pressure_hpa, 2),
        "flow_rate_lpm": round(flow_rate_lpm, 2),
        "buffer_depth": len(ring_buffer)
    }

def enqueue_packet(packet):
    global ring_buffer
    if len(ring_buffer) >= BUFFER_MAX_SIZE:
        ring_buffer.pop(0)  # Evict oldest entry on overflow
    ring_buffer.append(packet)

def flush_buffer():
    global ring_buffer
    packets = list(ring_buffer)
    ring_buffer = []
    return packets

if __name__ == "__main__":
    print("[RP2040 FIRMWARE INITIALIZED] Telemetry Node Active...")
    for _ in range(5):
        sample = read_simulated_hardware_sensors()
        enqueue_packet(sample)
        print(f"Sample Enqueued: {json.dumps(sample)}")
        time.sleep(0.1)
