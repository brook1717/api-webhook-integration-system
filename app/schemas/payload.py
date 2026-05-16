from pydantic import BaseModel, EmailStr


class OrderWebhookPayload(BaseModel):
    order_id: str
    customer_email: EmailStr
    total_amount: float
    items: list
