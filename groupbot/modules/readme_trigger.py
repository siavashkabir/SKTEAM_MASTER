"""ارسال README به پیوی سازنده"""
import os
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler, ApplicationHandlerStop
from config import OWNER_ID


async def readme_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user

    if user.id != OWNER_ID:
        await query.answer("⛔ فقط سازنده!", show_alert=True)
        return

    try:
        await query.answer("در حال ارسال راهنما...")
    except Exception:
        pass

    readme_path = os.path.expanduser("~/groupbot/README.md")

    if not os.path.exists(readme_path):
        try:
            await query.edit_message_text("خطا: فایل README.md پیدا نشد!")
        except Exception:
            pass
        return

    try:
        with open(readme_path, "rb") as f:
            await context.bot.send_document(
                chat_id=OWNER_ID,
                document=f,
                filename="Skteam_Bot_README.md",
                caption="راهنمای کامل ربات اسکای‌تیم\n\nهمه چیز در مورد دستورات، پنل‌ها و تنظیمات."
            )
        print(f"[README] Sent to owner {OWNER_ID}")
    except Exception as e:
        print("[README ERR]", str(e))
        try:
            await context.bot.send_message(
                chat_id=OWNER_ID,
                text=f"خطا در ارسال راهنما:\n{str(e)[:200]}"
            )
        except Exception:
            pass

    raise ApplicationHandlerStop


def register(app):
    app.add_handler(
        CallbackQueryHandler(readme_cb, pattern=r"^owner_readme:"),
        group=-41
    )
    print("OK module readme_trigger loaded")
