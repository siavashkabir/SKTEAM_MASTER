import asyncio

"""Trigger پنل سازنده - فقط برای Owner و Sudo"""
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters, ApplicationHandlerStop
from config import OWNER_ID


def _get_delete_delay(chat_id=None):
    """گرفتن زمان حذف پنل از دیتابیس (per-chat)"""
    try:
        from database import get_chat_panel_delete
        if chat_id is not None:
            sec = get_chat_panel_delete(chat_id)
        else:
            sec = 30
        if sec < 0:
            return 0
        if sec > 600:
            return 600
        return sec
    except Exception:
        return 30



async def _delete_later(context, chat_id, message_id, delay):
    """حذف پیام بعد از مدتی مشخص (توسط ربات)"""
    try:
        await asyncio.sleep(delay)
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        print(f"[DELETE LATER ERR] {e}")

async def owner_panel_trigger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اگه Owner/Sudo نوشت 'پنل'، پنل سازنده رو نشون بده و پردازش رو متوقف کن"""
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user or not msg.text:
        return
    if chat.type not in ("group", "supergroup", "private"):
        return

    # فقط پیام دقیق "پنل" یا "panel" (بدون فاصله، بدون کلمه اضافی)
    t = msg.text.strip()
    # [OWNER PANEL GUARD] بستن پنل قدیمی + باز کردن پنل جدید
    try:
        from modules.start import ACTIVE_PANELS as _AP
        _key = (user.id, chat.id)
        _old = _AP.pop(_key, None)
        if _old:
            print(f"[OWNER PANEL GUARD] Deleting old panel msg={_old} for user {user.id}")
            try:
                await context.bot.delete_message(chat_id=chat.id, message_id=_old)
            except Exception as _de:
                print(f"[OWNER PANEL GUARD] Old already deleted: {_de}")
            # فقط در این حالت، پیام "پنل" کاربر هم پاک میشه
    # [FIX-USER-MSG] پیام کاربر پاک نمیشه
    except Exception as _e:
        print("[OWNER PANEL GUARD ERR] " + str(_e))

    if t not in ("پنل", "panel", "Panel", "PANEL"):
        return

    # چک دسترسی
    try:
        from database import is_bot_admin
        if user.id != OWNER_ID and not is_bot_admin(user.id):
            return
    except Exception:
        return

    # نشون دادن پنل سازنده
    try:
        from modules.start import sudo_panel_menu, reset_timer
        sent = await context.bot.send_message(chat_id=msg.chat.id, text=
            "منوی اصلی - بخش مورد نظر:",
            reply_markup=sudo_panel_menu(user.id, chat.id)
        )
        try:
            reset_timer(context, sent.chat_id, sent.message_id)

            # [OWNER PANEL GUARD] ثبت پنل
            try:
                from modules.start import ACTIVE_PANELS as _AP2
                _AP2[(user.id, chat.id)] = sent.message_id
                print(f"[OWNER PANEL GUARD] Registered msg={sent.message_id}")
            except Exception as _e2:
                print("[OWNER PANEL GUARD REG ERR] " + str(_e2))
        except Exception:
            pass

        # ⏱ حذف خودکار پنل و پیام کاربر
        try:
            delay = _get_delete_delay()
            if delay > 0:
                # حذف پنل بعد از N ثانیه
                # [DISABLED] asyncio.create_task(_delete_later(context, sent.chat_id, sent.message_id, delay))
                print(f"[OWNER PANEL] Auto-delete panel in {delay}s")
        except Exception as _e:
            print(f"[OWNER PANEL DELETE ERR] {_e}")

        print(f"[OWNER PANEL] Menu shown for {user.id} in {chat.id}")
    except Exception as e:
        print(f"[OWNER PANEL ERR] {e}")

    # توقف پردازش - هیچ هندلر دیگه‌ای اجرا نشه
    raise ApplicationHandlerStop


def register(app):
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, owner_panel_trigger),
        group=-50
    )
    print("OK module owner_panel_trigger loaded")
