from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.foods import Food
from app.schemas.foods import FoodCreate, FoodUpdate

def create_food(db: Session, food: FoodCreate) -> Food:
    """Inserta un nuevo alimento en el refrigerador."""
    db_food = Food(
        refrigerator_id=str(food.refrigerator_id),
        name=food.name,
        category=food.category,
        quantity=food.quantity,
        unit=food.unit,
        purchase_date=food.purchase_date,
        expiration_date=food.expiration_date,
        status=food.status or "fresh",
    )
    db.add(db_food)
    db.commit()
    db.refresh(db_food)
    return db_food

def get_food(db: Session, food_id: str) -> Optional[Food]:
    """Obtiene un alimento por su ID."""
    return db.query(Food).filter(Food.id == str(food_id)).first()

def get_foods_by_refrigerator(db: Session, refrigerator_id: str) -> List[Food]:
    """Lista todos los alimentos almacenados en un refrigerador específico."""
    return db.query(Food).filter(Food.refrigerator_id == str(refrigerator_id)).all()
