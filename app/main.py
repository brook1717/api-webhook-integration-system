from fastapi import FastAPI
from app.config import settings

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.APP_NAME}
