"""No Photo Cleanup - کیک کاربران بدون عکس پروفایل"""
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


def _is_no_photo_enabled(chat_id):
    """چک می‌کنه این قابلیت برای این گروه فعاله یا نه"""
    return get_chat_raid_setting(chat_id, "nophoto_enabled", "0") == "1"


async def _has_profile_photo(context, user_id):
    """چک می‌کنه کاربر عکس پروفایل داره یا نه"""
    try:
        photos = await context.bot.get_user_profile_photos(user_id, limit=1)
        if photos and photos.total_count > 0:
            return True
    except Exception as e:
        print(f"[NOPHOTO CHK ERR] {user_id}: {e}")
        # اگه نتونستیم چک کنیم، فرض می‌کنیم داره (کیک نکن)
        return True
    return False


async def check_new_member_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """چک عکس پروفایل کاربر جدید"""
    msg = update.effective_message
    chat = update.effective_chat
    if not msg or not chat or chat.type not in ("group", "supergroup"):
        return
    if not msg.new_chat_members:
        return
    if not _is_no_photo_enabled(chat.id):
        return

    our_bot_id = context.bot.id

    for new_member in msg.new_chat_members:
        # ربات‌ها رو چک نکن
        if new_member.is_bot or new_member.id == our_bot_id:
            continue
        # Owner و Sudo و مالک گروه رو چک نکن
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

        # چک عکس
        has_photo = await _has_profile_photo(context, new_member.id)
        if not has_photo:
            # کیک
            try:
                await context.bot.ban_chat_member(chat.id, new_member.id)
                await context.bot.unban_chat_member(chat.id, new_member.id)
                print(f"[NOPHOTO] Kicked {new_member.id} ({new_member.first_name}) from {chat.id}")
                # پیام هشدار
                try:
                    sent = await context.bot.send_message(
                        chat_id=chat.id,
                        text=(
                            f"🚫 *{new_member.first_name}* عکس پروفایل نداشت و از گروه اخراج شد.\n\n"
                            f"⚠️ برای عضویت در گروه، لطفاً عکس پروفایل بذارید."
                        ),
                        parse_mode="Markdown"
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
                print(f"[NOPHOTO KICK ERR] {new_member.id}: {e}")


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


async def clean_nophoto_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /cleannophoto - کیک همه اعضای بدون عکس"""
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user:
        return
    if chat.type not in ("group", "supergroup"):
        return

    if not await _check_access(update):
        await msg.reply_text("⛔ فقط سازنده، سودو یا مالک گروه!")
        raise ApplicationHandlerStop

    sent = await msg.reply_text("🔍 در حال اسکن لیست اعضا برای عکس پروفایل...\n\n(ممکنه چند دقیقه طول بکشه)")

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
            # استثنا: Owner، Sudo، مالک گروه، ادمین‌ها
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
            has_photo = await _has_profile_photo(context, u.id)
            if not has_photo:
                try:
                    await context.bot.ban_chat_member(chat.id, u.id)
                    await context.bot.unban_chat_member(chat.id, u.id)
                    kicked += 1
                    await asyncio.sleep(0.3)
                except Exception as e:
                    print(f"[NOPHOTO CLEAN ERR] {u.id}: {e}")
                    failed += 1

            # هر 50 نفر، آپدیت کن
            if checked % 50 == 0:
                try:
                    await sent.edit_text(
                        f"🔍 در حال اسکن...\n\n"
                        f"👥 چک شده: `{checked}`\n"
                        f"🚫 کیک شده: `{kicked}`"
                    )
                except Exception:
                    pass
    except Exception as e:
        print("[NOPHOTO MAIN ERR]", str(e))
        try:
            await sent.edit_text(f"❌ خطا: {str(e)[:200]}")
        except Exception:
            pass
        raise ApplicationHandlerStop

    # گزارش نهایی
    text = (
        f"✅ *پاکسازی کامل شد*\n\n"
        f"👥 چک شده: `{checked}`\n"
        f"🚫 کیک شده: `{kicked}`\n"
        f"⏭️ نادیده گرفته: `{skipped}` (ادمین/مالک/Owner)\n"
    )
    if failed:
        text += f"⚠️ خطا: `{failed}`\n"

    try:
        await sent.edit_text(text, parse_mode="Markdown")
    except Exception:
        pass

    # حذف بعد از 30 ثانیه
    async def _del():
        await asyncio.sleep(30)
        try:
            await context.bot.delete_message(chat_id=chat.id, message_id=sent.message_id)
        except Exception:
            pass
    asyncio.create_task(_del())

    # پیام به Owner
    if user.id != OWNER_ID:
        try:
            await context.bot.send_message(
                chat_id=OWNER_ID,
                text=f"🧹 پاکسازی بدون عکس در گروه\n\n📍 {chat.title or chat.id}\n🚫 کیک شده: {kicked}\n👤 توسط: {user.first_name}",
            )
        except Exception:
            pass

    raise ApplicationHandlerStop


# ==================== پنل per-chat ====================
def build_nophoto_panel(uid, chat_id):
    enabled = _is_no_photo_enabled(chat_id)
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"📸 کیک بدون عکس: {'✅ فعال' if enabled else '❌ غیرفعال'}", callback_data=f"nphoto_tog:{uid}:{chat_id}")],
        [InlineKeyboardButton("📋 راهنما", callback_data=f"nphoto_help:{uid}:{chat_id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data=f"menu_settings:{uid}:{chat_id}")],
    ])


async def nophoto_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    if action == "nphoto_panel":
        try:
            await query.edit_message_text(
                "📸 *کیک بدون عکس پروفایل*\n\n"
                "اگه فعال باشه، هر کاربر جدیدی که عکس پروفایل نداشته باشه، خودکار کیک می‌شه.\n\n"
                "💡 برای پاکسازی دستی همه اعضا: `/cleannophoto`\n\n"
                "از دکمه‌ها استفاده کن:",
                reply_markup=build_nophoto_panel(uid, chat_id),
                parse_mode="Markdown"
            )
        except Exception as e:
            print("[NPHOTO PANEL ERR]", str(e))
        await query.answer()
        return

    if action == "nphoto_tog":
        cur = _is_no_photo_enabled(chat_id)
        new = "0" if cur else "1"
        set_chat_raid_setting(chat_id, "nophoto_enabled", new)
        try:
            await query.edit_message_reply_markup(reply_markup=build_nophoto_panel(uid, chat_id))
        except Exception:
            pass
        await query.answer("✅ فعال" if new == "1" else "❌ غیرفعال")
        return

    if action == "nphoto_help":
        try:
            await query.edit_message_text(
                "📋 *راهنمای کیک بدون عکس*\n\n"
                "🔹 *فعال‌سازی خودکار*:\n"
                "اگه «کیک بدون عکس» فعال باشه، هر کاربر جدیدی که وارد گروه بشه و عکس پروفایل نداشته باشه، خودکار کیک می‌شه.\n\n"
                "🔹 *پاکسازی دستی*:\n"
                "دستور `/cleannophoto` رو بزن تا همه اعضای فعلی که عکس ندارن کیک بشن.\n\n"
                "⚠️ *نکته مهم*:\n"
                "این عملیات ممکنه برای گروه‌های بزرگ چند دقیقه طول بکشه.\n"
                "اگه تلگرام محدودیت (Flood) بده، ربات صبر می‌کنه.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 بازگشت", callback_data=f"nphoto_panel:{uid}:{chat_id}")]
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
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, check_new_member_photo),
        group=-190
    )
    app.add_handler(CommandHandler("cleannophoto", clean_nophoto_cmd), group=-2)
    app.add_handler(
        CallbackQueryHandler(nophoto_cb, pattern=r"^nphoto_"),
        group=-42
    )
    print("OK module no_photo_cleanup loaded")
