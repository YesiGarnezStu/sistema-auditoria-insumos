import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import Base

class FoodImage(Base):
    __tablename__ = "food_images"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    food_id = Column(String(36), ForeignKey("foods.id"), nullable=True)
    ticket_id = Column(String(36), ForeignKey("purchase_tickets.id"), nullable=True)
    image_url = Column(String(255), nullable=False)
    image_type = Column(String(50), nullable=True, default="ticket")
    ocr_extracted_text = Column(Text, nullable=True)
    ai_analysis = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones opcionales
    food = relationship("Food", backref="images")
    ticket = relationship("PurchaseTicket", backref="images")
