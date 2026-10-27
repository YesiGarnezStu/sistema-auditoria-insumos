from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.foods import FoodCreate, FoodResponse
from app.crud import foods as crud_foods

router = APIRouter(
    prefix="/foods",
    tags=["Alimentos"]
)

@router.post("/", response_model=FoodResponse, status_code=status.HTTP_201_CREATED)
def create_food_item(food: FoodCreate, db: Session = Depends(get_db)):
    """Inserta un nuevo alimento en un refrigerador."""
    return crud_foods.create_food(db=db, food=food)

@router.get("/refrigerator/{refrigerator_id}", response_model=List[FoodResponse])
def get_foods_by_refrigerator(refrigerator_id: str, db: Session = Depends(get_db)):
    """Obtiene la lista de alimentos de un refrigerador."""
    return crud_foods.get_foods_by_refrigerator(db=db, refrigerator_id=refrigerator_id)
