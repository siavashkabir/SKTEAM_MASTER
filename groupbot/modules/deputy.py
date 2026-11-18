from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import MessageHandler, filters, ContextTypes, CallbackQueryHandler
from database import (
    add_deputy, remove_deputy, is_deputy, get_all_deputies,
    is_bot_admin, is_group_owner, init_deputy_perms
)
from config import OWNER_ID

NL = chr(10)


def display_user(first_name, username):
    name = first_name or "کاربر"
    if username:
        return name + " (@" + username + ")"
    return name


async def can_manage_deputy(chat, user_id):
    """فقط مالک گروه، مالک ربات، ادمین ربات"""
    try:
        if user_id == OWNER_ID:
            return True
        if is_bot_admin(user_id):
            return True
        if is_group_owner(chat.id, user_id):
            return True
    except Exception:
        pass
    # سازنده واقعی گروه هم می تونه
    try:
        m = await chat.get_member(user_id)
        if m.status == "creator":
            return True
    except Exception:
        pass
    return False


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user:
        return
    if chat.type not in ("group", "supergroup"):
        return

    text = (msg.text or "").strip()
    if not text:
        return

    # تنظیم معاون
    if text == "معاون":
        if not await can_manage_deputy(chat, user.id):
            return
        if msg.reply_to_message and msg.reply_to_message.from_user:
            target = msg.reply_to_message.from_user
            if target.id == context.bot.id:
                return
            if target.id == OWNER_ID:
                await msg.reply_text("مالک ربات نیازی به معاون نداره.")
                return
            if is_deputy(chat.id, target.id):
                await msg.reply_text("ℹ️ " + (target.first_name or "کاربر") + " از قبل معاون هست.")
                return
            ok = add_deputy(chat.id, target.id, target.first_name or "", target.username or "", user.id)
            if ok:
                init_deputy_perms(chat.id)
                display = display_user(target.first_name or "", target.username or "")
                await msg.reply_text(
                    "✅ " + display + " به عنوان معاون گروه تعیین شد." + NL + NL +
                    "برای تنظیم دسترسی هاش:" + NL +
                    "پنل → تنظیمات → دسترسی معاون"
                )
                print("[DEPUTY SET] " + str(target.id))
            else:
                await msg.reply_text("❌ خطا")
            return
        # بدون ریپلای → لیست معاونین
        deps = get_all_deputies(chat.id)
        if not deps:
            await msg.reply_text(
                "ℹ️ این گروه معاون نداره." + NL + NL +
                "برای تعیین معاون:" + NL +
                "روی پیام کاربر ریپلای کن و بنویس: معاون"
            )
            return
        lines = []
        for i, (uid, first_name, username, added_by, added_at) in enumerate(deps, 1):
            display = display_user(first_name, username)
            lines.append(str(i) + ". " + display + NL + "   🆔 " + str(uid))
        await msg.reply_text("📋 معاونین گروه:" + NL + "━━━━━━━━━━━━━━━━━━" + NL + NL + (NL + NL).join(lines))
        return

    # حذف معاون
    if text == "حذف معاون":
        if not await can_manage_deputy(chat, user.id):
            return
        if not msg.reply_to_message or not msg.reply_to_message.from_user:
            await msg.reply_text("روی پیام کاربر ریپلای کن و بنویس: حذف معاون")
            return
        target = msg.reply_to_message.from_user
        if not is_deputy(chat.id, target.id):
            await msg.reply_text("ℹ️ " + (target.first_name or "کاربر") + " معاون نیست.")
            return
        ok = remove_deputy(chat.id, target.id)
        if ok:
            await msg.reply_text("✅ " + (target.first_name or "کاربر") + " از معاونی حذف شد.")
        return


def register(app):
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler, block=False), group=52)
