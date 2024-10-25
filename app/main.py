import asyncio
import logging
from fastapi import FastAPI
from app.api.routes import router
from app.core.config import settings
from app.services.telegram_service import TelegramService
from app.services.ai_service import AIService
from app.services.response_handler_service import ResponseHandlerService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

project_name = settings.PROJECT_NAME

app = FastAPI(title=project_name, debug=settings.DEBUG)
app.include_router(router)

# Global variables to store our services and tasks
ai_task = None
response_handler = None

@app.on_event("startup")
async def startup_event():
    global ai_task, response_handler
    logger.info(f"Starting up {project_name}")

    try:
        input_queue = asyncio.Queue()
        response_queue = asyncio.Queue()
        logger.info("Created input and response queues")

        telegram_service = TelegramService(settings.TELEGRAM_TOKEN, input_queue, response_queue)
        logger.info("Initialized TelegramService")

        ai_service = AIService(input_queue, response_queue)
        logger.info("Initialized AIService")

        response_handler = ResponseHandlerService(response_queue, telegram_service)
        logger.info("Initialized ResponseHandlerService")

        await telegram_service.setup_bot()
        logger.info("Telegram bot setup completed")

        # Start the services
        ai_task = asyncio.create_task(ai_service.process_messages("company_data"))
        await response_handler.start()

        logger.info("All services started")

    except Exception as e:
        logger.error(f"Error during startup: {str(e)}", exc_info=True)
        raise

    logger.info("Startup completed successfully")

@app.on_event("shutdown")
async def shutdown_event():
    global ai_task, response_handler
    logger.info("Initiating shutdown")
    try:
        if ai_task:
            logger.info("Cancelling AI task")
            ai_task.cancel()
        if response_handler:
            logger.info("Stopping response handler")
            await response_handler.stop()
        # Wait for AI task to finish
        if ai_task:
            await asyncio.gather(ai_task, return_exceptions=True)
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")
    logger.info("Shutdown completed")
