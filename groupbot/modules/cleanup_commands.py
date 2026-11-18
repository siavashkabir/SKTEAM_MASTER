"""Cleanup Commands - پاکسازی لیست اعضا"""
import asyncio
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, ApplicationHandlerStop
from config import OWNER_ID
from database import get_all_bot_chats, is_bot_owner_or_sudo, is_group_owner


# پترن‌های تشخیص
TEBCHI_KEYWORDS = ["تبچی", "تبليغ", "تبلیغ", "tebchi", "tabchi", "advertising", "admin_ad"]
SOORCHI_KEYWORDS = ["سورچی", "سورچ", "sorchi", "soorchi", "سورس"]


def _is_deleted(user):
    """اکانت دیلیت شده"""
    if not user:
        return False
    try:
        if getattr(user, "is_deleted", False):
            return True
    except Exception:
        pass
    first = getattr(user, "first_name", "") or ""
    uname = getattr(user, "username", "") or ""
    if not first.strip() and not uname.strip():
        return True
    return False


def _is_tebchi(user):
    """تبچی / تبلیغ‌گر متنی"""
    if not user:
        return False
    first = (getattr(user, "first_name", "") or "").lower()
    uname = (getattr(user, "username", "") or "").lower()
    text = first + " " + uname
    for kw in TEBCHI_KEYWORDS:
        if kw.lower() in text:
            return True
    return False


def _is_soorchi(user):
    """سورچی / تبلیغ‌گر گروه"""
    if not user:
        return False
    first = (getattr(user, "first_name", "") or "").lower()
    uname = (getattr(user, "username", "") or "").lower()
    text = first + " " + uname
    for kw in SOORCHI_KEYWORDS:
        if kw.lower() in text:
            return True
    return False


async def _check_access(update):
    """چک دسترسی"""
    user = update.effective_user
    chat = update.effective_chat
    if not user or not chat:
        return False
    if user.id == OWNER_ID:
        return True
    try:
        if is_bot_owner_or_sudo(user.id):
            return True
    except Exception:
        pass
    try:
        if is_group_owner(chat.id, user.id):
            return True
    except Exception:
        pass
    try:
        member = await chat.get_member(user.id)
        if member.status in ("creator", "administrator"):
            return True
    except Exception:
        pass
    return False


async def _run_cleanup(context, chat, user_id, mode):
    """اجرای پاکسازی
    mode: 'del' | 'tebchi' | 'soorchi' | 'all'
    """
    kicked = {"del": 0, "tebchi": 0, "soorchi": 0}
    failed = 0
    total_checked = 0

    # دریافت لیست اعضا
    try:
        admins = await chat.get_administrators()
        admin_ids = {a.user.id for a in admins}
    except Exception:
        admin_ids = set()

    # iterate از طریق get_chat_members (100 تایی)
    async for member in chat.get_members():
        user = member.user
        if not user or user.is_bot:
            continue
        # استثنا: Owner، Sudo، مالک گروه، ادمین‌ها
        if user.id == OWNER_ID or user.id in admin_ids:
            continue
        try:
            if is_bot_owner_or_sudo(user.id):
                continue
        except Exception:
            pass
        try:
            if is_group_owner(chat.id, user.id):
                continue
        except Exception:
            pass

        total_checked += 1
        target = None

        # اولویت: دیلیت
        if mode in ("del", "all") and _is_deleted(user):
            target = "del"
        elif mode in ("tebchi", "all") and _is_tebchi(user):
            target = "tebchi"
        elif mode in ("soorchi", "all") and _is_soorchi(user):
            target = "soorchi"

        if not target:
            continue

        # کیک
        try:
            await context.bot.ban_chat_member(chat.id, user.id)
            await context.bot.unban_chat_member(chat.id, user.id)
            kicked[target] += 1
            await asyncio.sleep(0.3)  # جلوگیری از فلود
        except Exception as e:
            print(f"[CLEANUP ERR] {user.id}: {e}")
            failed += 1

    return kicked, failed, total_checked


async def cleanup_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستورات پاکسازی"""
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user or not msg.text:
        return
    if chat.type not in ("group", "supergroup"):
        return

    cmd = msg.text.split()[0].lstrip("/").split("@")[0].lower()

    if cmd not in ("cleandel", "cleantebchi", "cleansoorchi", "cleanall"):
        return

    if not await _check_access(update):
        await msg.reply_text("⛔ فقط سازنده، سودو یا مالک گروه!")
        raise ApplicationHandlerStop

    modes = {
        "cleandel": ("del", "اکانت‌های دیلیت شده"),
        "cleantebchi": ("tebchi", "تبچی‌ها (تبلیغ‌گر متنی)"),
        "cleansoorchi": ("soorchi", "سورچی‌ها (تبلیغ‌گر گروه)"),
        "cleanall": ("all", "همه (دیلیت + تبچی + سورچی)"),
    }
    mode, label = modes[cmd]

    sent = await msg.reply_text(f"🔍 در حال اسکن لیست اعضا...\n\n🎯 هدف: {label}")

    try:
        kicked, failed, total = await _run_cleanup(context, chat, user.id, mode)
    except Exception as e:
        print("[CLEANUP MAIN ERR]", str(e))
        try:
            await sent.edit_text(f"❌ خطا: {str(e)[:200]}")
        except Exception:
            pass
        raise ApplicationHandlerStop

    # ساخت گزارش
    text = f"✅ *پاکسازی کامل شد*\n\n"
    text += f"🎯 هدف: {label}\n"
    text += f"👥 اعضا چک شد: `{total}`\n\n"
    if mode in ("del", "all"):
        text += f"🗑 اکانت دیلیت: `{kicked['del']}`\n"
    if mode in ("tebchi", "all"):
        text += f"📢 تبچی: `{kicked['tebchi']}`\n"
    if mode in ("soorchi", "all"):
        text += f"🌐 سورچی: `{kicked['soorchi']}`\n"
    if failed:
        text += f"\n⚠️ خطا: `{failed}` مورد"

    try:
        await sent.edit_text(text, parse_mode="Markdown")
    except Exception:
        pass

    # حذف پیام بعد از 30 ثانیه
    async def _del():
        await asyncio.sleep(30)
        try:
            await context.bot.delete_message(chat_id=chat.id, message_id=sent.message_id)
        except Exception:
            pass
    asyncio.create_task(_del())

    # پیام به Owner (اگه خود Owner نبود)
    if user.id != OWNER_ID:
        try:
            await context.bot.send_message(
                chat_id=OWNER_ID,
                text=f"🧹 پاکسازی در گروه\n\n📍 {chat.title or chat.id}\n🎯 {label}\n👤 توسط: {user.first_name}",
            )
        except Exception:
            pass

    raise ApplicationHandlerStop


def register(app):
    for c in ("cleandel", "cleantebchi", "cleansoorchi", "cleanall"):
        app.add_handler(CommandHandler(c, cleanup_cmd), group=-2)
    print("OK module cleanup_commands loaded")
