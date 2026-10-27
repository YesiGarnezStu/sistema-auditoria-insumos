from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import date, datetime
from typing import Optional

class PurchaseTicketBase(BaseModel):
    store_name: Optional[str] = None
    purchase_date: Optional[date] = None

class PurchaseTicketCreate(PurchaseTicketBase):
    user_id: UUID
    refrigerator_id: Optional[UUID] = None
    ticket_image_url: Optional[str] = None  # URL asignada tras subir el archivo a MinIO
    raw_text_ocr: Optional[str] = None
    processed_by_ai: bool = False

class PurchaseTicketUpdateOCR(BaseModel):
    store_name: Optional[str] = None
    purchase_date: Optional[date] = None
    raw_text_ocr: Optional[str] = None
    processed_by_ai: bool = True

class PurchaseTicketResponse(PurchaseTicketBase):
    id: UUID
    user_id: UUID
    refrigerator_id: Optional[UUID] = None
    ticket_image_url: Optional[str] = None
    raw_text_ocr: Optional[str] = None
    processed_by_ai: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)