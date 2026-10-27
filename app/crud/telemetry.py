from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.refrigerators import Refrigerator
from app.models.sensor_readings import SensorReading
from app.schemas.sensor_readings import ESP32TelemetryPayload, SensorReadingCreate

def get_refrigerator_by_esp32_id(db: Session, esp32_device_id: str) -> Optional[Refrigerator]:
    """Busca un refrigerador registrado por el identificador de hardware del ESP32."""
    return db.query(Refrigerator).filter(Refrigerator.esp32_device_id == esp32_device_id).first()

def create_sensor_reading(db: Session, reading: SensorReadingCreate) -> SensorReading:
    """Registra una lectura de sensores para un refrigerador."""
    db_reading = SensorReading(
        refrigerator_id=str(reading.refrigerator_id),
        temperature=reading.temperature,
        humidity=reading.humidity,
        door_open=reading.door_open or False,
    )
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading

def create_esp32_telemetry(db: Session, payload: ESP32TelemetryPayload) -> Optional[SensorReading]:
    """
    Recibe la telemetría enviada por el ESP32, localiza el refrigerador vinculado
    a través de 'esp32_device_id' y almacena la lectura en sensor_readings.
    """
    refrigerator = get_refrigerator_by_esp32_id(db, payload.esp32_device_id)
    if not refrigerator:
        return None

    db_reading = SensorReading(
        refrigerator_id=refrigerator.id,
        temperature=payload.temperature,
        humidity=payload.humidity,
        door_open=payload.door_open or False,
    )
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading

def get_latest_readings_by_refrigerator(
    db: Session,
    refrigerator_id: str,
    limit: int = 50
) -> List[SensorReading]:
    """Obtiene el historial reciente de lecturas de sensores de un refrigerador."""
    return (
        db.query(SensorReading)
        .filter(SensorReading.refrigerator_id == str(refrigerator_id))
        .order_by(SensorReading.created_at.desc())
        .limit(limit)
        .all()
    )
