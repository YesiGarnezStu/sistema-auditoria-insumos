import argparse
import random
import socketio
import time

sio = socketio.Client()
game_code = ""
bot_name = ""

@sio.event
def connect():
    print(f"🟢 Conexión establecida. Desplegando a {bot_name} en la arena...")
    sio.emit("join", {"code": game_code, "name": bot_name})

@sio.on("game_state")
def on_game_state(data):
    """
    Cerebro del agente: Aquí se procesa la matriz del juego en tiempo real.
    """
    movimientos = ["UP", "DOWN", "LEFT", "RIGHT"]
    
    # 1. Extraer datos del mapa (dependerá de la estructura exacta del profesor)
    tablero = data.get("board", {})
    mi_serpiente = data.get("you", {})
    
    # 2. Lógica de Supervivencia Básica
    # Si el servidor envía la posición de las paredes o el propio cuerpo, 
    # se deben eliminar esas direcciones de la lista 'movimientos_seguros'.
    movimientos_seguros = movimientos.copy()
    
    # 3. Estrategia Ofensiva (Búsqueda de comida)
    # Aquí se implementaría un algoritmo (como Distancia Manhattan) para elegir 
    # la dirección que acerque la cabeza de tu serpiente a las coordenadas de la comida.
    
    if movimientos_seguros:
        ataque_decidido = random.choice(movimientos_seguros)
    else:
        ataque_decidido = "UP" # Fallback de emergencia
        
    sio.emit("move", {"move": ataque_decidido})
    print(f"⚔️ {bot_name} avanza hacia: {ataque_decidido}")

@sio.event
def disconnect():
    print("🔴 Conexión perdida con la arena.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agente de Combate - Snake Royal")
    parser.add_argument("--url", required=True, help="URL de la arena")
    parser.add_argument("--code", required=True, help="Código de acceso")
    parser.add_argument("--name", required=True, help="Nombre de batalla")
    args = parser.parse_args()

    game_code = args.code
    bot_name = args.name

    try:
        sio.connect(args.url)
        sio.wait()
    except Exception as e:
        print(f"💀 Error de conexión: {e}")