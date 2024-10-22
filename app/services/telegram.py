import logging
from telegram.ext import Application
from app.controllers.telegram_controller import setup_handlers

logger = logging.getLogger(__name__)

async def setup_bot(token: str):
    logger.info('Starting Telegram Bot')
    application = Application.builder().token(token).build()
    setup_handlers(application)
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
