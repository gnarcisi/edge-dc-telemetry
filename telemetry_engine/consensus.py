"""
Consensus and Sensor Drift Rejection Engine
Author: Gregory A. Narcisi <gregnarcisi@gmail.com>
"""

from typing import List, Dict, Tuple
import numpy as np
from .schema import SensorReading


class TelemetryConsensusEngine:
    """
    Evaluates multi-node sensor clusters, isolates failing or drifting hardware sensors,
    and produces deterministic consensus metrics for AI data center cooling systems.
    """

    def __init__(self, drift_threshold_sigma: float = 2.5):
        self.drift_threshold_sigma = drift_threshold_sigma
        self.node_history: Dict[str, List[float]] = {}

    def compute_consensus(self, readings: List[SensorReading]) -> Tuple[float, List[str], float]:
        """
        Computes the weighted consensus value across parallel sensor nodes.
        Returns:
            (consensus_value, list_of_faulted_nodes, confidence_score)
        """
        if not readings:
            raise ValueError("Consensus calculation requires at least one sensor reading.")

        if len(readings) == 1:
            return readings[0].calibrated_value, [], 1.0

        values = np.array([r.calibrated_value for r in readings])
        node_ids = [r.node_id for r in readings]

        median_val = np.median(values)
        mad = np.median(np.abs(values - median_val))
        sigma_est = 1.4826 * mad if mad > 1e-6 else np.std(values)

        faulted_nodes = []
        healthy_values = []

        for r in readings:
            val = r.calibrated_value
            if sigma_est > 1e-4:
                z_score = abs(val - median_val) / sigma_est
            else:
                z_score = 0.0

            if z_score > self.drift_threshold_sigma:
                faulted_nodes.append(r.node_id)
            else:
                healthy_values.append(val)

        if not healthy_values:
            healthy_values = values.tolist()

        consensus_value = float(np.mean(healthy_values))
        confidence = float(len(healthy_values) / len(readings))

        return consensus_value, faulted_nodes, confidence
