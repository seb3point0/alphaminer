import re
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
# from app.controllers.workflow_controller import handle_workflow

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = re.sub(r'\\', '', update.message.text_markdown_v2)
    await update.message.reply_text("Here is your message: " + user_message)

def setup_handlers(application):
    application.add_handler(CommandHandler("start", start_command)) 
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    await update.message.reply_text('Hello! I am your AI assistant. How can I help you?')
