"""
Liquid Cooling (CDU) Headroom & Thermal Dissipation Engine
Author: Gregory A. Narcisi <gregnarcisi@gmail.com>
"""

from typing import Dict
from .schema import CDUTelemetryPacket


class CDUAnalyticsEngine:
    """
    Thermodynamic modeling engine for rack-scale AI liquid cooling systems.
    Computes real-time heat rejection and predictive cooling headroom margin.
    """

    WATER_GLYCOL_HEAT_CAPACITY = 3.85  # kJ / (kg * C) for 25% propylene glycol mix
    FLUID_DENSITY_KG_L = 1.02          # kg / L

    @classmethod
    def calculate_thermal_metrics(cls, packet: CDUTelemetryPacket) -> Dict[str, float]:
        """
        Q_dot = m_dot * Cp * Delta_T
        Computes instantaneous heat rejection in kilowatts and cooling headroom margin.
        """
        delta_t = packet.return_temp_c - packet.supply_temp_c
        mass_flow_rate_kg_s = (packet.flow_rate_lpm / 60.0) * cls.FLUID_DENSITY_KG_L
        heat_rejection_kw = mass_flow_rate_kg_s * cls.WATER_GLYCOL_HEAT_CAPACITY * delta_t

        # Typical maximum rated CDU thermal capacity (e.g. 150 kW rated pod)
        rated_capacity_kw = 160.0
        headroom_margin_kw = max(0.0, rated_capacity_kw - heat_rejection_kw)

        return {
            "delta_t_c": round(delta_t, 2),
            "heat_rejection_kw": round(heat_rejection_kw, 2),
            "cooling_headroom_margin_kw": round(headroom_margin_kw, 2),
            "thermal_efficiency_ratio": round(heat_rejection_kw / max(1.0, packet.rack_power_kw), 3)
        }
