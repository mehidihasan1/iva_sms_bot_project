import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from .config import BOT_TOKEN
from .handlers.commands import start, get_sms, get_numbers
from .handlers.conversation import login_start, receive_email, receive_password, cancel, ASKING_EMAIL, ASKING_PASSWORD

def main() -> None:
    """Starts the bot."""
    logging.info("Starting bot...")
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    login_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("login", login_start)],
        states={
            ASKING_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_email)],
            ASKING_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_password)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(login_conv_handler)
    application.add_handler(CommandHandler("get_sms", get_sms))
    application.add_handler(CommandHandler("get_numbers", get_numbers))

    logging.info("Bot is running. Press Ctrl+C to stop.")
    application.run_polling()