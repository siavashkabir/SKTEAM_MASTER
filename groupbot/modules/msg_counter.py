"""
ماژول شمارش پیام‌ها (Message Counter)

این ماژول هر پیام توی گروه رو می‌شماره و توی دیتابیس ذخیره می‌کنه.
همچنین تشخیص می‌ده که پیام شامل «اد» (mention/link) هست یا نه.
"""

from telegram import Update
from telegram.ext import MessageHandler, filters


async def msg_counter(update, context):
    """شمارش هر پیام توی گروه"""
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if not msg or not chat or not user:
        return
    if chat.type not in ("group", "supergroup"):
        return
    if not msg.text and not msg.caption:
        return
    if user.is_bot:
        return

    try:
        from database import increment_msg
        text = (msg.text or msg.caption or "")

        # تشخیص اد
        is_ad = False
        if msg.entities:
            for ent in msg.entities:
                if ent.type in ("mention", "text_mention", "url"):
                    is_ad = True
                    break
        if not is_ad:
            if "@" in text or "t.me/" in text or "telegram.me/" in text:
                is_ad = True

        increment_msg(
            chat.id, user.id,
            user.username or "",
            user.first_name or "",
            is_ad=is_ad
        )
    except Exception as e:
        print("[MSG COUNT ERR] " + str(e))


def register(app):
    """ثبت هندلر شمارش پیام (گروه 20 - آخر از همه)"""
    app.add_handler(
        MessageHandler(
            filters.ChatType.GROUPS & (filters.TEXT | filters.CAPTION) & ~filters.COMMAND,
            msg_counter
        ),
        group=20
    )
    print("OK module msg_counter loaded")
