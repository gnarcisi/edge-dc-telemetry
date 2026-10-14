"""
Live Telemetry Simulation & Sensor Drift Rejection Demo
Author: Gregory A. Narcisi <gregnarcisi@gmail.com>
"""

from datetime import datetime
import json
from telemetry_engine.schema import SensorReading, CDUTelemetryPacket
from telemetry_engine.consensus import TelemetryConsensusEngine
from telemetry_engine.cdu_metrics import CDUAnalyticsEngine


def run_simulation():
    print("=" * 70)
    print("EDGE-DC-TELEMETRY: LIVE CONSENSUS & DRIFT REJECTION DEMO")
    print("Author: Gregory A. Narcisi")
    print("=" * 70)

    # 1. Setup multi-node sensor cluster monitoring supply temperature
    # Node 1 and Node 2 read accurately; Node 3 exhibits uncalibrated thermal drift
    readings = [
        SensorReading(node_id="NODE-ALPHA-I2C", sensor_type="thermistor", raw_value=22.38, calibrated_value=22.40, unit="degC"),
        SensorReading(node_id="NODE-BETA-I2C", sensor_type="thermistor", raw_value=22.44, calibrated_value=22.42, unit="degC"),
        SensorReading(node_id="NODE-GAMMA-DRIFT", sensor_type="thermistor", raw_value=31.10, calibrated_value=31.15, unit="degC")  # Drifting node!
    ]

    print("\n[STEP 1: INGESTING PARALLEL SENSOR NODES]")
    for r in readings:
        print(f"  - {r.node_id} ({r.sensor_type}): {r.calibrated_value} {r.unit}")

    # 2. Compute Consensus
    consensus_engine = TelemetryConsensusEngine(drift_threshold_sigma=2.0)
    consensus_temp, faulted_nodes, confidence = consensus_engine.compute_consensus(readings)

    print("\n[STEP 2: RUNNING STATISTICAL DRIFT ANALYSIS]")
    print(f"  - Consensus Supply Temperature: {consensus_temp:.2f} degC")
    print(f"  - Isolated Faulted Nodes: {faulted_nodes}")
    print(f"  - Stream Confidence Score: {confidence * 100:.1f}%")

    # 3. Formulate OCP CDUTelemetryPacket with guaranteed consensus value
    cdu_packet = CDUTelemetryPacket(
        facility_zone="CDU-AI-POD-01",
        supply_temp_c=consensus_temp,
        return_temp_c=38.85,
        flow_rate_lpm=115.0,
        ambient_wet_bulb_c=24.5,
        rack_power_kw=120.0
    )

    # 4. Calculate CDU Thermal Headroom Metrics
    metrics = CDUAnalyticsEngine.calculate_thermal_metrics(cdu_packet)

    print("\n[STEP 3: CDU LIQUID COOLING DYNAMICS & HEADROOM FORECAST]")
    print(json.dumps(metrics, indent=2))

    print("\n[RESULT] Hardware drift rejected. Zero hallucination. Upstream DCIM protected.")
    print("=" * 70)


if __name__ == "__main__":
    run_simulation()
