from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters, CallbackQueryHandler
from database import is_group_owner, is_bot_admin
from config import OWNER_ID

NL = chr(10)

TRIGGERS_PROMOTE = ["افزودن مدیر", "افزودن ادمین", "promote"]
TRIGGERS_DEMOTE = ["عزل مدیر", "حذف مدیر", "demote", "عزل ادمین"]


async def is_admin_user(chat, user_id):
    """
    چک دسترسی برای «افزودن مدیر»:
    - سازنده (همیشه)
    - مالک گروه (همیشه)
    - ادمین‌های ربات (بعداً از پنل سازنده تعیین می‌شه - فعلاً غیرفعال)
    """
    try:
        if user_id == OWNER_ID:
            return True
        if is_group_owner(chat.id, user_id):
            return True
        # چک دسترسی ادمین تلگرام (سازنده گروه)
        m = await chat.get_member(user_id)
        if m.status == "creator":
            return True
        # TODO: بعداً دسترسی ادمین‌های ربات از پنل سازنده
        # if is_bot_admin(user_id) and get_bot_admin_perm(user_id, "manage_groups"):
        #     return True
    except Exception:
        pass
    return False


async def find_target(msg, chat):
    """پیدا کردن کاربر هدف از ریپلای یا یوزرنیم"""
    # حالت ۱: ریپلای
    if msg.reply_to_message and msg.reply_to_message.from_user:
        t = msg.reply_to_message.from_user
        return t.id, (t.first_name or "?")
    # حالت ۲: یوزرنیم توی متن
    parts = msg.text.split()
    username = None
    for p in parts:
        if p.startswith("@"):
            username = p.replace("@", "").strip()
            break
    if not username:
        return None, None
    # جستجو در ادمین‌های تلگرام
    try:
        admins = await chat.get_administrators()
        for a in admins:
            if a.user.username and a.user.username.lower() == username.lower():
                return a.user.id, (a.user.first_name or "?")
    except Exception:
        pass
    # جستجو در دیتابیس
    import turso_db as sqlite3
    from config import DATABASE_PATH
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cur = conn.cursor()
        cur.execute("SELECT user_id, first_name FROM members WHERE chat_id=? AND username=?", (chat.id, username))
        row = cur.fetchone()
        conn.close()
        if row:
            return row[0], (row[1] or "?")
    except Exception as e:
        print("[FIND TARGET DB ERR] " + str(e))
    return None, None


async def reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user:
        return
    if chat.type not in ("group", "supergroup"):
        return
    if not msg.text:
        return

    text = msg.text.strip()
    text_low = text.lower()

    # ========== افزودن مدیر ==========
    is_promote = False
    for tr in TRIGGERS_PROMOTE:
        if text == tr or text_low == tr.lower() or text.startswith(tr + " ") or text.startswith(tr + " @"):
            is_promote = True
            break
    if is_promote:
        if not await is_admin_user(chat, user.id):
            return
        target, target_name = await find_target(msg, chat)
        if not target:
            await msg.reply_text("❌ لطفاً روی پیام کاربر مورد نظر ریپلای کنید یا آیدی عددی بفرستید.")
            return
        try:
            from modules.start import PROMOTE_WAIT
        except Exception as e:
            print("[PROMOTE IMPORT ERR] " + str(e))
            await msg.reply_text("❌ خطای داخلی: " + str(e)[:200])
            return
        # ★ خوندن perms از دیتابیس
        _TG2BOT = {
            "can_delete_messages": "purge",
            "can_restrict_members": "ban",
            "can_pin_messages": "pin",
            "can_invite_users": "admin_add",
            "can_manage_video_chats": "vcall",
            "can_change_info": "group_info",
        }
        _loaded = {}
        try:
            from database import get_all_perms
            _saved = get_all_perms(chat.id, target)
            print(f"[PROMOTE LOAD] saved = {_saved}")
            for _tg, _bot in _TG2BOT.items():
                _loaded[_tg] = bool(_saved.get(_bot, _saved.get(_tg, False)))
        except Exception as _e:
            print(f"[PROMOTE LOAD ERR] {_e}")
            _loaded = {k: False for k in _TG2BOT.keys()}

        PROMOTE_WAIT[user.id] = {
            "chat_id": chat.id,
            "target_id": target,
            "target_name": target_name or "?",
            "perms": _loaded
        }
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        perms = PROMOTE_WAIT[user.id]["perms"]
        def _mk(b):
            return "✅" if b else "❌"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(_mk(perms["can_delete_messages"]) + " پاک کردن پیام‌ها", callback_data="pm_toggle_can_delete_messages")],
            [InlineKeyboardButton(_mk(perms["can_restrict_members"]) + " محدود کردن اعضا (بن/سکوت)", callback_data="pm_toggle_can_restrict_members")],
            [InlineKeyboardButton(_mk(perms["can_pin_messages"]) + " پین کردن پیام‌ها", callback_data="pm_toggle_can_pin_messages")],
            [InlineKeyboardButton(_mk(perms["can_invite_users"]) + " اضافه کردن اعضا", callback_data="pm_toggle_can_invite_users")],
            [InlineKeyboardButton(_mk(perms["can_manage_video_chats"]) + " مدیریت ویدیو چت", callback_data="pm_toggle_can_manage_video_chats")],
            [InlineKeyboardButton(_mk(perms["can_change_info"]) + " تغییر اطلاعات گروه", callback_data="pm_toggle_can_change_info")],
            [InlineKeyboardButton("✅ تایید و ارتقا", callback_data="pm_confirm")],
            [InlineKeyboardButton("❌ لغو", callback_data="pm_cancel")]
        ])
        await msg.reply_text(
            "🔨 ارتقای ادمین جدید" + NL + "━━━━━━━━━━━━━━" + NL +
            "👤 کاربر: " + (target_name or str(target)) + NL +
            "🆔 آیدی: " + str(target) + NL + NL +
            "دسترسی‌های مورد نظر را انتخاب کنید:",
            reply_markup=kb
        )
        return

    # ========== عزل مدیر ==========
    is_demote = False
    for tr in TRIGGERS_DEMOTE:
        if text == tr or text_low == tr.lower() or text.startswith(tr + " ") or text.startswith(tr + " @"):
            is_demote = True
            break
    if is_demote:
        if not await is_admin_user(chat, user.id):
            return
        target, target_name = await find_target(msg, chat)
        if not target:
            await msg.reply_text("❌ لطفاً روی پیام کاربر مورد نظر ریپلای کنید.")
            return
        try:
            await context.bot.promote_chat_member(
                chat_id=chat.id,
                user_id=target,
                can_delete_messages=False,
                can_restrict_members=False,
                can_pin_messages=False,
                can_invite_users=False,
                can_manage_video_chats=False,
                can_change_info=False,
                can_manage_chat=False,
                can_post_messages=False,
                can_edit_messages=False,
                can_promote_members=False,
                is_anonymous=False
            )
        except Exception as e:
            print("[DEMOTE PROMOTE ERR] " + str(e))
            await msg.reply_text("❌ خطا در عزل: " + str(e)[:200])
            return
        try:
            import turso_db as sqlite3
            from config import DATABASE_PATH
            conn = sqlite3.connect(DATABASE_PATH)
            cur = conn.cursor()
            cur.execute("DELETE FROM group_admins WHERE chat_id=? AND user_id=?", (chat.id, target))
            cur.execute("DELETE FROM admin_permissions WHERE chat_id=? AND user_id=?", (chat.id, target))
            conn.commit()
            conn.close()
        except Exception as e:
            print("[DEMOTE DB ERR] " + str(e))
        await msg.reply_text("✅ " + (target_name or "کاربر") + " از ادمینی عزل شد.")
        return



# ═══ مدیریت اخطار (reset warn) ═══
async def cmd_reset_warn(update, context):
    """دستور: حذف اخطار / رفع اخطار / پاک اخطار"""
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    
    if chat.type not in ("group", "supergroup"):
        return
    
    try:
        m = await chat.get_member(user.id)
        if m.status not in ("creator", "administrator"):
            return
    except Exception:
        return
    
    target = None
    if msg.reply_to_message:
        target = msg.reply_to_message.from_user
    else:
        import re as _re
        parts = (msg.text or "").split()
        for p in parts:
            if p.lstrip("-").isdigit() and len(p) > 5:
                try:
                    target = await context.bot.get_chat(int(p))
                except Exception:
                    pass
                break
    
    if not target:
        await msg.reply_text("❌ روی پیام کاربر reply کن یا آیدی عددی بفرست")
        return
    
    from database import reset_warn, get_warn
    old_count = get_warn(chat.id, target.id) or 0
    reset_warn(chat.id, target.id)
    
    await msg.reply_text(
        f"✅ اخطارهای {target.first_name or target.id} صفر شد\n"
        f"قبلاً: {old_count} اخطار"
    )


async def cmd_check_warn(update, context):
    """دستور: اخطار کاربر / چک اخطار"""
    msg = update.effective_message
    chat = update.effective_chat
    
    if chat.type not in ("group", "supergroup"):
        return
    
    target = None
    if msg.reply_to_message:
        target = msg.reply_to_message.from_user
    
    if not target:
        await msg.reply_text("❌ روی پیام کاربر reply کن")
        return
    
    from database import get_warn, get_setting
    count = get_warn(chat.id, target.id) or 0
    limit = get_setting(chat.id, "warn_limit", "3")
    
    await msg.reply_text(
        f"⚠️ {target.first_name or target.id}: {count}/{limit} اخطار"
    )


def register(app):
    from telegram.ext import MessageHandler, filters as _f
    app.add_handler(
        MessageHandler(_f.TEXT & (_f.ChatType.GROUP | _f.ChatType.SUPERGROUP)
            & _f.Regex(r"^(حذف اخطار|رفع اخطار|پاک اخطار|reset warn|/unwarn)$"),
            cmd_reset_warn),
        group=-7
    )
    app.add_handler(
        MessageHandler(_f.TEXT & (_f.ChatType.GROUP | _f.ChatType.SUPERGROUP)
            & _f.Regex(r"^(اخطار کاربر|چک اخطار|/checkwarn)$"),
            cmd_check_warn),
        group=-7
    )
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_handler, block=False), group=-5)
