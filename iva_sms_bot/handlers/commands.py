import logging
import os
from telegram import Update, InputFile
from telegram.ext import ContextTypes
from ..config import GROUP_CHAT_ID
from ..services.ivasms_api import IvaSmsApi

# Global dictionary to store authenticated API sessions for each user
user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Greets the user and explains the bot's features."""
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"👋 **Hello, {user_name}!** I am your iVAS SMS bot.\n\n"
        "Here's what I can do for you:\n"
        "• Login to your iVAS account securely with `/login`.\n"
        "• Retrieve your recent SMS messages with `/get_sms`.\n"
        "• Get a list of numbers for a specific termination ID with `/get_numbers <id>`.\n",
        parse_mode='Markdown'
    )

async def get_sms(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Retrieves SMS messages and sends them to the configured group."""
    user_id = update.effective_user.id
    
    if user_id not in user_sessions:
        await update.message.reply_text("⚠️ You are not logged in. Please use the /login command first.")
        return

    await update.message.reply_text("⏳ Retrieving your SMS messages...")
    
    iva_sms_api = user_sessions[user_id]
    messages = iva_sms_api.get_sms_messages()
    
    if messages:
        message_parts = ["📩 **New SMS Messages**\n"]
        for msg in messages:
            message_parts.append("---")
            message_parts.append(f"📞 **From:** `{msg['number']}`")
            message_parts.append(f"💬 **Message:** {msg['message']}")
            message_parts.append(f"⏰ **Date:** {msg['date']}")
        
        message_to_send = "\n".join(message_parts)
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=message_to_send, parse_mode='Markdown')
        await update.message.reply_text("✅ The SMS messages have been sent to the group chat.")
    else:
        await update.message.reply_text("ℹ️ No new SMS messages found or failed to retrieve.")
        if not iva_sms_api.session.get('https://www.ivasms.com/portal').url.endswith('/portal'):
            await update.message.reply_text(
                "❌ Your session might have expired. Please try logging in again with /login."
            )
            del user_sessions[user_id]


async def get_numbers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Retrieves numbers for a given termination_id, saves them to a text file,
    and sends the file to the user."""
    user_id = update.effective_user.id
    
    if user_id not in user_sessions:
        await update.message.reply_text("⚠️ You are not logged in. Please use the /login command first.")
        return

    if not context.args:
        await update.message.reply_text("Please provide a termination ID. Example: `/get_numbers 301984`")
        return
        
    termination_id = context.args[0]
    
    await update.message.reply_text(f"⏳ Retrieving numbers for termination ID: `{termination_id}`...")

    file_name = f"numbers_{termination_id}.txt"
    try:
        iva_sms_api = user_sessions[user_id]
        numbers_list = iva_sms_api.get_numbers_list(termination_id)
                
        if numbers_list:
            with open(file_name, 'w') as f:
                for num in numbers_list:
                    f.write(num['number'] + '\n')

            with open(file_name, 'rb') as f:
                await update.message.reply_document(document=InputFile(f))
            
            await update.message.reply_text(f"✅ Numbers for termination ID `{termination_id}` sent as a text file.")
        else:
            await update.message.reply_text(f"⚠️ No numbers found for termination ID `{termination_id}`.")
            if not iva_sms_api.session.get('https://www.ivasms.com/portal').url.endswith('/portal'):
                await update.message.reply_text(
                    "❌ Your session might have expired. Please try logging in again with /login."
                )
                del user_sessions[user_id]
    
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)