import os

from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.database.db import engine, Base, get_db
from app.database import models  # noqa: F401 – registers models with Base
from app.database.models import WebhookEvent
from app.routes.webhooks import router as webhooks_router

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)
app.include_router(webhooks_router)

templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "templates")
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.APP_NAME}


@app.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    events = (
        db.query(WebhookEvent)
        .options(joinedload(WebhookEvent.api_requests))
        .order_by(WebhookEvent.created_at.desc())
        .limit(50)
        .all()
    )
    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "events": events}
    )
