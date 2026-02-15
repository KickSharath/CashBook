from pydantic import BaseModel, Field
from enum import Enum

class ServicesTypeEnum(str, Enum):
    TELEGRAM = "Telegram"

class MessageServicesRequest(BaseModel):
    message: str = Field(..., description="Response message indicating the status of the operation")

class MessageServicesResponse(BaseModel):
    status_code: int = Field(200, description="HTTP status code of the response")
    message: str = Field(..., description="Response message indicating the status of the operation")