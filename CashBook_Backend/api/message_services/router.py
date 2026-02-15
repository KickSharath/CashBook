from fastapi import APIRouter

from .services import MessageServices
from .schema import (MessageServicesRequest, MessageServicesResponse)

routes = APIRouter()

@routes.post(
    "/send-message/{servicesType}",
    response_model=MessageServicesResponse,
    summary="Share a message on a specified messaging service",
    description="""
    This endpoint allows you to share a message on a specified messaging service.
    Currently, the only supported service is Telegram. 
    The response will indicate that the feature is coming soon, but it serves as a placeholder for future implementation.
    """
)
async def share_on_telegram(
    servicesType: str,
    request: MessageServicesRequest
) -> MessageServicesResponse:
    try:
        response = await MessageServices(servicesType, request)
        return response
    except Exception as e:
        raise Exception(f"Failed to share message: {str(e)}")