"""
Edge Data Center Telemetry Schemas (OCP & Redfish Compliant)
Author: Gregory A. Narcisi <gregnarcisi@gmail.com>
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class SensorReading(BaseModel):
    node_id: str = Field(..., description="Unique physical identifier of sensing node")
    sensor_type: str = Field(..., description="Sensor classification (e.g. thermistor, pressure_transducer, flow_meter)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    raw_value: float = Field(..., description="Raw digitized reading from ADC or I2C bus")
    calibrated_value: float = Field(..., description="Zero-drift calibrated physical value")
    unit: str = Field(..., description="Standard unit (degC, hPa, L_min, m_s)")
    is_valid: bool = True


class CDUTelemetryPacket(BaseModel):
    facility_zone: str = Field(..., description="Data center pod or cooling zone identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    supply_temp_c: float = Field(..., ge=5.0, le=50.0, description="CDU primary coolant supply temperature in Celsius")
    return_temp_c: float = Field(..., ge=10.0, le=85.0, description="CDU secondary return coolant temperature in Celsius")
    flow_rate_lpm: float = Field(..., ge=0.0, le=1000.0, description="Coolant volumetric flow rate in Liters/minute")
    ambient_wet_bulb_c: float = Field(..., description="Exterior ambient wet-bulb temperature")
    rack_power_kw: float = Field(..., ge=0.0, description="Total electrical IT compute power in kW")
    heat_rejection_kw: Optional[float] = None
    cooling_headroom_kw: Optional[float] = None
    drift_score: float = Field(default=0.0, description="Statistical drift distance from consensus baseline")

    @field_validator("return_temp_c")
    @classmethod
    def validate_thermal_gradient(cls, return_temp, info):
        supply_temp = info.data.get("supply_temp_c")
        if supply_temp is not None and return_temp < supply_temp:
            raise ValueError(f"Thermodynamic violation: return temperature ({return_temp}C) cannot be lower than supply ({supply_temp}C)")
        return return_temp
