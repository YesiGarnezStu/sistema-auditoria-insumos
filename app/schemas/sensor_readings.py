from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class SensorReadingBase(BaseModel):
    temperature: Optional[float] = Field(None, description="Temperatura en grados Celsius")
    humidity: Optional[float] = Field(None, description="Humedad relativa en porcentaje")
    door_open: Optional[bool] = Field(False, description="Estado de la puerta del refrigerador")

class SensorReadingCreate(SensorReadingBase):
    refrigerator_id: UUID

class ESP32TelemetryPayload(SensorReadingBase):
    """Payload enviado directamente por el microcontrolador ESP32 vía HTTP POST"""
    esp32_device_id: str = Field(..., description="Identificador único del microcontrolador ESP32 asignado al refrigerador")

class SensorReadingResponse(SensorReadingBase):
    id: UUID
    refrigerator_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
