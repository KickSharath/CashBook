from .schema import (MessageServicesRequest, MessageServicesResponse, ServicesTypeEnum)
from core.config import settings
from telegram import Bot
    
async def MessageServices(servicesType: str, request: MessageServicesRequest) -> MessageServicesResponse:
    try:
        if(servicesType == ServicesTypeEnum.TELEGRAM):
            try:
                bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

                try:
                    await bot.send_message(
                        chat_id=settings.TELEGRAM_GROUP_CHAT_ID,
                        text=request.message,
                        parse_mode="HTML"
                    )
                    status_code = 200
                    message="Message sent to Telegram successfully."
                except Exception as e:
                    status_code = 500
                    message=f"Failed to send Telegram message: {str(e)}"
            except Exception as e:
                status_code = 500
                message=f"Failed to initialize Telegram Bot: {str(e)}"

        else:
            status_code = 400
            supported_services = ', '.join([service.value for service in ServicesTypeEnum])
            message=f"This service {servicesType} is not supported yet. Supported services: {supported_services}"
        return MessageServicesResponse(status_code=status_code, message=message)
    except Exception as e:
        status_code = 500
        return MessageServicesResponse(status_code=status_code, message=f"Failed to share message: {str(e)}")
