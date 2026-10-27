import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.minio_client import get_minio_client, MinioClientWrapper
from app.schemas.purchase_tickets import (
    PurchaseTicketCreate,
    PurchaseTicketResponse,
    PurchaseTicketUpdateOCR,
)
from app.crud import tickets as crud_tickets

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets de Compra"]
)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}

@router.post("/upload", response_model=PurchaseTicketResponse, status_code=status.HTTP_201_CREATED)
async def upload_ticket_image(
    file: UploadFile = File(..., description="Archivo de imagen del ticket de compra"),
    user_id: str = Form(..., description="UUID del usuario propietario"),
    refrigerator_id: Optional[str] = Form(None, description="UUID del refrigerador al que ingresarán los alimentos"),
    store_name: Optional[str] = Form(None, description="Nombre del supermercado o comercio (opcional)"),
    db: Session = Depends(get_db),
    minio_client: MinioClientWrapper = Depends(get_minio_client),
):
    """
    Recibe la imagen de un ticket de compra, la sube a MinIO S3 y genera el registro
    inicial en la tabla 'purchase_tickets' para posterior procesamiento por el Agente de IA.
    """
    # 1. Validación de tipo de archivo
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no permitido: {file.content_type}. Formatos válidos: JPEG, PNG, WEBP."
        )

    # 2. Generación de nombre único para el objeto en MinIO
    extension = file.filename.split(".")[-1] if file.filename and "." in file.filename else "jpg"
    unique_object_name = f"tickets/{uuid.uuid4()}.{extension}"

    try:
        # 3. Subir archivo a MinIO usando el cliente inyectado
        image_url = minio_client.upload_file(
            file_data=file.file,
            object_name=unique_object_name,
            content_type=file.content_type,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir el archivo a MinIO: {str(exc)}"
        )

    # 4. Crear registro en la base de datos
    ticket_data = PurchaseTicketCreate(
        user_id=uuid.UUID(user_id),
        refrigerator_id=uuid.UUID(refrigerator_id) if refrigerator_id else None,
        store_name=store_name,
        ticket_image_url=image_url,
        processed_by_ai=False,
    )

    created_ticket = crud_tickets.create_ticket(db=db, ticket=ticket_data)
    return created_ticket

@router.get("/{ticket_id}", response_model=PurchaseTicketResponse)
def get_ticket_by_id(ticket_id: str, db: Session = Depends(get_db)):
    """Obtiene el detalle de un ticket por su identificador."""
    ticket = crud_tickets.get_ticket(db=db, ticket_id=ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {ticket_id} no encontrado."
        )
    return ticket

@router.get("/user/{user_id}", response_model=List[PurchaseTicketResponse])
def get_user_tickets(user_id: str, db: Session = Depends(get_db)):
    """Lista todos los tickets de compra registrados por un usuario."""
    return crud_tickets.get_tickets_by_user(db=db, user_id=user_id)

@router.patch("/{ticket_id}/ocr", response_model=PurchaseTicketResponse)
def update_ticket_ocr_info(
    ticket_id: str,
    ocr_payload: PurchaseTicketUpdateOCR,
    db: Session = Depends(get_db)
):
    """Actualiza los datos del ticket tras la extracción OCR y procesamiento del agente."""
    updated_ticket = crud_tickets.update_ticket_ocr(
        db=db,
        ticket_id=ticket_id,
        ocr_data=ocr_payload
    )
    if not updated_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {ticket_id} no encontrado."
        )
    return updated_ticket
