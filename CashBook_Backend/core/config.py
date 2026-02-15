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

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
