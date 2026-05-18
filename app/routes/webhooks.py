from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import WebhookEvent
from app.schemas.payload import OrderWebhookPayload
from app.services.processor import process_order_event

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/event", status_code=202)
def receive_webhook(
    payload: OrderWebhookPayload,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    event = WebhookEvent(
        source="order_service",
        payload=payload.model_dump(),
        status="pending",
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    background_tasks.add_task(process_order_event, event.id, payload.model_dump())

    return JSONResponse(
        status_code=202,
        content={"message": "accepted", "event_id": str(event.id)},
    )
