from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.food_images import FoodImage
from app.schemas.food_images import FoodImageCreate

def create_food_image(db: Session, food_image: FoodImageCreate) -> FoodImage:
    """Registra la imagen del alimento o ticket asociada al análisis de IA."""
    db_image = FoodImage(
        food_id=str(food_image.food_id) if food_image.food_id else None,
        ticket_id=str(food_image.ticket_id) if food_image.ticket_id else None,
        image_url=food_image.image_url,
        image_type=food_image.image_type,
        ocr_extracted_text=food_image.ocr_extracted_text,
        ai_analysis=food_image.ai_analysis,
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

def get_images_by_ticket(db: Session, ticket_id: str) -> List[FoodImage]:
    """Obtiene las imágenes asociadas a un ticket específico."""
    return db.query(FoodImage).filter(FoodImage.ticket_id == str(ticket_id)).all()
