"""Auto Global Ban - تشخیص خودکار اسپمرها و بن سراسری"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, MessageHandler, CallbackQueryHandler,
    filters, ApplicationHandlerStop
)
from config import OWNER_ID
from database import (
    record_spam_ban, get_spam_count, get_spam_record,
    get_all_spam_users, remove_spam_record, mark_spam_global,
    add_to_global_blacklist, is_bot_admin, get_setting,
    set_setting, get_all_bot_chats, is_global_blacklisted
)

# آستانه‌ها (پیش‌فرض)
DEFAULT_THRESHOLD = 3


async def check_and_global_ban(user_id, chat_id, reason, banned_by, context):
    """چک می‌کنه کاربر چقدر بن شده و در صورت لزوم global ban می‌کنه"""
    try:
        # ثبت رکورد
        record_spam_ban(user_id, chat_id, reason, banned_by)

        # چک حد نصاب
        threshold = int(get_setting(0, "spam_threshold", str(DEFAULT_THRESHOLD)))
        count = get_spam_count(user_id)

        if count < threshold:
            print(f"[SPAM TRACKER] user {user_id} has {count}/{threshold} bans")
            return False

        # از قبل global هست؟
        if is_global_blacklisted(user_id):
            print(f"[SPAM TRACKER] user {user_id} already global banned")
            return True

        # اضافه به global blacklist
        add_to_global_blacklist(user_id, "", "", OWNER_ID, f"Auto: {count} bans")
        mark_spam_global(user_id)

        # بن از همه گروه‌ها
        banned_in = 0
        try:
            chats = get_all_bot_chats()
            for cid, _ in chats:
                try:
                    await context.bot.ban_chat_member(cid, user_id)
                    banned_in += 1
                except Exception:
                    pass
        except Exception as e:
            print("[AUTO GLOBAL BAN ERR]", str(e))

        # پیام به Owner
        try:
            record = get_spam_record(user_id)
            info = f"🚫 *Global Ban خودکار*\n\n"
            info += f"👤 کاربر: `{user_id}`\n"
            info += f"📊 تعداد بن: `{count}`\n"
            info += f"🎯 بن در: `{banned_in}` گروه\n"
            info += f"\n📋 *تاریخچه:*\n"
            for rec in record[:5]:
                cid, r, by, at, is_g = rec
                info += f"• `{cid}` - {r or 'نامعلوم'} - {at}\n"

            await context.bot.send_message(chat_id=OWNER_ID, text=info, parse_mode="Markdown")
        except Exception as e:
            print("[AUTO GLOBAL BAN NOTIFY ERR]", str(e))

        print(f"[AUTO GLOBAL BAN] user {user_id} global banned (count={count})")
        return True

    except Exception as e:
        print("[AUTO GLOBAL BAN FATAL]", str(e))
        return False


# ============ پنل spam_tracker ============

def build_spam_tracker_menu():
    threshold = int(get_setting(0, "spam_threshold", str(DEFAULT_THRESHOLD)))
    auto = get_setting(0, "auto_global_ban_enabled", "1") == "1"
    auto_label = "✅ فعال" if auto else "❌ غیرفعال"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"📊 لیست اسپمرها", callback_data="spam_list")],
        [InlineKeyboardButton(f"🎯 حد نصاب: {threshold} گروه", callback_data="spam_threshold")],
        [InlineKeyboardButton(f"⚙️ Global Ban خودکار: {auto_label}", callback_data="spam_toggle")],
        [InlineKeyboardButton("🗑 حذف رکورد کاربر", callback_data="spam_remove")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="spam_back_menu")],
    ])


async def spam_tracker_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data

    if user.id != OWNER_ID:
        await query.answer("⛔ فقط سازنده!", show_alert=True)
        return

    # جدا کردن action از پارامترها
    action = data.split(":")[0] if ":" in data else data
    print(f"[SPAM CB] data={data} action={action} user={user.id}")

    if action == "spam_tracker_menu":
        try:
            await query.edit_message_text(
                "🚫 *مدیریت اسپم‌ترکر*\n\nاز دکمه‌ها استفاده کن:",
                reply_markup=build_spam_tracker_menu(),
                parse_mode="Markdown"
            )
        except Exception:
            pass
        await query.answer()
        return

    if action == "spam_list":
        users = get_all_spam_users(min_count=1)
        if not users:
            await query.answer("📋 لیست خالیه.", show_alert=True)
            return
        text = f"📊 *اسپمرهای شناسایی‌شده ({len(users)}):*\n\n"
        for uid, cnt in users[:25]:
            text += f"• `{uid}` → {cnt} بن\n"
        if len(users) > 25:
            text += f"\n... و {len(users) - 25} نفر دیگه"
        kb = [[InlineKeyboardButton("🔙 بازگشت", callback_data="spam_tracker_menu")]]
        try:
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            pass
        await query.answer()
        return

    if action == "spam_threshold":
        current = int(get_setting(0, "spam_threshold", str(DEFAULT_THRESHOLD)))
        options = [2, 3, 4, 5, 7, 10]
        try:
            idx = options.index(current)
            new_val = options[(idx + 1) % len(options)]
        except ValueError:
            new_val = options[1]
        set_setting(0, "spam_threshold", str(new_val))
        try:
            await query.edit_message_reply_markup(reply_markup=build_spam_tracker_menu())
        except Exception:
            pass
        await query.answer(f"✅ حد نصاب: {new_val} گروه")
        return

    if action == "spam_toggle":
        current = get_setting(0, "auto_global_ban_enabled", "1")
        new_val = "0" if current == "1" else "1"
        set_setting(0, "auto_global_ban_enabled", new_val)
        try:
            await query.edit_message_reply_markup(reply_markup=build_spam_tracker_menu())
        except Exception:
            pass
        await query.answer("✅ تغییر کرد")
        return

    if action == "spam_remove":
        context.user_data["spam_waiting"] = True
        kb = [[InlineKeyboardButton("❌ لغو", callback_data="spam_tracker_menu")]]
        try:
            await query.edit_message_text(
                "🗑 آیدی عددی کاربری که می‌خوای رکوردش پاک بشه رو بفرست:",
                reply_markup=InlineKeyboardMarkup(kb)
            )
        except Exception:
            pass
        await query.answer()
        return

    if action == "spam_back_menu":
        # برگشت به پنل سازنده (sudo_panel_menu)
        try:
            from modules.start import sudo_panel_menu
            chat_id = 0
            if query.message.chat.type != "private":
                chat_id = query.message.chat.id
            await query.edit_message_text(
                "منوی اصلی - بخش مورد نظر:",
                reply_markup=sudo_panel_menu(user.id, chat_id)
            )
        except Exception as e:
            print("[SPAM BACK ERR]", str(e))
            await query.answer("❌ خطا در بازگشت", show_alert=True)
            return
        await query.answer()
        return

    await query.answer()


async def spam_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    user = update.effective_user
    if not msg or not user or not msg.text:
        return
    if user.id != OWNER_ID:
        return
    if not context.user_data.get("spam_waiting"):
        return
    try:
        uid = int(msg.text.strip())
    except ValueError:
        await msg.reply_text("❌ آیدی باید عددی باشه.")
        raise ApplicationHandlerStop
    n = remove_spam_record(uid)
    await msg.reply_text(f"✅ {n} رکورد از کاربر `{uid}` پاک شد.", parse_mode="Markdown")
    context.user_data.pop("spam_waiting", None)
    raise ApplicationHandlerStop


def register(app):
    app.add_handler(CallbackQueryHandler(spam_tracker_cb, pattern=r"^spam_"), group=-45)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, spam_text_handler), group=-45)
    print("OK module auto_global_ban loaded")
