"""ماژول /reset - نسخه نهایی"""
import datetime
import asyncio
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ApplicationHandlerStop


async def send_with_retry(coro_func, retries=3, delay=2):
    last_err = None
    for i in range(retries):
        try:
            return await coro_func()
        except Exception as e:
            last_err = e
            print(f"[RESET SEND ERR] try {i+1}: {e}")
            await asyncio.sleep(delay)
    raise last_err


async def do_reset(msg, chat, user, context):
    """منطق مشترک ری‌فرش گروه"""
    log_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[RESET] START Group {chat.id} user {user.id} at {log_time}")

    try:
        cleared = len(context.chat_data)
        context.chat_data.clear()
    except Exception as e:
        cleared = 0
        print(f"[RESET CLEAR ERR] {e}")

    print(f"[RESET] Group {chat.id} cleared {cleared} items")

    confirm_text = (
        f"✅ گروه ری‌فرش شد\n\n"
        f"👤 توسط: {user.first_name}\n"
        f"🧹 کش پاک شد: {cleared} آیتم\n"
        f"🕒 زمان: {log_time}"
    )

    try:
        await send_with_retry(lambda: msg.reply_text(confirm_text), retries=3, delay=2)
        print(f"[RESET] confirmation sent for group {chat.id}")
    except Exception as e:
        print(f"[RESET FINAL ERR] could not send confirmation: {e}")


def _check_access(user):
    """چک می‌کنه کاربر Owner یا Sudo هست یا نه"""
    try:
        from config import OWNER_ID
        from database import is_bot_owner_or_sudo
        return user.id == OWNER_ID or is_bot_owner_or_sudo(user.id)
    except Exception:
        return False


async def reset_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر دستور /reset"""
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if not msg or not chat or not user:
        return
    if chat.type not in ("group", "supergroup"):
        return
    if not _check_access(user):
        return

    await do_reset(msg, chat, user, context)
    raise ApplicationHandlerStop


async def reset_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر کلمه 'ریست' بدون اسلش"""
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if not msg or not chat or not user or not msg.text:
        return
    if chat.type not in ("group", "supergroup"):
        return
    if not _check_access(user):
        return

    text = msg.text.strip()
    if text not in ("ریست", "ريس"):
        return

    await do_reset(msg, chat, user, context)
    raise ApplicationHandlerStop


def register(app):
    # دستور انگلیسی /reset (فقط انگلیسی، چون PTB فارسی رو قبول نمی‌کنه)
    app.add_handler(CommandHandler("reset", reset_cmd), group=-2)
    # کلمه فارسی 'ریست' بدون اسلش
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(r"^(ریست|ريس)$"), reset_text_handler),
        group=-2
    )
    print("OK module reset_cmd loaded")
