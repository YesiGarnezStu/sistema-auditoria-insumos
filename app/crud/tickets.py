from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.purchase_tickets import PurchaseTicket
from app.schemas.purchase_tickets import PurchaseTicketCreate, PurchaseTicketUpdateOCR

def create_ticket(db: Session, ticket: PurchaseTicketCreate) -> PurchaseTicket:
    """Crea un registro de ticket de compra en la base de datos."""
    db_ticket = PurchaseTicket(
        user_id=str(ticket.user_id),
        refrigerator_id=str(ticket.refrigerator_id) if ticket.refrigerator_id else None,
        store_name=ticket.store_name,
        purchase_date=ticket.purchase_date,
        ticket_image_url=ticket.ticket_image_url,
        raw_text_ocr=ticket.raw_text_ocr,
        processed_by_ai=ticket.processed_by_ai,
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

def get_ticket(db: Session, ticket_id: str) -> Optional[PurchaseTicket]:
    """Obtiene un ticket por su identificador UUID."""
    return db.query(PurchaseTicket).filter(PurchaseTicket.id == str(ticket_id)).first()

def get_tickets_by_user(db: Session, user_id: str) -> List[PurchaseTicket]:
    """Obtiene todos los tickets asociados a un usuario."""
    return db.query(PurchaseTicket).filter(PurchaseTicket.user_id == str(user_id)).all()

def update_ticket_ocr(
    db: Session,
    ticket_id: str,
    ocr_data: PurchaseTicketUpdateOCR
) -> Optional[PurchaseTicket]:
    """Actualiza la información del ticket una vez procesado por el Agente de IA."""
    db_ticket = get_ticket(db, ticket_id)
    if not db_ticket:
        return None

    if ocr_data.store_name is not None:
        db_ticket.store_name = ocr_data.store_name
    if ocr_data.purchase_date is not None:
        db_ticket.purchase_date = ocr_data.purchase_date
    if ocr_data.raw_text_ocr is not None:
        db_ticket.raw_text_ocr = ocr_data.raw_text_ocr

    db_ticket.processed_by_ai = ocr_data.processed_by_ai
    db.commit()
    db.refresh(db_ticket)
    return db_ticket
