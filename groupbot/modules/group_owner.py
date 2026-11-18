from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes
from database import set_group_owner, remove_group_owner, get_group_owner, is_group_owner, is_bot_admin
from config import OWNER_ID

NL = chr(10)


def display_user(first_name, username):
    name = first_name or "کاربر"
    if username:
        return name + " (@" + username + ")"
    return name


async def is_bot_owner_or_admin(user_id):
    try:
        if user_id == OWNER_ID:
            return True
        if is_bot_admin(user_id):
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

    # تنظیم مالک گروه (فقط مالک ربات / ادمین ربات)
    if text == "مالک":
        if not await is_bot_owner_or_admin(user.id):
            return
        if msg.reply_to_message and msg.reply_to_message.from_user:
            target = msg.reply_to_message.from_user
            if target.id == context.bot.id:
                return
            if target.id == OWNER_ID:
                await msg.reply_text("مالک ربات از قبل همه دسترسی ها رو داره.")
                return
            ok = set_group_owner(chat.id, target.id, target.first_name or "", target.username or "", user.id)
            if ok:
                display = display_user(target.first_name or "", target.username or "")
                await msg.reply_text("✅ " + display + " به عنوان مالک گروه تعیین شد.")
                print("[GROUP OWNER SET] " + str(target.id))
            else:
                await msg.reply_text("❌ خطا")
            return
        # بدون ریپلای → نمایش مالک فعلی
        current = get_group_owner(chat.id)
        if not current:
            await msg.reply_text(
                "ℹ️ این گروه هنوز مالکی نداره." + NL + NL +
                "برای تعیین مالک:" + NL +
                "روی پیام کاربر ریپلای کن و بنویس: مالک"
            )
            return
        display = display_user(current[1], current[2])
        await msg.reply_text(
            "👑 مالک گروه:" + NL +
            "━━━━━━━━━━━━━━━━━━" + NL +
            "نام: " + display + NL +
            "🆔 آیدی: " + str(current[0]) + NL +
            "🕐 تعیین شده در: " + str(current[4])
        )
        return

    # حذف مالک گروه (فقط مالک ربات / ادمین ربات)
    if text == "حذف مالک":
        if not await is_bot_owner_or_admin(user.id):
            return
        current = get_group_owner(chat.id)
        if not current:
            await msg.reply_text("ℹ️ این گروه مالکی نداره.")
            return
        ok = remove_group_owner(chat.id)
        if ok:
            display = display_user(current[1], current[2])
            await msg.reply_text("✅ " + display + " از مالکیت گروه حذف شد.")
        return


def register(app):
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler, block=False), group=80)
