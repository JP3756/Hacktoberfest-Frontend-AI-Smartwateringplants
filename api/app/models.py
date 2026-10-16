from sqlalchemy import Column, Integer

from app.database import Base


class SensorDataModel(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    moisture_level = Column(Integer, nullable=False)
    water_level = Column(Integer, nullable=False)


class PumpModeModel(Base):
    __tablename__ = "pump_mode"

    id = Column(Integer, primary_key=True, index=True)
    mode = Column(Integer, nullable=False)