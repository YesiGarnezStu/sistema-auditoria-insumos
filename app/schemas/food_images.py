from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class FoodImageBase(BaseModel):
    image_url: str
    image_type: Optional[str] = "ticket"
    ocr_extracted_text: Optional[str] = None
    ai_analysis: Optional[str] = None

class FoodImageCreate(FoodImageBase):
    food_id: Optional[UUID] = None
    ticket_id: Optional[UUID] = None

class FoodImageResponse(FoodImageBase):
    id: UUID
    food_id: Optional[UUID] = None
    ticket_id: Optional[UUID] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
