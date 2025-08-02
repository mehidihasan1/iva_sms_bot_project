import os

# --- Bot Configuration ---
# ⚠️ Replace with your actual Telegram Bot Token from @BotFather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8106314263:AAHzUcAit4ejLmIIEMcc-FEhfyNgbrP5u5M")

# ⚠️ Replace with the chat ID of your target group. It must be a negative number.
#    Add the bot to the group, send a message, then get the ID from this URL:
#    https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
GROUP_CHAT_ID = int(os.environ.get("GROUP_CHAT_ID", "-1002819835150"))