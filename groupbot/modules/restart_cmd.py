"""ماژول ری‌استارت از داخل گروه"""
import subprocess
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters, ApplicationHandlerStop

RESTART_TRIGGERS = ["ریستارت ربات", "ریستارت"]

async def restart_cmd(update, context):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user or not msg.text:
        return
    if chat.type not in ("group", "supergroup"):
        return
    
    text = msg.text.strip().lower()
    if text not in [t.lower() for t in RESTART_TRIGGERS]:
        return
    
    try:
        from config import OWNER_ID
        from database import is_bot_owner_or_sudo
        if user.id != OWNER_ID and not is_bot_owner_or_sudo(user.id):
            return
    except Exception:
        return
    
    await msg.reply_text("🔄 ربات در حال ری‌استارت...")
    try:
        subprocess.Popen(
            "pkill -9 -f 'main.py' ; sleep 3 ; cd ~/groupbot && source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &",
            shell=True
        )
    except Exception as e:
        print("[RESTART CMD ERR] " + str(e))
    
    raise ApplicationHandlerStop

def register(app):
    app.add_handler(
        MessageHandler(filters.TEXT & filters.ChatType.GROUPS, restart_cmd),
        group=3
    )
    print("OK module restart_cmd loaded")
