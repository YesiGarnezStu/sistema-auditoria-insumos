import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base

class PurchaseTicket(Base):
    __tablename__ = "purchase_tickets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    refrigerator_id = Column(String(36), ForeignKey("refrigerators.id"), nullable=True)
    store_name = Column(String(100), nullable=True)
    purchase_date = Column(Date, nullable=True)
    
    # Campo para la URL de MinIO
    ticket_image_url = Column(String(255), nullable=True) 
    raw_text_ocr = Column(String(1000), nullable=True)
    processed_by_ai = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    user = relationship("User", back_populates="purchase_tickets")