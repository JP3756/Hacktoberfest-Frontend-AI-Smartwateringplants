from pydantic import BaseModel


class SensorDataRequest(BaseModel):
    sensor: int
    moisture_level: int
    water_level: int


class PumpModeRequest(BaseModel):
    pump: int
    pump_mode: int
