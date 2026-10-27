from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import MYSQL_URL

# 1. Creamos el motor de conexión usando la URL de tu config.py
# echo=True hace que la terminal te muestre el código SQL que se ejecuta por detrás
engine = create_engine(MYSQL_URL, echo=True)

# 2. Configuramos la fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Esta es la función get_db que tu enrutador estaba buscando
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()