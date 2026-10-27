import os
from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

# Variables de base de datos
user = os.getenv('DB_USER', 'root')
password = os.getenv('DB_PASSWORD', '')
host = os.getenv('DB_HOST', 'localhost')
port = os.getenv('DB_PORT', '3306')
db_name = os.getenv('DB_NAME', 'denise_iot_db')
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Esta es la variable que Alembic y la Base de Datos buscan:
MYSQL_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"

# Configuración de MinIO ajustada a tu Docker
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "passwordseguro123")
MINIO_SECURE = os.getenv("MINIO_SECURE", "False").lower() in ("true", "1", "t")
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "tickets")