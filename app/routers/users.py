from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.users import UserCreate, UserResponse
from app.crud import users as crud_users

# Configuramos el enrutador con un prefijo para que todas las URLs empiecen con /users
router = APIRouter(
    prefix="/users",
    tags=["Usuarios"]
)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # 1. Verificamos si el correo ya está registrado usando nuestra función del CRUD
    db_user = crud_users.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado en el sistema")
    
    # 2. Si el correo es nuevo, mandamos a crear el usuario
    return crud_users.create_user(db=db, user=user)

@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: str, db: Session = Depends(get_db)):
    # Endpoint adicional para buscar un usuario por su ID
    db_user = crud_users.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_user