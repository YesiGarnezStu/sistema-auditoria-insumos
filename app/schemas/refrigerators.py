from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class RefrigeratorBase(BaseModel):
    name: str
    brand: Optional[str] = None
    esp32_device_id: Optional[str] = None
    capacity_liters: Optional[int] = None
    is_active: bool = True

class RefrigeratorCreate(RefrigeratorBase):
    user_id: UUID

class RefrigeratorUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    esp32_device_id: Optional[str] = None
    capacity_liters: Optional[int] = None
    is_active: Optional[bool] = None

class RefrigeratorResponse(RefrigeratorBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)