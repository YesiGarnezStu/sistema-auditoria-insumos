from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import date, datetime
from typing import Optional
from decimal import Decimal

class FoodBase(BaseModel):
    name: str
    category: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit: Optional[str] = None
    purchase_date: Optional[date] = None
    expiration_date: Optional[date] = None
    status: Optional[str] = "fresh"  # Enum o string según negocio

class FoodCreate(FoodBase):
    refrigerator_id: UUID

class FoodUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit: Optional[str] = None
    expiration_date: Optional[date] = None
    status: Optional[str] = None

class FoodResponse(FoodBase):
    id: UUID
    refrigerator_id: UUID
    created_at: datetime
    consumed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)