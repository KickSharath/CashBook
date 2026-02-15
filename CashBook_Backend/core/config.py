from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

load_dotenv()

class Settings(BaseSettings):
    # MongoDB configuration
    MONGO_USERNAME: Optional[str] = Field(default=None, alias="MONGO_USERNAME")
    MONGO_PASSWORD: Optional[str] = Field(default=None, alias="MONGO_PASSWORD")
    MONGO_HOST: Optional[str] = Field(default=None, alias="MONGO_HOST")
    MONGO_DB: Optional[str] = Field(default=None, alias="MONGO_DB")

    # Telegram Bot configuration
    TELEGRAM_BOT_TOKEN: Optional[str] = Field(default=None, alias="TELEGRAM_BOT_TOKEN")
    TELEGRAM_GROUP_CHAT_ID: Optional[int] = Field(default=None, alias="TELEGRAM_GROUP_CHAT_ID")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
