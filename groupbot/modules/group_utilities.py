"""Group Utilities - pin, unpin, rules"""
from telegram import Update
from telegram.ext import (
    ContextTypes, CommandHandler, ApplicationHandlerStop
)
from config import OWNER_ID
from database import (
    is_bot_owner_or_sudo, is_group_owner, get_setting, set_setting,
)


async def _check_access(update):
    """چک دسترسی: Owner, Sudo, مالک گروه, ادمین"""
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


# ==================== /pin ====================
async def pin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    if not msg or not chat or chat.type not in ("group", "supergroup"):
        return
    if not await _check_access(update):
        await msg.reply_text("⛔ فقط ادمین‌ها!")
        raise ApplicationHandlerStop
    if not msg.reply_to_message:
        await msg.reply_text("❌ روی یه پیام ریپلای کن و /pin بزن.")
        raise ApplicationHandlerStop
    try:
        await context.bot.pin_chat_message(
            chat_id=chat.id,
            message_id=msg.reply_to_message.message_id,
            disable_notification=False
        )
        try:
            await msg.delete()
        except Exception:
            pass
    except Exception as e:
        try:
            await msg.reply_text("❌ خطا در پین: " + str(e)[:100])
        except Exception:
            pass
    raise ApplicationHandlerStop


# ==================== /unpin ====================
async def unpin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    if not msg or not chat or chat.type not in ("group", "supergroup"):
        return
    if not await _check_access(update):
        await msg.reply_text("⛔ فقط ادمین‌ها!")
        raise ApplicationHandlerStop
    try:
        await context.bot.unpin_chat_message(chat_id=chat.id)
        try:
            await msg.delete()
        except Exception:
            pass
    except Exception as e:
        try:
            await msg.reply_text("❌ خطا: " + str(e)[:100])
        except Exception:
            pass
    raise ApplicationHandlerStop


# ==================== /rules ====================
async def rules_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user:
        return
    if chat.type not in ("group", "supergroup"):
        return

    args = context.args or []

    # اگه متن داد، ذخیره کن
    if args:
        if not await _check_access(update):
            await msg.reply_text("⛔ فقط ادمین‌ها می‌تونن قوانین رو تنظیم کنن!")
            raise ApplicationHandlerStop
        new_rules = " ".join(args)
        if len(new_rules) > 500:
            new_rules = new_rules[:500]
        set_setting(chat.id, "rules", new_rules)
        await msg.reply_text("✅ قوانین گروه ذخیره شد.")
        raise ApplicationHandlerStop

    # اگه متن نداد، نشون بده
    rules = get_setting(chat.id, "rules", "")
    if not rules:
        await msg.reply_text("📋 هنوز قانونی تنظیم نشده.\n\nادمین‌ها می‌تونن با /rules متن بذارن.")
    else:
        await msg.reply_text("📋 *قوانین گروه:*\n\n" + rules, parse_mode="Markdown")
    raise ApplicationHandlerStop

# ==================== دستورات فارسی ====================
async def pin_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پین با دستور فارسی"""
    msg = update.effective_message
    if not msg or not msg.text:
        return
    t = msg.text.strip().replace("\u200c", "").lower()
    if t not in ("پین", "پین کن", "سنجاق", "سنجاق کن"):
        return
    chat = update.effective_chat
    if chat.type not in ("group", "supergroup"):
        return
    if not await _check_access(update):
        await msg.reply_text("⛔ فقط ادمین‌ها!")
        raise ApplicationHandlerStop
    if not msg.reply_to_message:
        await msg.reply_text("❌ روی یه پیام ریپلای کن و بنویس: پین")
        raise ApplicationHandlerStop
    try:
        await context.bot.pin_chat_message(
            chat_id=chat.id,
            message_id=msg.reply_to_message.message_id,
            disable_notification=False
        )
        try:
            await msg.delete()
        except Exception:
            pass
    except Exception as e:
        try:
            await msg.reply_text("❌ خطا: " + str(e)[:100])
        except Exception:
            pass
    raise ApplicationHandlerStop


async def unpin_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """آنپین با دستور فارسی"""
    msg = update.effective_message
    if not msg or not msg.text:
        return
    t = msg.text.strip().replace("\u200c", "").lower()
    if t not in ("آنپین", "انپین", "آنپین کن", "انپین کن", "برداشتن پین", "پین رو بردار"):
        return
    chat = update.effective_chat
    if chat.type not in ("group", "supergroup"):
        return
    if not await _check_access(update):
        await msg.reply_text("⛔ فقط ادمین‌ها!")
        raise ApplicationHandlerStop
    try:
        await context.bot.unpin_chat_message(chat_id=chat.id)
        try:
            await msg.delete()
        except Exception:
            pass
    except Exception as e:
        try:
            await msg.reply_text("❌ خطا: " + str(e)[:100])
        except Exception:
            pass
    raise ApplicationHandlerStop


async def rules_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """قوانین با دستور فارسی"""
    msg = update.effective_message
    if not msg or not msg.text:
        return
    t = msg.text.strip().replace("\u200c", "").lower()
    
    # نمایش قوانین
    if t in ("قوانین", "قانون", "قوانین گروه"):
        chat = update.effective_chat
        if chat.type not in ("group", "supergroup"):
            return
        rules = get_setting(chat.id, "rules", "")
        if not rules:
            await msg.reply_text("📋 هنوز قانونی تنظیم نشده.\n\nادمین‌ها می‌تونن بنویسن: تنظیم قوانین [متن]")
        else:
            try:
                await msg.reply_text("📋 *قوانین گروه:*\n\n" + rules, parse_mode="Markdown")
            except Exception:
                await msg.reply_text("📋 قوانین گروه:\n\n" + rules)
        raise ApplicationHandlerStop
    
    # تنظیم قوانین
    if t.startswith("تنظیم قوانین"):
        chat = update.effective_chat
        if chat.type not in ("group", "supergroup"):
            return
        if not await _check_access(update):
            await msg.reply_text("⛔ فقط ادمین‌ها!")
            raise ApplicationHandlerStop
        # گرفتن متن قوانین
        parts = msg.text.strip().split(maxsplit=2)
        if len(parts) < 3:
            await msg.reply_text("❌ بنویس: تنظیم قوانین [متن قوانین]")
            raise ApplicationHandlerStop
        new_rules = parts[2]
        if len(new_rules) > 500:
            new_rules = new_rules[:500]
        set_setting(chat.id, "rules", new_rules)
        await msg.reply_text("✅ قوانین گروه ذخیره شد.")
        raise ApplicationHandlerStop




def register(app):
    from telegram.ext import MessageHandler, filters
    app.add_handler(CommandHandler("pin", pin_cmd), group=-2)
    app.add_handler(CommandHandler("unpin", unpin_cmd), group=-2)
    app.add_handler(CommandHandler("rules", rules_cmd), group=-2)
    # هندلرهای فارسی
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS,
            pin_text_handler
        ),
        group=-2
    )
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS,
            unpin_text_handler
        ),
        group=-2
    )
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS,
            rules_text_handler
        ),
        group=-2
    )
    print("OK module group_utilities loaded (EN + FA)")