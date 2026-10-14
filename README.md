# Edge-DC-Telemetry: Zero-Drift Telemetry & Environmental Consensus for AI Data Centers

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Hardware: RP2040 / ESP32](https://img.shields.io/badge/Hardware-RP2040%20%7C%20ESP32-purple.svg)](https://www.raspberrypi.com/products/rp2040/)
[![Standard: OCP / Redfish Telemetry](https://img.shields.io/badge/Standard-OCP%20%7C%20Redfish-orange.svg)](https://www.opencompute.org/)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://python.org)

> **A hardware-in-the-loop (HITL) physical telemetry and consensus engine for next-generation AI data centers.**  
> Solves sensor drift, packet loss, and environmental hallucination across high-density liquid cooling distribution units (CDUs) and ambient facility weather interlocks.

---

## The Industrial Problem

Next-generation AI training clusters (NVIDIA GB200/NVL72 and beyond) push rack power densities from 40 kW to **120 kW – 1 MW per rack**, requiring closed-loop liquid cooling distribution units (CDUs) coupled to exterior cooling towers.

In production environments, automated facility management systems frequently suffer from **telemetry blind spots and sensor drift**:
1. **The Telemetry Drift Gap:** Ambient wet-bulb temperature, barometric pressure drops, and supply-manifold thermistors drift over time. Uncalibrated single-point sensors cause automated cooling-tower interlocks to cycle improperly, triggering catastrophic thermal throttling or emergency shutdowns (e.g. the CME CyrusOne facility outage).
2. **Firmware Packet Jitter & Power Drops:** Transient brownouts or edge microcontroller restarts corrupt buffer rings, causing upstream DCIM software to act on stale or hallucinated metrics.
3. **The IT / Facilities Protocol Divide:** Operational technology (OT/Modbus/BACnet) rarely integrates cleanly with modern agentic orchestration and Redfish data models.

**Edge-DC-Telemetry** bridges this gap. It deploys an edge consensus harness across dual-core microcontrollers (Raspberry Pi RP2040 and Espressif ESP32), applying multi-point calibration, Kalman anomaly filtering, and zero-trust schema validation to provide guaranteed ground truth.

---

## Architectural Topology

```
   ┌──────────────────────────────────────────────────────────────┐
   │                PHYSICAL SENSOR TELEMETRY BUS                 │
   │   - Dual I2C Barometric/Temp Arrays (BMP280/BME280)          │
   │   - Analog Heat-Exchanger Differential Flow Voltage (ADC)    │
   │   - Ambient Cooling-Tower Anemometer & Wet-Bulb Array        │
   └──────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
   ┌──────────────────────────────────────────────────────────────┐
   │             RP2040 / ESP32 EDGE FIRMWARE HARNESS             │
   │   - Non-Blocking Ring Buffer Memory (Zero Telemetry Loss)     │
   │   - Hardware Watchdog Failover (Power-Loss Resilience)       │
   │   - Microsecond Timestamped Telemetry Packets                │
   └──────────────────────────────┬───────────────────────────────┘
                                  │ (JSON / Modbus over Serial / TCP)
                                  ▼
   ┌──────────────────────────────────────────────────────────────┐
   │         SOVEREIGN CONSENSUS & DRIFT REJECTION ENGINE         │
   │   - Multi-Sensor Consensus Validation (Tri-Modular Drift)    │
   │   - Kalman Anomaly Detection & Statistical Outlier Clamping  │
   │   - OCP CDU Metric Schema Enforcement (Redfish Compliant)    │
   └──────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
               [GUARANTEED GROUND TRUTH TELEMETRY STREAM]
               - Predictive Cooling-Headroom Margin (kW)
               - Real-Time Thermal Dissipation Rate (BTU/hr)
               - Zero Hallucination / Zero Out-of-Bound Jitter
```

---

## Key Technical Features

### 1. Tri-Modular Sensor Consensus & Drift Rejection
Single sensors lie; sensor clusters reveal truth. The consensus engine ingests concurrent streams from parallel physical sensing nodes. If a thermistor or pressure transducer drifts beyond $\pm 2.5\sigma$ of the calibrated baseline, the anomaly engine isolates the faulted node, flags an automated calibration ticket, and re-weights the aggregate stream using healthy nodes.

### 2. High-Density Liquid Cooling (CDU) Headroom Modeling
Calculates instantaneous heat rejection capability based on:
$$\dot{Q} = \dot{m} \cdot C_p \cdot (T_{\text{return}} - T_{\text{supply}})$$
Couples dynamic fluid thermal mass with ambient external wet-bulb temperatures to forecast cooling headroom 30–60 minutes in advance of AI cluster compute surges.

### 3. Power-Loss Resilience & Failover Storage
Embedded firmware incorporates ring-buffer persistence. In the event of network disruption or power-rail transients, up to 10,000 telemetry packets are safely buffered in local non-volatile memory and deterministically flushed upon connection restoration—guaranteeing zero historical data holes.

### 4. Zero-Trust Schema Validation
All inbound telemetry is audited against strict Pydantic schemas. Corrupted, truncated, or out-of-order packets are rejected at the ingestion boundary with microsecond audit logging, preventing hallucinated parameters from reaching upstream autonomous facility agents.

---

## Directory Structure

```
edge-dc-telemetry/
├── firmware/                     # Embedded C++ / MicroPython hardware firmware
│   └── rp2040_telemetry_node.py  # RP2040 ring buffer & multi-sensor ADC sampling
├── telemetry_engine/             # Python consensus & analytics framework
│   ├── __init__.py
│   ├── consensus.py              # Statistical consensus & drift filtering
│   ├── cdu_metrics.py            # Liquid cooling headroom & thermal calculations
│   └── schema.py                 # OCP/Redfish compliant telemetry data contracts
├── examples/
│   └── simulate_telemetry.py     # Live simulation runner demonstrating drift rejection
├── tests/
│   └── test_consensus.py         # Automated test suite for sensor anomaly handling
├── LICENSE
└── README.md
```

---

## Quickstart & Simulation

```bash
# Clone the repository
git clone https://github.com/gnarcisi/edge-dc-telemetry.git
cd edge-dc-telemetry

# Install dependencies
pip install pydantic numpy

# Run the live consensus and drift-rejection simulation
python examples/simulate_telemetry.py
```

### Example Telemetry Audit Output:
```json
{
  "timestamp": "2026-10-14T15:26:00Z",
  "facility_zone": "CDU-POD-04",
  "rack_density_kw": 128.4,
  "consensus_status": "LOCKED",
  "active_nodes": 3,
  "isolated_faulted_nodes": 0,
  "metrics": {
    "supply_temp_c": 22.41,
    "return_temp_c": 38.82,
    "delta_t_c": 16.41,
    "heat_rejection_kw": 121.7,
    "cooling_headroom_margin_kw": 43.3
  },
  "schema_validated": true
}
```

---

## Author & Provenance
**Architect:** Gregory A. Narcisi  
**Specialization:** Principal AI Systems Evaluator & Physical Telemetry Architect  
**Contact:** gregnarcisi@gmail.com | [LinkedIn](https://www.linkedin.com/in/greg-narcisi)  
**License:** MIT Open Source License (2026)
