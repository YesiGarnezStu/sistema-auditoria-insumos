from fastapi import FastAPI
from app.routers import users, refrigerators, tickets, foods, telemetry, network_audit

app = FastAPI(
    title="Smart Fridge IoT & AI Network Audit API",
    description="API para gestión de refrigeradores inteligentes, inventario de alimentos, telemetría ESP32 y auditoría de redes con Nmap y FastMCP",
    version="2.0.0"
)

# Registro de enrutadores
app.include_router(users.router)
app.include_router(refrigerators.router)
app.include_router(tickets.router)
app.include_router(foods.router)
app.include_router(telemetry.router)
app.include_router(network_audit.router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Bienvenido a la API del Refrigerador Inteligente Denise IoT. Visita /docs para explorar los endpoints."
    }