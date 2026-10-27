import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# 1. Agregamos el directorio raíz al path para que Python encuentre la carpeta "app"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 2. Importamos nuestra URL de MySQL y la Base con los modelos
from app.config import MYSQL_URL
from app.models import Base

# Objeto de configuración de Alembic
config = context.config

# Configuración de logs
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 3. SOBRESCRIBIMOS LA URL FALSA DE ALEMBIC.INI CON NUESTRA URL REAL
config.set_main_option("sqlalchemy.url", str(MYSQL_URL))

# 4. Asignamos los metadatos de nuestros modelos
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()