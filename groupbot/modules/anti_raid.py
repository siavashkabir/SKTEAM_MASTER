"""Anti-Raid - جلوگیری از حمله اعضای جدید"""
import time
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ContextTypes, MessageHandler, CallbackQueryHandler,
    filters, ApplicationHandlerStop
)
from config import OWNER_ID
from database import (
    get_chat_raid_setting, set_chat_raid_setting,
    log_raid_event, end_raid_event, get_raid_history,
    get_all_bot_chats, get_ai_setting
)

# 🔒 Raid tracker: {chat_id: [timestamps]}
_RAID_TRACKER = {}
# 🔐 حالت قفل: {chat_id: {"until": timestamp, "event_id": id}}
_RAID_LOCK = {}
# 👥 اعضای جدید که بعد از شروع ریید وارد شدن (فقط اینا بلاک می‌شن)
_RAID_NEW_MEMBERS = {}


def _is_raid_enabled(chat_id):
    return get_chat_raid_setting(chat_id, "enabled", "0") == "1"


def _get_threshold(chat_id):
    try:
        return int(get_chat_raid_setting(chat_id, "threshold", "10"))
    except Exception:
        return 10


def _get_window(chat_id):
    try:
        return int(get_chat_raid_setting(chat_id, "window", "60"))
    except Exception:
        return 60


def _get_duration(chat_id):
    try:
        return int(get_chat_raid_setting(chat_id, "duration", "600"))
    except Exception:
        return 600


def _get_action(chat_id):
    return get_chat_raid_setting(chat_id, "action", "lock")


def _get_protect_old(chat_id):
    """محافظت از اعضای قبلی"""
    return get_chat_raid_setting(chat_id, "protect_old", "1") == "1"


def _is_raid_active(chat_id):
    info = _RAID_LOCK.get(chat_id)
    if not info:
        return False
    if time.time() > info["until"]:
        _RAID_LOCK.pop(chat_id, None)
        return False
    return True


async def check_raid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """چک ریید روی اعضای جدید"""
    msg = update.effective_message
    chat = update.effective_chat
    if not msg or not chat or chat.type not in ("group", "supergroup"):
        return
    if not msg.new_chat_members:
        return

    if not _is_raid_enabled(chat.id):
        return

    # اگه ریید فعاله، اعضای جدید رو بن کن
    if _is_raid_active(chat.id):
        for m in msg.new_chat_members:
            if m.is_bot:
                continue
            try:
                await context.bot.ban_chat_member(chat.id, m.id)
                print(f"[RAID] Banned new member {m.id} during raid")
            except Exception:
                pass
        try:
            await msg.delete()
        except Exception:
            pass
        return

    # شمارش اعضای جدید
    now = time.time()
    window = _get_window(chat.id)
    threshold = _get_threshold(chat.id)

    _RAID_TRACKER.setdefault(chat.id, [])
    # اضافه کردن اعضای جدید
    for _ in msg.new_chat_members:
        _RAID_TRACKER[chat.id].append(now)

    # حذف قدیمی‌ها
    cutoff = now - window
    _RAID_TRACKER[chat.id] = [t for t in _RAID_TRACKER[chat.id] if t > cutoff]

    count = len(_RAID_TRACKER[chat.id])

    if count >= threshold:
        # 🚨 ریید تشخیص داده شد!
        await _trigger_raid(context, chat, count, msg)


async def _trigger_raid(context, chat, count, msg):
    """فعال کردن حالت ریید"""
    action = _get_action(chat.id)
    duration = _get_duration(chat.id)

    # ثبت در دیتابیس
    event_id = log_raid_event(chat.id, action, count)

    print(f"[RAID ALERT] Chat {chat.id} - {count} new members - action={action}")

    # اعمال اکشن
    if action in ("lock", "lock_ban"):
        _RAID_LOCK[chat.id] = {
            "until": time.time() + duration,
            "event_id": event_id
        }

    # 👥 ثبت اعضای جدید که بعد از این وارد می‌شن (فقط اینا بلاک می‌شن)
    _RAID_NEW_MEMBERS.setdefault(chat.id, set())
    if msg and msg.new_chat_members:
        for m in msg.new_chat_members:
            if not m.is_bot:
                _RAID_NEW_MEMBERS[chat.id].add(m.id)

    if action in ("lock_ban",):
        # بن کردن اعضای جدید فعلی
        if msg and msg.new_chat_members:
            for m in msg.new_chat_members:
                if m.is_bot:
                    continue
                try:
                    await context.bot.ban_chat_member(chat.id, m.id)
                except Exception:
                    pass

    # پیام هشدار به گروه
    action_labels = {
        "lock": "🔒 قفل گروه",
        "lock_ban": "🔒 قفل + بن کردن اعضا",
        "notify": "📢 فقط هشدار به ادمین‌ها",
    }
    action_txt = action_labels.get(action, "🔒")

    try:
        await context.bot.send_message(
            chat_id=chat.id,
            text=(
                "🚨 *هشدار ریید!*\n\n"
                f"👥 تعداد اعضای جدید: `{count}`\n"
                f"⚙️ اکشن: {action_txt}\n"
                f"⏱ مدت زمان: `{duration // 60}` دقیقه\n\n"
                "🛡 ربات گروه رو در حالت امن قرار داد."
            ),
            parse_mode="Markdown"
        )
    except Exception:
        pass

    # پیام به Owner
    try:
        chat_title = chat.title or str(chat.id)
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=(
                f"🚨 *ریید در گروه* {chat_title}\n\n"
                f"🆔 `{chat.id}`\n"
                f"👥 `{count}` عضو جدید\n"
                f"⚙️ {action_txt}"
            ),
            parse_mode="Markdown"
        )
    except Exception:
        pass

    # تایمر برای پایان ریید
    async def _end_raid():
        await asyncio.sleep(duration)
        info = _RAID_LOCK.get(chat.id)
        if info:
            _RAID_LOCK.pop(chat.id, None)
            if info.get("event_id"):
                end_raid_event(info["event_id"])
            try:
                await context.bot.send_message(
                    chat_id=chat.id,
                    text="✅ حالت ریید تمام شد. گروه دوباره فعال شد."
                )
            except Exception:
                pass
            try:
                await context.bot.send_message(
                    chat_id=OWNER_ID,
                    text=f"✅ ریید گروه `{chat.id}` تمام شد.",
                    parse_mode="Markdown"
                )
            except Exception:
                pass

    asyncio.create_task(_end_raid())


async def raid_check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """چک ریید در Middleware - اگه ریید فعاله، فقط اعضای جدید پیامشون پاک شه"""
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user:
        return
    if chat.type not in ("group", "supergroup"):
        return

    if not _is_raid_active(chat.id):
        return

    # استثنا: Owner و Sudo
    try:
        from database import is_bot_owner_or_sudo
        if user.id == OWNER_ID or is_bot_owner_or_sudo(user.id):
            return
    except Exception:
        pass

    # 👴 اگه محافظت از اعضای قبلی فعاله، فقط اعضای جدید رو بلاک کن
    if _get_protect_old(chat.id):
        new_members = _RAID_NEW_MEMBERS.get(chat.id, set())
        if user.id not in new_members:
            return  # عضو قبلی → اجازه بده

    # حذف پیام
    try:
        await msg.delete()
    except Exception:
        pass


# ==================== پنل per-chat ====================
def build_raid_panel(uid, chat_id):
    enabled = get_chat_raid_setting(chat_id, "enabled", "0") == "1"
    threshold = get_chat_raid_setting(chat_id, "threshold", "10")
    window = get_chat_raid_setting(chat_id, "window", "60")
    duration = get_chat_raid_setting(chat_id, "duration", "600")
    action = get_chat_raid_setting(chat_id, "action", "lock")

    action_labels = {
        "lock": "🔒 قفل گروه",
        "lock_ban": "🔒 قفل + بن",
        "notify": "📢 فقط هشدار",
    }
    dur_label = f"{int(duration) // 60} دقیقه" if int(duration) >= 60 else f"{duration} ثانیه"

    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🛡 Anti-Raid: {'✅ فعال' if enabled else '❌ غیرفعال'}", callback_data=f"raid_tog:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"👥 تعداد اعضا: {threshold} نفر", callback_data=f"raid_set_th:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"⏱ بازه زمانی: {window} ثانیه", callback_data=f"raid_set_wd:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"⚙️ اکشن: {action_labels.get(action, '🔒 قفل')}", callback_data=f"raid_set_ac:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"⏳ مدت ریید: {dur_label}", callback_data=f"raid_set_dur:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"👴 محافظت از اعضای قبلی: {'✅ فعال' if get_chat_raid_setting(chat_id, 'protect_old', '1') == '1' else '❌ غیرفعال'}", callback_data=f"raid_tog_old:{uid}:{chat_id}")],
        [InlineKeyboardButton("📜 تاریخچه رییدها", callback_data=f"raid_history:{uid}:{chat_id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data=f"menu_settings:{uid}:{chat_id}")],
    ])


async def raid_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data
    parts = data.split(":")
    action_name = parts[0]

    # دسترسی: Owner، Sudo، مالک گروه
    uid = user.id
    chat_id = 0
    try:
        if len(parts) > 2 and parts[2].lstrip("-").isdigit():
            chat_id = int(parts[2])
    except Exception:
        pass

    allowed = False
    try:
        from database import is_bot_admin
        if user.id == OWNER_ID or is_bot_admin(user.id):
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
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    if action_name == "raid_panel":
        try:
            await query.edit_message_text(
                "🛡 *پنل Anti-Raid*\n\nاز دکمه‌ها استفاده کن:",
                reply_markup=build_raid_panel(uid, chat_id),
                parse_mode="Markdown"
            )
        except Exception:
            pass
        await query.answer()
        return

    if action_name == "raid_tog":
        cur = get_chat_raid_setting(chat_id, "enabled", "0")
        new = "0" if cur == "1" else "1"
        set_chat_raid_setting(chat_id, "enabled", new)
        try:
            await query.edit_message_reply_markup(reply_markup=build_raid_panel(uid, chat_id))
        except Exception:
            pass
        await query.answer("✅ فعال" if new == "1" else "❌ غیرفعال")
        return

    if action_name == "raid_set_th":
        opts = ["5", "10", "15", "20", "30", "50", "100"]
        cur = get_chat_raid_setting(chat_id, "threshold", "10")
        try:
            i = opts.index(cur)
            new = opts[(i + 1) % len(opts)]
        except ValueError:
            new = "10"
        set_chat_raid_setting(chat_id, "threshold", new)
        try:
            await query.edit_message_reply_markup(reply_markup=build_raid_panel(uid, chat_id))
        except Exception:
            pass
        await query.answer(f"✅ {new} نفر")
        return

    if action_name == "raid_set_wd":
        opts = ["30", "60", "120", "300", "600"]
        cur = get_chat_raid_setting(chat_id, "window", "60")
        try:
            i = opts.index(cur)
            new = opts[(i + 1) % len(opts)]
        except ValueError:
            new = "60"
        set_chat_raid_setting(chat_id, "window", new)
        try:
            await query.edit_message_reply_markup(reply_markup=build_raid_panel(uid, chat_id))
        except Exception:
            pass
        await query.answer(f"✅ {new} ثانیه")
        return

    if action_name == "raid_set_ac":
        opts = ["lock", "lock_ban", "notify"]
        cur = get_chat_raid_setting(chat_id, "action", "lock")
        try:
            i = opts.index(cur)
            new = opts[(i + 1) % len(opts)]
        except ValueError:
            new = "lock"
        set_chat_raid_setting(chat_id, "action", new)
        try:
            await query.edit_message_reply_markup(reply_markup=build_raid_panel(uid, chat_id))
        except Exception:
            pass
        await query.answer("✅ تغییر کرد")
        return

    if action_name == "raid_set_dur":
        opts = ["60", "300", "600", "1800", "3600", "7200"]
        cur = get_chat_raid_setting(chat_id, "duration", "600")
        try:
            i = opts.index(cur)
            new = opts[(i + 1) % len(opts)]
        except ValueError:
            new = "600"
        set_chat_raid_setting(chat_id, "duration", new)
        try:
            await query.edit_message_reply_markup(reply_markup=build_raid_panel(uid, chat_id))
        except Exception:
            pass
        await query.answer(f"✅ {int(new) // 60} دقیقه")
        return

    if action_name == "raid_tog_old":
        cur = get_chat_raid_setting(chat_id, "protect_old", "1")
        new = "0" if cur == "1" else "1"
        set_chat_raid_setting(chat_id, "protect_old", new)
        try:
            await query.edit_message_reply_markup(reply_markup=build_raid_panel(uid, chat_id))
        except Exception:
            pass
        await query.answer("✅ فعال" if new == "1" else "❌ غیرفعال")
        return

    if action_name == "raid_history":
        rows = get_raid_history(chat_id, limit=10)
        if not rows:
            await query.answer("📜 هیچ رییدی ثبت نشده", show_alert=True)
            return
        text = "📜 *تاریخچه رییدها*\n\n"
        for r in rows:
            rid, action, cnt, trig, ended, status = r
            status_lbl = "🔴 فعال" if status == "active" else "✅ پایان"
            text += f"• `{trig}` - {cnt} نفر - {action} - {status_lbl}\n"
        kb = [[InlineKeyboardButton("🔙 بازگشت", callback_data=f"raid_panel:{uid}:{chat_id}")]]
        try:
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            pass
        await query.answer()
        return

    await query.answer()


def register(app):
    # دستور /raid برای دسترسی سریع
    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, check_raid),
        group=-180
    )
    app.add_handler(
        CallbackQueryHandler(raid_cb, pattern=r"^raid_"),
        group=-42
    )
    print("OK module anti_raid loaded")
