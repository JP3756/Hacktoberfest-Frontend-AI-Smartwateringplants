from pydantic import BaseModel


class SensorDataRequest(BaseModel):
    moisture_level: int
    water_level: int


class PumpModeRequest(BaseModel):
    pump_mode: int
