import logging
import re
import asyncio
import json
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self, token: str, input_queue: asyncio.Queue, response_queue: asyncio.Queue):
        self.token = token
        self.application = None
        self.input_queue = input_queue
        self.response_queue = response_queue

    async def setup_bot(self):
        logger.info('Starting Telegram Service')
        try:
            self.application = Application.builder().token(self.token).build()
            self._setup_handlers()
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            logger.info('Telegram bot setup completed successfully')
        except Exception as e:
            logger.error(f'Error setting up Telegram bot: {str(e)}')
            raise

    async def send_response(self, chat_id: int, response: str):
        try:
            logger.info(f"Attempting to send response to chat {chat_id}")
            # Handle JSON responses differently if needed
            if response.startswith('{'):
                # Maybe format JSON responses in a more readable way
                formatted_response = json.loads(response)
                response = json.dumps(formatted_response, indent=2, ensure_ascii=False)
            await self.application.bot.send_message(chat_id=chat_id, text=response)
            logger.info(f"Response sent successfully to chat {chat_id}")
        except Exception as e:
            logger.error(f"Failed to send message to chat {chat_id}: {str(e)}")

    def _setup_handlers(self):
        logger.info('Setting up handlers for Telegram Service')
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        logger.info('Handlers setup completed')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        user_message = update.message.text
        logger.info(f'User message received from chat {chat_id}: {user_message}')
        try:
            await update.message.reply_text("Message received, processing...")
            cleaned_message = re.sub(r'\\', '', update.message.text_markdown_v2)
            logger.info(f'Putting message from chat {chat_id} into input queue')
            await self.input_queue.put((chat_id, cleaned_message))
            logger.info(f'Message from chat {chat_id} added to input queue successfully')
        except Exception as e:
            logger.error(f'Error handling message from chat {chat_id}: {str(e)}')
            await update.message.reply_text("Sorry, an error occurred while processing your message.")
