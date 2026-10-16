from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database import Base


class Sensor(Base):
    __tablename__ = "sensor"

    id = Column(Integer, primary_key=True, index=True)

    data_entries = relationship("SensorData", back_populates="sensor")


class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    moisture_level = Column(Integer, nullable=False)
    water_level = Column(Integer, nullable=False)

    sensor_id = Column(Integer, ForeignKey("sensor.id"), nullable=False)

    sensor = relationship("Sensor", back_populates="data_entries")


class Pump(Base):
    __tablename__ = "pump"

    id = Column(Integer, primary_key=True, index=True)

    pump_mode = relationship("PumpMode", back_populates="pump", uselist=False)


class PumpMode(Base):
    __tablename__ = "pump_mode"

    id = Column(Integer, primary_key=True, index=True)
    mode = Column(Integer, nullable=False)

    pump_id = Column(Integer, ForeignKey("pump.id"), nullable=False, unique=True)
    pump = relationship("Pump", back_populates="pump_mode")
