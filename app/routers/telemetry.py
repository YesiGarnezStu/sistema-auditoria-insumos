from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.sensor_readings import (
    ESP32TelemetryPayload,
    SensorReadingCreate,
    SensorReadingResponse,
)
from app.crud import telemetry as crud_telemetry

router = APIRouter(
    prefix="/telemetry",
    tags=["Telemetría IoT (ESP32)"]
)

@router.post("/esp32", response_model=SensorReadingResponse, status_code=status.HTTP_201_CREATED)
def receive_esp32_telemetry(
    payload: ESP32TelemetryPayload,
    db: Session = Depends(get_db)
):
    """
    Endpoint diseñado para el microcontrolador ESP32.
    Recibe la telemetría periódica del refrigerador (temperatura, humedad, estado de puerta),
    identifica el refrigerador vinculado mediante 'esp32_device_id' y guarda la lectura
    en la tabla 'sensor_readings'.
    """
    reading = crud_telemetry.create_esp32_telemetry(db=db, payload=payload)
    if not reading:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró ningún refrigerador asociado al 'esp32_device_id': '{payload.esp32_device_id}'. "
                   f"Asegúrese de vincular el dispositivo al registrar el refrigerador."
        )
    return reading

@router.get("/refrigerator/{refrigerator_id}", response_model=List[SensorReadingResponse])
def get_refrigerator_telemetry_history(
    refrigerator_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Devuelve las lecturas de telemetría más recientes de un refrigerador."""
    return crud_telemetry.get_latest_readings_by_refrigerator(
        db=db,
        refrigerator_id=refrigerator_id,
        limit=limit
    )
