from fastapi import FastAPI, Depends
from typing import List
import datetime, os
from sqlmodel import create_engine,Session
from db import Infrastructure,InfrastructureBase,SensorData,SensorDataBase
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
DATABASE_URL = os.getenv("DATABASE_URL")

# Dependency to get database session
def get_session():
    engine = create_engine(DATABASE_URL)
    with Session(engine) as session:
        yield session

# API endpoints
@app.post("/infrastructure/", response_model=Infrastructure)
def create_infrastructure(
    infrastructure: InfrastructureBase,
    session: Session = Depends(get_session)
):
    db_infrastructure = Infrastructure.model_validate(infrastructure)
    session.add(db_infrastructure)
    session.commit()
    session.refresh(db_infrastructure)
    return db_infrastructure

@app.post("/sensor-data/", response_model=SensorData)
def create_sensor_data(
    sensor_data: SensorDataBase,
    session: Session = Depends(get_session)
):
    db_sensor_data = SensorData.from_orm(sensor_data)
    session.add(db_sensor_data)
    session.commit()
    session.refresh(db_sensor_data)
    return db_sensor_data

# Example data insertion
example_infrastructure = {
    "device_id": "ROAD_001",
    "device_type": "road",
    "location_lat": 40.7128,
    "location_lon": -74.0060,
    "name": "Main Street Sensor",
    "description": "Primary road sensor for downtown area",
    "mdata": {
        "installation_date": "2025-01-01",
        "manufacturer": "SensorCorp",
        "model": "RS-2000"
    }
}

example_sensor_data = {
    "device_id": "ROAD_001",
    "timestamp": datetime.datetime.utcnow(),
    "temperature": 25.5,
    "operational_status": "active",
    "weather_condition": "clear",
    "sensor_readings": {
        "traffic_flow": 1500,
        "surface_moisture": 15,
        "surface_condition": "dry",
        "average_speed": 65.5
    }
}