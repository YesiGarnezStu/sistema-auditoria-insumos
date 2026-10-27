import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.models.base import Base

class Refrigerator(Base):
    __tablename__ = "refrigerators"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    brand = Column(String(100), nullable=True)
    esp32_device_id = Column(String(100), nullable=True)
    capacity_liters = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    owner = relationship("User", back_populates="refrigerators")
    foods = relationship("Food", back_populates="refrigerator")