import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Date, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.models.base import Base

class Food(Base):
    __tablename__ = "foods"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    refrigerator_id = Column(String(36), ForeignKey("refrigerators.id"), nullable=False)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=True)
    quantity = Column(Numeric(10, 2), nullable=True)
    unit = Column(String(20), nullable=True)
    purchase_date = Column(Date, nullable=True)
    expiration_date = Column(Date, nullable=True)
    status = Column(String(20), default="fresh")
    created_at = Column(DateTime, default=datetime.utcnow)
    consumed_at = Column(DateTime, nullable=True)

    # Relaciones
    refrigerator = relationship("Refrigerator", back_populates="foods")