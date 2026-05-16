from fastapi import FastAPI
from app.config import settings
from app.database.db import engine, Base
from app.database import models  # noqa: F401 – registers models with Base
from app.routes.webhooks import router as webhooks_router

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)
app.include_router(webhooks_router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.APP_NAME}
