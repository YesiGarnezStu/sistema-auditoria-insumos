import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    # En MySQL, UUID se maneja típicamente como String(36)
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    password = Column(String(255), nullable=False) # Aquí se guardará el hash, no el texto plano
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    refrigerators = relationship("Refrigerator", back_populates="owner")
    purchase_tickets = relationship("PurchaseTicket", back_populates="user")