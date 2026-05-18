from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    APP_NAME: str = "Webhook Integration System"
    DEBUG: bool = False
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/webhooks"
    SECRET_KEY: str = "change-me-in-production"
    SLACK_WEBHOOK_URL: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
