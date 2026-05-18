import asyncio
from uuid import UUID

from sqlalchemy.orm import Session

from app.database.db import SessionLocal
from app.database.models import WebhookEvent, APIRequestLog
from app.services.integrations import send_to_slack


def process_order_event(event_id: UUID, payload: dict):
    formatted_data = (
        f"📦 New Order Received!\n"
        f"• Order ID: {payload.get('order_id')}\n"
        f"• Customer: {payload.get('customer_email')}\n"
        f"• Total: ${payload.get('total_amount', 0):.2f}\n"
        f"• Items: {len(payload.get('items', []))} item(s)"
    )

    status_code, response_body = asyncio.run(_send(formatted_data))
    success = 200 <= status_code < 300

    db: Session = SessionLocal()
    try:
        log = APIRequestLog(
            webhook_event_id=event_id,
            target_service="slack",
            request_body={"text": formatted_data},
            response_status_code=status_code,
            response_body=response_body,
            success=success,
        )
        db.add(log)

        event = db.query(WebhookEvent).filter(WebhookEvent.id == event_id).first()
        if event:
            event.status = "success" if success else "failed"

        db.commit()
    finally:
        db.close()


async def _send(formatted_data: str) -> tuple[int, dict]:
    return await send_to_slack(formatted_data)
