from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.refrigerators import RefrigeratorCreate, RefrigeratorResponse
from app.crud import refrigerators as crud_refrigerators

router = APIRouter(
    prefix="/refrigerators",
    tags=["Refrigeradores"]
)

@router.post("/", response_model=RefrigeratorResponse, status_code=status.HTTP_201_CREATED)
def create_refrigerator(refrigerator: RefrigeratorCreate, db: Session = Depends(get_db)):
    return crud_refrigerators.create_refrigerator(db=db, refrigerator=refrigerator)

@router.get("/user/{user_id}", response_model=List[RefrigeratorResponse])
def get_user_refrigerators(user_id: str, db: Session = Depends(get_db)):
    return crud_refrigerators.get_refrigerators_by_user(db=db, user_id=user_id)