"""Vague Name Cleanup - کیک کاربران با اسم مبهم (با ۳ سطح حساسیت)"""
import re
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ApplicationHandlerStop
)
from config import OWNER_ID
from database import (
    get_chat_raid_setting, set_chat_raid_setting,
    is_bot_owner_or_sudo, is_group_owner
)


def _is_vague_enabled(chat_id):
    return get_chat_raid_setting(chat_id, "vague_enabled", "0") == "1"


def _get_sensitivity(chat_id):
    """low / medium / high"""
    return get_chat_raid_setting(chat_id, "vague_sensitivity", "medium")


def _is_vague_name(user, sensitivity="medium"):
    """چک می‌کنه اسم مبهم هست یا نه بر اساس حساسیت"""
    if not user:
        return False
    first = (getattr(user, "first_name", "") or "").strip()
    last = (getattr(user, "last_name", "") or "").strip()
    uname = (getattr(user, "username", "") or "").strip()
    full = (first + " " + last).strip()

    # اگه اسمی نداره ولی یوزرنیم داره، رد کن
    if not full and uname:
        return False

    # اگه کلاً خالی
    if not full:
        return True  # همه سطوح

    # ==================== سطح LOW ====================
    # فقط نقطه، خط تیره، آندرلاین، ستاره و ترکیب‌شون
    low_patterns = [
        r"^\.+$",
        r"^\-+$",
        r"^_+$",
        r"^\*+$",
        r"^[\s\.\-\*_]+$",
    ]
    for pat in low_patterns:
        if re.match(pat, full):
            return True

    if sensitivity == "low":
        return False

    # ==================== سطح MEDIUM ====================
    # + فقط عدد، + ترکیب علامت‌های عجیب
    med_patterns = [
        r"^[\d\s\.\-\*_]+$",       # فقط عدد و علامت
        r"^[\s\.\-\*_~•·°◦]+$",     # ترکیب علامت‌ها
        r"^[^\w\u0600-\u06FF]+$",    # فقط علامت‌ها (غیر حرف/عدد)
    ]
    for pat in med_patterns:
        if re.match(pat, full):
            return True

    if sensitivity == "medium":
        return False

    # ==================== سطح HIGH ====================
    # + کمتر از 2 حرف واقعی، + اسم‌های تک‌حرفی
    cleaned = full.replace(" ", "").replace("\u200c", "")
    real_chars = re.sub(r"[\W_\d]", "", cleaned, flags=re.UNICODE)
    if len(real_chars) < 2:
        if uname:
            return False
        return True

    return False


async def check_new_member_vague(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    if not msg or not chat or chat.type not in ("group", "supergroup"):
        return
    if not msg.new_chat_members:
        return
    if not _is_vague_enabled(chat.id):
        return

    sens = _get_sensitivity(chat.id)
    our_bot_id = context.bot.id

    for new_member in msg.new_chat_members:
        if new_member.is_bot or new_member.id == our_bot_id:
            continue
        if new_member.id == OWNER_ID:
            continue
        try:
            if is_bot_owner_or_sudo(new_member.id):
                continue
        except Exception:
            pass
        try:
            if is_group_owner(chat.id, new_member.id):
                continue
        except Exception:
            pass

        if _is_vague_name(new_member, sens):
            try:
                await context.bot.ban_chat_member(chat.id, new_member.id)
                await context.bot.unban_chat_member(chat.id, new_member.id)
                print(f"[VAGUE] Kicked {new_member.id} (sens={sens}) from {chat.id}")
                try:
                    sent = await context.bot.send_message(
                        chat_id=chat.id,
                        text="🚫 کاربری با اسم مبهم از گروه اخراج شد.\n\n⚠️ برای عضویت، اسم واقعی خودتون رو بذارید."
                    )
                    async def _del():
                        await asyncio.sleep(10)
                        try:
                            await context.bot.delete_message(chat_id=chat.id, message_id=sent.message_id)
                        except Exception:
                            pass
                    asyncio.create_task(_del())
                except Exception:
                    pass
            except Exception as e:
                print(f"[VAGUE KICK ERR] {e}")


async def _check_access(update):
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


async def _do_clean_vague(update, context, sent):
    """منطق پاک‌سازی"""
    chat = update.effective_chat
    sens = _get_sensitivity(chat.id)
    kicked = 0
    checked = 0
    skipped = 0
    failed = 0

    try:
        admins = await chat.get_administrators()
        admin_ids = {a.user.id for a in admins}
    except Exception:
        admin_ids = set()

    try:
        async for member in chat.get_members():
            u = member.user
            if not u or u.is_bot:
                continue
            if u.id == OWNER_ID or u.id in admin_ids:
                skipped += 1
                continue
            try:
                if is_bot_owner_or_sudo(u.id):
                    skipped += 1
                    continue
            except Exception:
                pass
            try:
                if is_group_owner(chat.id, u.id):
                    skipped += 1
                    continue
            except Exception:
                pass

            checked += 1
            if _is_vague_name(u, sens):
                try:
                    await context.bot.ban_chat_member(chat.id, u.id)
                    await context.bot.unban_chat_member(chat.id, u.id)
                    kicked += 1
                    await asyncio.sleep(0.3)
                except Exception as e:
                    print(f"[VAGUE CLEAN ERR] {u.id}: {e}")
                    failed += 1

            if checked % 50 == 0:
                try:
                    await sent.edit_text(
                        f"🔍 در حال اسکن...\n\n👥 `{checked}` چک شده\n🚫 `{kicked}` کیک شده"
                    )
                except Exception:
                    pass
    except Exception as e:
        print("[VAGUE MAIN ERR]", str(e))
        try:
            await sent.edit_text(f"❌ خطا: {str(e)[:200]}")
        except Exception:
            pass
        return

    sens_labels = {"low": "کم", "medium": "متوسط", "high": "زیاد"}
    text = (
        f"✅ *پاکسازی کامل شد*\n\n"
        f"🎚 حساسیت: `{sens_labels.get(sens, sens)}`\n"
        f"👥 چک شده: `{checked}`\n"
        f"🚫 کیک شده: `{kicked}`\n"
        f"⏭️ نادیده: `{skipped}` (ادمین/مالک/Owner)\n"
    )
    if failed:
        text += f"⚠️ خطا: `{failed}`\n"

    try:
        await sent.edit_text(text, parse_mode="Markdown")
    except Exception:
        pass

    async def _del():
        await asyncio.sleep(30)
        try:
            await context.bot.delete_message(chat_id=chat.id, message_id=sent.message_id)
        except Exception:
            pass
    asyncio.create_task(_del())


async def clean_vague_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /cleanvague"""
    msg = update.effective_message
    chat = update.effective_chat
    if not msg or not chat:
        return
    if chat.type not in ("group", "supergroup"):
        return
    if not await _check_access(update):
        await msg.reply_text("⛔ فقط سازنده، سودو یا مالک گروه!")
        raise ApplicationHandlerStop
    sent = await msg.reply_text("🔍 در حال اسکن لیست اعضا برای اسم‌های مبهم...")
    await _do_clean_vague(update, context, sent)
    raise ApplicationHandlerStop


async def clean_vague_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور نوشتاری فارسی"""
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user or not msg.text:
        return
    if chat.type not in ("group", "supergroup"):
        return

    t = msg.text.strip().replace("\u200c", "")
    targets = [
        "پاک‌سازی اسم مبهم", "پاکسازی اسم مبهم",
        "حذف اسم مبهم",
        "پاک‌سازی اسم‌های مبهم", "پاکسازی اسمهای مبهم",
    ]
    if t not in targets:
        return

    if not await _check_access(update):
        await msg.reply_text("⛔ فقط سازنده، سودو یا مالک گروه!")
        raise ApplicationHandlerStop

    sent = await msg.reply_text("🔍 در حال اسکن لیست اعضا برای اسم‌های مبهم...")
    await _do_clean_vague(update, context, sent)
    raise ApplicationHandlerStop


def build_vague_panel(uid, chat_id):
    enabled = _is_vague_enabled(chat_id)
    sens = _get_sensitivity(chat_id)
    sens_labels = {"low": "🟢 کم", "medium": "🟡 متوسط", "high": "🔴 زیاد"}
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"❓ کیک اسم مبهم: {'✅ فعال' if enabled else '❌ غیرفعال'}", callback_data=f"vague_tog:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"🎚 حساسیت: {sens_labels.get(sens, sens)}", callback_data=f"vague_sens:{uid}:{chat_id}")],
        [InlineKeyboardButton("📋 راهنما", callback_data=f"vague_help:{uid}:{chat_id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data=f"menu_settings:{uid}:{chat_id}")],
    ])


async def vague_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data
    parts = data.split(":")
    action = parts[0]

    # استخراج chat_id اول (مهم!)
    uid = user.id
    chat_id = 0
    try:
        if len(parts) > 2 and parts[2].lstrip("-").isdigit():
            chat_id = int(parts[2])
    except Exception:
        pass

    # اگه chat_id صفر بود، از خود پیام بگیر
    if chat_id == 0 and query.message and query.message.chat:
        chat_id = query.message.chat.id

    # دسترسی: Owner، Sudo، مالک گروه
    allowed = False
    try:
        if user.id == OWNER_ID or is_bot_owner_or_sudo(user.id):
            allowed = True
    except Exception:
        pass
    if not allowed:
        try:
            from database import is_group_owner
            if is_group_owner(chat_id, user.id):
                allowed = True
        except Exception:
            pass
    if not allowed:
        try:
            member = await query.message.chat.get_member(user.id)
            if member.status in ("creator", "administrator"):
                allowed = True
        except Exception:
            pass
    if not allowed:
        await query.answer("⛔ فقط سازنده یا مالک گروه!", show_alert=True)
        return

    if action == "vague_panel":
        try:
            await query.edit_message_text(
                "❓ *کیک اسم مبهم*\n\n"
                "اگه فعال باشه، کاربران جدیدی که اسمشون مبهم باشه، کیک می‌شن.\n\n"
                "💡 *پاکسازی دستی*: `/cleanvague` یا بنویس `پاک‌سازی اسم مبهم`\n\n"
                "از دکمه‌ها استفاده کن:",
                reply_markup=build_vague_panel(uid, chat_id),
                parse_mode="Markdown"
            )
        except Exception:
            pass
        await query.answer()
        return

    if action == "vague_tog":
        cur = _is_vague_enabled(chat_id)
        new = "0" if cur else "1"
        set_chat_raid_setting(chat_id, "vague_enabled", new)
        try:
            await query.edit_message_reply_markup(reply_markup=build_vague_panel(uid, chat_id))
        except Exception:
            pass
        await query.answer("✅ فعال" if new == "1" else "❌ غیرفعال")
        return

    if action == "vague_sens":
        opts = ["low", "medium", "high"]
        cur = _get_sensitivity(chat_id)
        try:
            i = opts.index(cur)
            new = opts[(i + 1) % len(opts)]
        except ValueError:
            new = "medium"
        set_chat_raid_setting(chat_id, "vague_sensitivity", new)
        try:
            await query.edit_message_reply_markup(reply_markup=build_vague_panel(uid, chat_id))
        except Exception:
            pass
        labels = {"low": "🟢 کم", "medium": "🟡 متوسط", "high": "🔴 زیاد"}
        await query.answer(f"✅ {labels.get(new, new)}")
        return

    if action == "vague_help":
        try:
            await query.edit_message_text(
                "📋 *راهنمای کیک اسم مبهم*\n\n"
                "🎚 *حساسیت*:\n\n"
                "🟢 *کم*: فقط نقاط و علائم خالص\n"
                "• مثال: `...` ، `---` ، `***`\n\n"
                "🟡 *متوسط* (پیش‌فرض): + عدد خالص، ترکیب‌های عجیب\n"
                "• مثال: `12345` ، `•.¸`\n\n"
                "🔴 *زیاد*: + اسم‌های تک‌حرفی و خیلی کوتاه\n"
                "• مثال: `آ` ، `x`\n\n"
                "⚠️ *توجه*: حساسیت زیاد ممکنه کاربران واقعی رو هم کیک کنه.\n\n"
                "💡 *پاکسازی دستی*:\n"
                "• `/cleanvague`\n"
                "• یا بنویس: `پاک‌سازی اسم مبهم`",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 بازگشت", callback_data=f"vague_panel:{uid}:{chat_id}")]
                ]),
                parse_mode="Markdown"
            )
        except Exception:
            pass
        await query.answer()
        return

    await query.answer()


def register(app):
    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, check_new_member_vague),
        group=-191
    )
    app.add_handler(CommandHandler("cleanvague", clean_vague_cmd), group=-2)
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS,
            clean_vague_text_handler
        ),
        group=-2
    )
    app.add_handler(
        CallbackQueryHandler(vague_cb, pattern=r"^vague_"),
        group=-42
    )
    print("OK module vague_name_cleanup loaded")
