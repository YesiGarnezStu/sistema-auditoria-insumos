from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.users import User
from app.schemas.users import UserCreate

# 1. Configuración del motor de encriptación (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Convierte la contraseña en texto plano a un hash indescifrable"""
    return pwd_context.hash(password)

def get_user_by_email(db: Session, email: str):
    """Busca un usuario por su correo (vital para evitar correos duplicados)"""
    return db.query(User).filter(User.email == email).first()

def get_user(db: Session, user_id: str):
    """Busca un usuario por su ID (UUID)"""
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user: UserCreate):
    """Crea un nuevo usuario en la base de datos de forma segura"""
    
    # 2. Encriptamos la contraseña que viene del schema UserCreate
    hashed_password = get_password_hash(user.password)
    
    # 3. Instanciamos el modelo de SQLAlchemy (la tabla física)
    db_user = User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        password=hashed_password  # ¡Guardamos el hash, NUNCA el texto plano!
    )
    
    # 4. Impactamos los datos en MySQL
    db.add(db_user)
    db.commit()
    
    # 5. Refrescamos para que MySQL nos devuelva el ID (UUID) y las fechas generadas
    db.refresh(db_user) 
    
    return db_user