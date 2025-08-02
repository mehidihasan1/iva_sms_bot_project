import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from ..services.ivasms_api import IvaSmsApi
from .commands import user_sessions

# Define conversation states
ASKING_EMAIL, ASKING_PASSWORD = range(2)

async def login_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the login conversation."""
    await update.message.reply_text("🔐 **Login Process**\nPlease provide your iVAS account email address.")
    return ASKING_EMAIL

async def receive_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the email and prompts for the password."""
    context.user_data["email"] = update.message.text
    await update.message.reply_text("🔒 Thank you. Now, please enter your password.")
    return ASKING_PASSWORD

async def receive_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the password, attempts to log in, and saves the session."""
    password = update.message.text
    email = context.user_data["email"]
    user_id = update.effective_user.id
    
    await update.message.reply_text("⏳ **Attempting to log you in...**")

    api_service = IvaSmsApi()
    if api_service.login(email, password):
        user_sessions[user_id] = api_service
        await update.message.reply_text(
            "✅ **Login successful!** You are now ready to use the bot.\n\n"
            "• Use /get_sms to retrieve messages.\n"
            "• Use /get_numbers to get available numbers."
        )
    else:
        await update.message.reply_text("❌ **Login failed.** Please check your credentials.")
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text("👋 Login process canceled. Goodbye!")
    return ConversationHandler.END