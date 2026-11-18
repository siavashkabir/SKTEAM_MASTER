from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from database import save_member
from datetime import datetime


async def save_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ذخیره اطلاعات هر کاربری که توی گروه پیام می‌ده"""
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    
    if not chat or not user:
        return
    
    if chat.type not in ("group", "supergroup"):
        return
    
    if user.is_bot:
        return
    
    try:
        save_member(
            chat.id,
            user.id,
            user.first_name or "",
            user.username or "",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        print("[MEMBER_SAVER] Saved: " + str(user.id) + " | " + (user.first_name or "") + " | @" + (user.username or ""))
    except Exception as e:
        print("[MEMBER_SAVER ERR] " + str(e))


def register(app):
    app.add_handler(
        MessageHandler(filters.ALL, save_user_info, block=False),
        group=-200
    )
