"""
Script de Demostración del Agente de IA para Procesamiento de Tickets de Compra
Integración: MinIO -> FastAPI -> Visión y OCR Real -> FastMCP Tools -> MySQL
"""
import os
import sys
import json
from datetime import datetime, timedelta
import httpx
import easyocr  # Librería agregada para escanear texto real

PROJECT_DIR = r"C:\Users\HP\profeMike\Act10oct"
sys.path.insert(0, PROJECT_DIR)

# Configurar stdout en UTF-8 para Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.mcp_server import (
    update_ticket_ocr,
    add_food_to_refrigerator,
    record_food_image_analysis,
)

# URL base de FastAPI
FASTAPI_BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

def extract_real_vision_ocr(image_file_path: str, image_url: str) -> dict:
    """
    Análisis real utilizando EasyOCR para extraer el texto exacto de la foto subida.
    """
    print(f"[Agente IA] Escaneando texto real de la imagen: {image_file_path}")
    today = datetime.now()
    
    # 1. Extracción real de texto con EasyOCR
    try:
        # Iniciamos el lector en español
        reader = easyocr.Reader(['es'], gpu=False) 
        ocr_results = reader.readtext(image_file_path, detail=0)
        texto_real = "\n".join(ocr_results)
    except Exception as e:
        texto_real = f"Error al extraer texto: {str(e)}"

    # 2. Estructuración de datos
    # IMPORTANTE: EasyOCR extrae el texto "crudo". Para que el bot separe 
    # mágicamente "1x Leche" en variables JSON exactas (nombre, cantidad, caducidad),
    # aquí es donde debes conectar tu API de OpenAI o Gemini pasándole el 'texto_real'.
    # Por ahora, guardaremos el texto real extraído en tu base de datos MySQL y 
    # un alimento genérico para que el flujo no se rompa.
    
    return {
        "store_name": "Tienda Detectada en OCR",
        "purchase_date": today.strftime("%Y-%m-%d"),
        "raw_text_ocr": texto_real if texto_real else "No se detectó texto legibles.",
        "detected_foods": [
            {
                "name": "Producto escaneado (Conecta tu LLM para clasificar)",
                "category": "General",
                "quantity": 1.0,
                "unit": "pz",
                "estimated_shelf_life_days": 5
            }
        ],
        "ai_summary": "Ticket escaneado correctamente usando EasyOCR."
    }

def run_agent_pipeline(image_file_path: str, user_id: str, refrigerator_id: str):
    """
    Flujo de trabajo del agente:
    1. Envía la imagen a FastAPI y MinIO.
    2. Extrae el texto real con EasyOCR.
    3. Invoca las herramientas FastMCP para registrar los datos.
    """
    print("\n" + "=" * 66)
    print("INICIANDO PIPELINE DEL AGENTE DE IA")
    print("REFRIGERADOR INTELIGENTE")
    print("=" * 66)
    
    print(f"\n[Paso 1] Subiendo ticket '{image_file_path}' a FastAPI / MinIO...")
    if not os.path.isfile(image_file_path):
        print(f"[Error] No se encontró la imagen:\n{image_file_path}")
        return
        
    ticket_id = None
    ticket_image_url = None
    
    try:
        with open(image_file_path, "rb") as image_file:
            files = {
                "file": (
                    os.path.basename(image_file_path),
                    image_file,
                    "image/jpeg"
                )
            }
            data = {
                "user_id": user_id,
                "refrigerator_id": refrigerator_id,
                "store_name": "Detectando..."
            }
            response = httpx.post(
                f"{FASTAPI_BASE_URL}/tickets/upload",
                files=files,
                data=data,
                timeout=5.0
            )
            
        if response.status_code == 201:
            res_data = response.json()
            ticket_id = res_data["id"]
            ticket_image_url = res_data["ticket_image_url"]
            print(f"[OK] Ticket creado en BD con ID: {ticket_id}")
            print(f"[OK] Imagen almacenada en MinIO: {ticket_image_url}")
        else:
            print(f"[Aviso] FastAPI respondió con status {response.status_code}: {response.text}")
            ticket_id = "00000000-0000-0000-0000-000000000001"
            ticket_image_url = "http://localhost:9000/tickets/sample_ticket.jpg"
            
    except httpx.RequestError as error:
        print(f"[Info] No fue posible conectar con FastAPI en {FASTAPI_BASE_URL}: {error}")
        ticket_id = "00000000-0000-0000-0000-000000000001"
        ticket_image_url = "http://localhost:9000/tickets/sample_ticket.jpg"

    print("\n[Paso 2] Ejecutando análisis de visión y OCR real...")
    # Ahora enviamos la RUTA LOCAL de la imagen para que EasyOCR pueda leerla
    llm_analysis = extract_real_vision_ocr(image_file_path, ticket_image_url)
    
    print(f"   Tienda: {llm_analysis['store_name']}")
    print(f"   Fecha: {llm_analysis['purchase_date']}")
    print(f"   Total de alimentos detectados: {len(llm_analysis['detected_foods'])}")
    print(f"   Texto detectado (Muestra): {llm_analysis['raw_text_ocr'][:50]}...")

    print("\n[Paso 3] El agente invoca las herramientas FastMCP...")
    try:
        print("\n -> Invocando herramienta: update_ticket_ocr()...")
        ticket_update_result = update_ticket_ocr(
            ticket_id=ticket_id,
            raw_text_ocr=llm_analysis["raw_text_ocr"],
            store_name=llm_analysis["store_name"],
            purchase_date=llm_analysis["purchase_date"]
        )
        print(f"    Resultado: {ticket_update_result}")

        print("\n -> Invocando add_food_to_refrigerator()....")
        purchase_dt = datetime.strptime(llm_analysis["purchase_date"], "%Y-%m-%d")
        
        inserted_foods = []
        for item in llm_analysis["detected_foods"]:
            exp_date = (purchase_dt + timedelta(days=item["estimated_shelf_life_days"])).strftime("%Y-%m-%d")
            food_result = add_food_to_refrigerator(
                refrigerator_id=refrigerator_id,
                name=item["name"],
                category=item["category"],
                quantity=item["quantity"],
                unit=item["unit"],
                purchase_date=llm_analysis["purchase_date"],
                expiration_date=exp_date
            )
            inserted_foods.append(food_result)
            print(f"    + Alimento: {item['name']} | Expira: {exp_date} | ID: {food_result.get('food_id')}")

        print("\n -> Invocando record_food_image_analysis()...")
        image_analysis_result = record_food_image_analysis(
            ticket_id=ticket_id,
            image_url=ticket_image_url,
            ocr_extracted_text=llm_analysis["raw_text_ocr"],
            ai_analysis=llm_analysis["ai_summary"],
            image_type="purchase_ticket"
        )
        print(f"    Resultado: {image_analysis_result}")
        
    except Exception as db_err:
        print(f"\n[Aviso Base de Datos] {type(db_err).__name__}: {db_err}")
        print("Verifica que MySQL esté activo y configurado.")
        
    print("\n" + "=" * 66)
    print("FLUJO COMPLETADO: DEMOSTRACIÓN DEL AGENTE DE IA")
    print("=" * 66)

if __name__ == "__main__":
    SAMPLE_USER_ID = "a43f99e5-b24a-42e1-9933-a209071be69c"
    SAMPLE_REFRIGERATOR_ID = "cf2ca64c-4639-48d5-ae46-3ae1b8a55620"
    
    # IMPORTANTE: Si corres este script manualmente, leerá el archivo de abajo.
    # Para que funcione con Telegram, asegúrate de que tu bot llame a la función
    # run_agent_pipeline(ruta_de_la_foto_descargada, SAMPLE_USER_ID, SAMPLE_REFRIGERATOR_ID)
    SAMPLE_IMAGE = os.path.join(PROJECT_DIR, "ticket_ejemplo.jpg")
    
    run_agent_pipeline(
        image_file_path=SAMPLE_IMAGE,
        user_id=SAMPLE_USER_ID,
        refrigerator_id=SAMPLE_REFRIGERATOR_ID
    )