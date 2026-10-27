from sqlalchemy.orm import Session
from app.models.refrigerators import Refrigerator
from app.schemas.refrigerators import RefrigeratorCreate

def create_refrigerator(db: Session, refrigerator: RefrigeratorCreate):
    """Guarda un nuevo refrigerador asociado a un usuario"""
    # model_dump() convierte el schema Pydantic en un diccionario automáticamente
    db_refrigerator = Refrigerator(**refrigerator.model_dump())
    
    db.add(db_refrigerator)
    db.commit()
    db.refresh(db_refrigerator)
    return db_refrigerator

def get_refrigerators_by_user(db: Session, user_id: str):
    """Devuelve la lista de refrigeradores que le pertenecen a un usuario"""
    return db.query(Refrigerator).filter(Refrigerator.user_id == user_id).all()