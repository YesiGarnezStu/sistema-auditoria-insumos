import requests
import time
import random

# ==========================================
# 1. CREDENCIALES DE LA ARENA (Por definir)
# ==========================================
SERVER_URL = "http://snake.mikecardona076.com/api" # Cambiaremos esto con la ruta del profe
AGENT_TOKEN = "TU_TOKEN_SECRETO" # El ID de tu serpiente

# ==========================================
# 2. CEREBRO DEL AGENTE (Estrategia)
# ==========================================
def calcular_movimiento(tablero):
    """
    Aquí programaremos la inteligencia de tu agente.
    Recibirá el 'tablero' (con tu posición, la comida y los enemigos).
    """
    movimientos_posibles = ["UP", "DOWN", "LEFT", "RIGHT"]
    
    # Por ahora, elige un movimiento al azar para sobrevivir el primer turno
    # Más adelante le pondremos lógica para esquivar paredes y cazar comida.
    movimiento_elegido = random.choice(movimientos_posibles)
    
    return movimiento_elegido

# ==========================================
# 3. CICLO DE COMBATE (El bucle infinito)
# ==========================================
def entrar_a_la_arena():
    print("🐍 Agente conectándose a Snake Royal...")
    
    while True:
        try:
            # A) Pedirle al servidor cómo se ve el mapa en este instante
            # respuesta = requests.get(f"{SERVER_URL}/estado", headers={"Authorization": AGENT_TOKEN})
            # tablero = respuesta.json()
            tablero = {} # Simulador temporal
            
            # B) Pensar el siguiente movimiento
            siguiente_paso = calcular_movimiento(tablero)
            
            # C) Mandar el ataque/movimiento al servidor
            payload = {"move": siguiente_paso}
            # requests.post(f"{SERVER_URL}/mover", json=payload, headers={"Authorization": AGENT_TOKEN})
            
            print(f"⚔️ Movimiento enviado: {siguiente_paso}")
            
            # D) Esperar el tiempo exacto del turno (el profe dirá si son 0.1s, 0.5s, etc.)
            time.sleep(0.5) 
            
        except Exception as error:
            print(f"💀 Caímos en combate. Error: {error}")
            time.sleep(2) # Esperar antes de reconectar

if __name__ == "__main__":
    entrar_a_la_arena()