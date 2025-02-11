from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field
from pydantic import field_validator
from sqlalchemy import Column, DateTime, text
from sqlalchemy.dialects.postgresql import JSONB

class InfrastructureBase(SQLModel):
    device_id: str = Field(index=True)
    device_type: str = Field(index=True)  # 'road', 'bridge', 'tunnel', etc.
    location_lat: float
    location_lon: float
    name: str
    description: Optional[str] = None
    mdata: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))  # Correct way

class Infrastructure(InfrastructureBase, table=True):
    __tablename__ = "infrastructure"
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("CURRENT_TIMESTAMP"),
            onupdate=text("CURRENT_TIMESTAMP")
        )
    )
    
class SensorDataBase(SQLModel):
    device_id: str = Field(foreign_key="infrastructure.device_id", index=True)
    timestamp: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), index=True),
        default_factory=datetime.utcnow
    )
    
    # Common metrics
    temperature: Optional[float] = None
    operational_status: Optional[str] = None
    weather_condition: Optional[str] = None
    
    # Device-specific readings stored in JSONB
    sensor_readings: Dict[str, Any] = Field(
        default={},
        sa_column=Column(JSONB)
    )

class SensorData(SensorDataBase, table=True):
    __tablename__ = "sensor_data"
    id: Optional[int] = Field(default=None, primary_key=True)

    @field_validator("sensor_readings", mode="before")
    def validate_sensor_readings(cls, v, values):
        device_type = values.get("device_type")
        if device_type == "road":
            required_fields = {"traffic_flow", "surface_moisture", "surface_condition"}
        elif device_type == "bridge":
            required_fields = {"structural_stress", "vibration", "weight_load"}
        elif device_type == "tunnel":
            required_fields = {"air_quality", "visibility", "ventilation_status"}
        elif device_type == "traffic_signal":
            required_fields = {"signal_status", "queue_length", "wait_time"}
        elif device_type == "streetlight":
            required_fields = {"light_status", "light_intensity", "power_consumption"}
        else:
            return v

        missing_fields = required_fields - set(v.keys())
        if missing_fields:
            raise ValueError(f"Missing required fields for {device_type}: {missing_fields}")
        return v

# FastAPI/SQLModel database initialization and TimescaleDB setup
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy import create_engine as sa_create_engine
from sqlalchemy.schema import CreateTable
import logging

def init_db(database_url: str):
    # Create SQLAlchemy engine
    engine = create_engine(database_url, echo=True)
    
    SQLModel.metadata.drop_all(engine)

    # Create all tables
    SQLModel.metadata.create_all(engine)
    
    # Convert sensor_data table to hypertable
    with engine.connect() as connection:
        try:
            connection.execute(text("""
                SELECT create_hypertable('sensor_data', 'timestamp', 
                    if_not_exists => TRUE,
                    chunk_time_interval => INTERVAL '1 day'
                );
            """))
            
            # Create additional indexes for better query performance
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_sensor_data_device_time 
                ON sensor_data (device_id, timestamp DESC);
            """))
            
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_sensor_readings 
                ON sensor_data USING GIN (sensor_readings);
            """))
            
        except Exception as e:
            logging.error(f"Error setting up TimescaleDB: {e}")
            raise

# Example usage with FastAPI
