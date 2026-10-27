"""
Punto de entrada principal para ejecutar el servidor FastMCP.
Permite iniciar el servidor con:
    python mcp_server.py
"""
import sys
import os
from dotenv import load_dotenv

# Forzar la lectura del archivo .env
load_dotenv()

# Asegurar que el directorio actual esté en el PATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.mcp_server import mcp

if __name__ == "__main__":
    mcp.run()