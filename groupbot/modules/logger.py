# -*- coding: utf-8 -*-
"""سیستم لاگ Sk.Team - هسته"""
import os, re, asyncio, time, sqlite3
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
from config import OWNER_ID, DATABASE_PATH
from database import (
    init_log_tables, set_log_channel, get_log_channel, remove_log_channel,
    toggle_log_channel, get_all_log_channels, archive_log_event, get_log_events,
    count_log_events, log_stats_by_chat, save_system_stats, get_latest_system_stats,
    is_bot_admin
)

NL = chr(10)
PENDING_SETUP = {}

CATEGORIES = {
    'ban': '🔨 بن', 'mute': '🔇 سکوت', 'warn': '⚠️ اخطار', 'kick': '🚪 اخراج',
    'purge': '🗑 پاک‌سازی', 'pin': '📌 پین', 'lock': '🔒 قفل', 'unlock': '🔓 باز کردن',
    'join': '👋 ورود', 'leave': '🚶 خروج', 'fkick': '👢 حذف',
    'badword': '🚫 فحش', 'spam': '⚡ ضد اسپم', 'raid': '🛡 Anti-Raid', 'nsfw': '🔞 NSFW', 'link': '🔗 لینک',
    'sub_new': '✅ اشتراک جدید', 'sub_expire': '⏰ انقضای اشتراک', 'sub_extend': '🔄 تمدید',
    'fj_add': '➕ FJ افزودن', 'fj_del': '🗑 FJ حذف', 'fj_on': '🟢 FJ روشن', 'fj_off': '🔴 FJ خاموش',
    'admin_add': '➕ ادمین افزودن', 'admin_del': '🗑 ادمین حذف', 'perm_change': '🔐 تغییر دسترسی',
    'setting_change': '⚙️ تغییر تنظیمات', 'sudo_action': '👑 اقدام سودو',
    'rec_start': '🎙 شروع ضبط', 'rec_stop': '⏹ پایان ضبط', 'music': '🎵 موزیک',
    'ai': '🤖 AI', 'sys': '💻 سیستم', 'err': '❌ خطا',
}


def fmt_time(t=None):
    if t is None: t = datetime.now()
    return t.strftime("%Y/%m/%d - %H:%M:%S")


def _cat_label(a):
    return CATEGORIES.get(a, a)


def _build_event_text(scope, chat_id, action, actor_id, actor_name, target_id, target_name, details, ts):
    lines = ["🚨 " + _cat_label(action), "━━━━━━━━━━━━━━━━━━━━"]
    if scope == 'global' and chat_id:
        lines.append("📍 گروه: " + str(chat_id))
    if actor_id:
        lines.append("👮 " + str(actor_name or actor_id))
        lines.append("   ID: " + str(actor_id))
    if target_id:
        lines.append("👤 " + str(target_name or target_id))
        lines.append("   ID: " + str(target_id))
    if details:
        lines.append("📝 " + str(details))
    lines.append("⏰ " + str(ts))
    tag = "#group_" + str(abs(chat_id)) if chat_id else "#global"
    lines.append("")
    lines.append(tag + " #action_" + action)
    return NL.join(lines)


async def log_event(context, action, chat_id=0, actor_id=0, actor_name="", target_id=0, target_name="", details="", extra=None):
    ts = fmt_time()
    try:
        archive_log_event('global' if not chat_id else 'group', chat_id, action, actor_id, actor_name, target_id, target_name, details)
    except Exception as e:
        print("[LOG ARCH ERR] " + str(e))

    try:
        row = get_log_channel('global', 0)
        if row and row[3] == 1:
            txt = _build_event_text('global', chat_id, action, actor_id, actor_name, target_id, target_name, details, ts)
            try:
                await context.bot.send_message(row[1], txt)
            except Exception as e:
                print("[LOG GLOBAL ERR] " + str(e))
                toggle_log_channel('global', 0, False)
    except Exception as e:
        print("[LOG GLOBAL EXT ERR] " + str(e))

    if chat_id:
        try:
            row = get_log_channel('group', chat_id)
            if row and row[3] == 1:
                txt = _build_event_text('group', 0, action, actor_id, actor_name, target_id, target_name, details, ts)
                try:
                    await context.bot.send_message(row[1], txt)
                except Exception as e:
                    print("[LOG GROUP ERR] " + str(e))
                    toggle_log_channel('group', chat_id, False)
        except Exception as e:
            print("[LOG GROUP EXT ERR] " + str(e))


async def try_log(context, action, chat_id=0, **kw):
    try:
        await log_event(context, action, chat_id=chat_id, **kw)
    except Exception as e:
        print("[TRY LOG ERR] " + str(e))


def _parse_channel_input(text):
    if not text: return None
    t = text.strip()
    if t.startswith("@") and len(t) > 1: return t
    m = re.search(r't\.me/([A-Za-z0-9_]+)', t)
    if m: return "@" + m.group(1)
    m = re.search(r'telegram\.me/([A-Za-z0-9_]+)', t)
    if m: return "@" + m.group(1)
    if t.startswith("-100") and t[4:].isdigit(): return t
    return None


async def _verify_bot_admin(context, ref):
    try:
        chat = await context.bot.get_chat(ref)
        me = await context.bot.get_me()
        member = await context.bot.get_chat_member(chat.id, me.id)
        if member.status in ("administrator", "creator"):
            return (True, chat.id, chat.title or str(chat.id))
        return (False, None, "ربات تو این کانال ادمین نیست!")
    except Exception as e:
        return (False, None, "خطا: " + str(e)[:120])


def build_global_log_panel(uid):
    row = get_log_channel('global', 0)
    btns = []
    if row:
        _id, ch_id, title, en = row
        status = "✅ فعال" if en else "🔴 غیرفعال"
        text = ("📢 کانال لاگ گلوبال" + NL + "━━━━━━━━━━━━━━━━━━" + NL +
                "📊 وضعیت: " + status + NL +
                "📢 " + str(title) + NL +
                "🆔 " + str(ch_id) + NL)
        btns.append([InlineKeyboardButton("🔗 تغییر کانال", callback_data="log_g_set:" + str(uid))])
        btns.append([InlineKeyboardButton("🔴 غیرفعال" if en else "🟢 فعال", callback_data="log_g_toggle:" + str(uid))])
        btns.append([InlineKeyboardButton("🗑 حذف کانال", callback_data="log_g_del:" + str(uid))])
        btns.append([InlineKeyboardButton("📊 آمار لاگ", callback_data="log_stats:" + str(uid))])
    else:
        text = ("📢 کانال لاگ گلوبال" + NL + "━━━━━━━━━━━━━━━━━━" + NL +
                "❌ تنظیم نشده" + NL + NL +
                "لینک کانال رو بفرست (ربات باید ادمین باشه).")
        btns.append([InlineKeyboardButton("➕ تنظیم کانال", callback_data="log_g_set:" + str(uid))])
    btns.append([InlineKeyboardButton("🔙 بازگشت", callback_data="owner_section_back:" + str(uid) + ":0")])
    return text, InlineKeyboardMarkup(btns)


def build_group_log_panel(uid, chat_id):
    row = get_log_channel('group', chat_id)
    btns = []
    if row:
        _id, ch_id, title, en = row
        status = "✅ فعال" if en else "🔴 غیرفعال"
        text = ("📢 کانال لاگ گروه" + NL + "━━━━━━━━━━━━━━━━━━" + NL +
                "📊 وضعیت: " + status + NL +
                "📢 " + str(title) + NL +
                "🆔 " + str(ch_id) + NL)
        btns.append([InlineKeyboardButton("🔗 تغییر کانال", callback_data="log_gr_set:" + str(uid) + ":" + str(chat_id))])
        btns.append([InlineKeyboardButton("🔴 غیرفعال" if en else "🟢 فعال", callback_data="log_gr_toggle:" + str(uid) + ":" + str(chat_id))])
        btns.append([InlineKeyboardButton("🗑 حذف", callback_data="log_gr_del:" + str(uid) + ":" + str(chat_id))])
    else:
        text = ("📢 کانال لاگ گروه" + NL + "━━━━━━━━━━━━━━━━━━" + NL +
                "❌ تنظیم نشده" + NL + NL +
                "لینک کانال رو بفرست (ربات باید ادمین باشه).")
        btns.append([InlineKeyboardButton("➕ تنظیم کانال", callback_data="log_gr_set:" + str(uid) + ":" + str(chat_id))])
    btns.append([InlineKeyboardButton("🔙 بازگشت", callback_data="menu_settings:" + str(uid) + ":" + str(chat_id))])
    return text, InlineKeyboardMarkup(btns)


def build_stats_panel(uid):
    text = "📊 آمار لاگ‌ها" + NL + "━━━━━━━━━━━━━━━━━━" + NL + NL + "🔍 بازه:"
    btns = [
        [InlineKeyboardButton("📅 امروز", callback_data="log_stats_1:" + str(uid))],
        [InlineKeyboardButton("📅 هفته", callback_data="log_stats_7:" + str(uid))],
        [InlineKeyboardButton("📅 ماه", callback_data="log_stats_30:" + str(uid))],
        [InlineKeyboardButton("📅 کل", callback_data="log_stats_0:" + str(uid))],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="log_g_panel:" + str(uid))],
    ]
    return text, InlineKeyboardMarkup(btns)


def build_stats_detail(uid, days):
    d = None if days == 0 else days
    txt = "📊 آمار " + ("کل" if days == 0 else str(days) + " روز") + NL + "━━━━━━━━━━━━━━━━━━" + NL + NL
    total = count_log_events(days=d)
    txt += "📋 مجموع: " + str(total) + NL + NL
    txt += "🔝 دسته‌ها:" + NL
    for cat, lbl in CATEGORIES.items():
        cnt = count_log_events(action=cat, days=d)
        if cnt > 0:
            txt += "• " + lbl + ": " + str(cnt) + NL
    btns = [[InlineKeyboardButton("🔙 بازگشت", callback_data="log_stats:" + str(uid))]]
    return txt, InlineKeyboardMarkup(btns)


async def log_cb(update, context):
    query = update.callback_query
    print("[LOG CB] called data=" + str(query.data if query else None))
    if not query: return
    data = query.data or ""
    user = query.from_user
    if not user: return
    print("[LOG CB] user=" + str(user.id) + " action=" + data.split(":")[0])
    parts = data.split(":")
    action = parts[0]

    is_owner = (user.id == OWNER_ID)
    is_sudo = False if is_owner else is_bot_admin(user.id)
    action_name = data.split(":")[0]

    # لاگ گروه → مالک گروه هم می‌تونه
    if action_name.startswith("log_gr_"):
        if not (is_owner or is_sudo):
            parts_perm = data.split(":")
            _grp_ok = False
            if len(parts_perm) >= 3:
                try:
                    _grp_chat = int(parts_perm[2])
                    from database import is_group_owner
                    if is_group_owner(_grp_chat, user.id):
                        _grp_ok = True
                except Exception as _pe:
                    print("[LOG PERM ERR] " + str(_pe))
            if not _grp_ok:
                await query.answer("⛔ دسترسی ندارید", show_alert=True)
                return
    else:
        # لاگ گلوبال → فقط سازنده/سودو
        if not (is_owner or is_sudo):
            await query.answer("⛔ دسترسی ندارید", show_alert=True)
            return

    try:
        if action == "log_g_panel":
            txt, kb = build_global_log_panel(user.id)
            await query.edit_message_text(txt, reply_markup=kb)
            return
        if action == "log_g_set":
            PENDING_SETUP[user.id] = {"scope": "global", "owner_chat_id": 0, "msg_id": query.message.message_id, "chat_id": query.message.chat.id}
            await query.edit_message_text(
                "📢 تنظیم کانال لاگ گلوبال" + NL + "━━━━━━━━━━━━━━━━━━" + NL + NL +
                "لینک یا @username کانال رو بفرست:" + NL + NL +
                "مثال: @SkTeamLogs" + NL + "یا" + NL + "https://t.me/SkTeamLogs" + NL + NL +
                "⚠️ ربات باید ادمین باشه.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 انصراف", callback_data="log_g_panel:" + str(user.id))]]))
            return
        if action == "log_g_toggle":
            row = get_log_channel('global', 0)
            if row: toggle_log_channel('global', 0, not row[3])
            txt, kb = build_global_log_panel(user.id)
            await query.edit_message_text(txt, reply_markup=kb)
            return
        if action == "log_g_del":
            remove_log_channel('global', 0)
            txt, kb = build_global_log_panel(user.id)
            await query.edit_message_text(txt, reply_markup=kb)
            await query.answer("حذف شد")
            return
        if action == "log_gr_set":
            chat_id = int(parts[2])
            PENDING_SETUP[user.id] = {"scope": "group", "owner_chat_id": chat_id, "msg_id": query.message.message_id, "chat_id": query.message.chat.id}
            await query.edit_message_text(
                "📢 تنظیم کانال لاگ گروه" + NL + "━━━━━━━━━━━━━━━━━━" + NL + NL +
                "لینک یا @username کانال رو بفرست:" + NL + NL +
                "مثال: @MyGroupLogs" + NL + "یا" + NL + "https://t.me/MyGroupLogs" + NL + NL +
                "⚠️ ربات باید ادمین باشه.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 انصراف", callback_data="log_gr_panel:" + str(user.id) + ":" + str(chat_id))]]))
            return
        if action == "log_gr_panel":
            chat_id = int(parts[2])
            txt, kb = build_group_log_panel(user.id, chat_id)
            await query.edit_message_text(txt, reply_markup=kb)
            return
        if action == "log_gr_toggle":
            chat_id = int(parts[2])
            row = get_log_channel('group', chat_id)
            if row: toggle_log_channel('group', chat_id, not row[3])
            txt, kb = build_group_log_panel(user.id, chat_id)
            await query.edit_message_text(txt, reply_markup=kb)
            return
        if action == "log_gr_del":
            chat_id = int(parts[2])
            remove_log_channel('group', chat_id)
            txt, kb = build_group_log_panel(user.id, chat_id)
            await query.edit_message_text(txt, reply_markup=kb)
            return
        if action == "log_stats":
            txt, kb = build_stats_panel_v2(user.id)
            await query.edit_message_text(txt, reply_markup=kb)
            return
        if action.startswith("log_stats_") or action.startswith("log_st_"):
            parts_d = action.split("_")
            days = int(parts_d[-1])
            txt, kb = build_stats_detail_v2(user.id, days)
            await query.edit_message_text(txt, reply_markup=kb)
            return
        if action == "log_groups":
            page = 0
            if len(parts) >= 3:
                try: page = int(parts[2])
                except Exception: page = 0
            txt, kb = build_groups_stats(user.id, page)
            await query.edit_message_text(txt, reply_markup=kb)
            return
        if action == "log_chat":
            cid = int(parts[2])
            txt, kb = build_chat_detail(user.id, cid)
            await query.edit_message_text(txt, reply_markup=kb)
            return
        if action == "log_events":
            cid = int(parts[2])
            offset = 0
            if len(parts) >= 4:
                try: offset = int(parts[3])
                except Exception: offset = 0
            txt, kb = build_recent_events(user.id, cid, offset)
            await query.edit_message_text(txt, reply_markup=kb)
            return
        if action == "log_sudos":
            await query.answer("به‌زودی...", show_alert=True)
            return
        if action == "log_search":
            await query.answer("به‌زودی...", show_alert=True)
            return
    except Exception as e:
        print("[LOG CB ERR] " + str(e))
        try: await query.answer("خطا", show_alert=True)
        except Exception: pass




async def _send_welcome_to_channel(context, channel_id, scope, owner_chat_id, user_id, user_name):
    """ارسال پیام فعال‌سازی به کانال لاگ"""
    try:
        from datetime import datetime
        now = datetime.now().strftime("%Y/%m/%d - %H:%M:%S")
        if scope == "global":
            title = "🌍 کانال لاگ گلوبال فعال شد!"
            info = ("📢 این کانال برای لاگ **کل ربات** تنظیم شد." + NL +
                    "تمام رخدادهای همه گروه‌ها اینجا ثبت می‌شه.")
        else:
            title = "🏠 کانال لاگ گروه فعال شد!"
            grp_name = str(owner_chat_id)
            try:
                gchat = await context.bot.get_chat(owner_chat_id)
                grp_name = gchat.title or str(owner_chat_id)
            except Exception:
                pass
            info = ("📢 این کانال برای لاگ گروه زیر تنظیم شد:" + NL +
                    "🏠 " + grp_name + NL +
                    "🆔 " + str(owner_chat_id))

        txt = (title + NL +
               "━━━━━━━━━━━━━━━━━━━━" + NL + NL +
               info + NL + NL +
               "👤 تنظیم‌کننده: " + str(user_name) + NL +
               "🆔 " + str(user_id) + NL +
               "⏰ " + now + NL + NL +
               "✅ از این لحظه، همه رخدادها اینجا ثبت می‌شن.")

        await context.bot.send_message(channel_id, txt)
        print("[LOG WELCOME] sent to " + str(channel_id))
        return True
    except Exception as e:
        print("[LOG WELCOME ERR] " + str(e))
        return False


async def log_text_handler(update, context):
    msg = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    if not msg or not user or not chat: return
    if chat.type != "private": return
    if user.id not in PENDING_SETUP: return

    info = PENDING_SETUP.get(user.id) or {}
    scope = info.get("scope", "global")
    owner_chat_id = info.get("owner_chat_id", 0)
    orig_msg_id = info.get("msg_id")
    orig_chat_id = info.get("chat_id")

    # استخراج ref
    ref = None
    try:
        fc = getattr(msg, 'forward_from_chat', None)
        if fc and fc.type in ("channel", "supergroup"):
            ref = str(fc.id)
    except Exception: pass

    if not ref:
        try:
            fo = getattr(msg, 'forward_origin', None)
            if fo:
                fc = getattr(fo, 'chat', None) or getattr(fo, 'sender_chat', None)
                if fc and fc.type in ("channel", "supergroup"):
                    ref = str(fc.id)
        except Exception: pass

    if not ref:
        txt = (msg.text or "").strip()
        if not txt: return
        if txt.startswith("/"):
            PENDING_SETUP.pop(user.id, None)
            return
        ref = _parse_channel_input(txt)

    if not ref:
        await msg.reply_text(
            "❌ نامعتبر. یکی از این سه راه:" + NL + NL +
            "1️⃣ @YourChannel" + NL +
            "2️⃣ https://t.me/YourChannel" + NL +
            "3️⃣ 👈 یه پیام از کانال رو **فوروارد** کن"
        )
        return

    # چک ادمین بودن ربات
    ok, ch_id, title = await _verify_bot_admin(context, ref)
    if not ok:
        await msg.reply_text("❌ " + str(title) + NL + NL + "👉 ربات توی کانال ادمین باشه.")
        return

    # ذخیره
    if not set_log_channel(scope, owner_chat_id, ch_id, title, user.id):
        await msg.reply_text("❌ خطا در ذخیره")
        return

    PENDING_SETUP.pop(user.id, None)

    # ارسال welcome به کانال
    try:
        await _send_welcome_to_channel(context, ch_id, scope, owner_chat_id, user.id, user.full_name or user.username or str(user.id))
    except Exception as _we:
        print("[LOG WELCOME CALL ERR] " + str(_we))

    # پاک کردن پیام لینک کاربر
    try:
        await msg.delete()
    except Exception: pass

    # ویرایش پیام اصلی (لینک بفرست) به پنل جدید
    sn = "گلوبال" if scope == "global" else "گروه"
    if orig_msg_id and orig_chat_id:
        try:
            if scope == "global":
                txt, kb = build_global_log_panel(user.id)
            else:
                txt, kb = build_group_log_panel(user.id, owner_chat_id)
            await context.bot.edit_message_text(
                chat_id=orig_chat_id,
                message_id=orig_msg_id,
                text=txt + NL + NL + "✅ " + sn + " ثبت شد!",
                reply_markup=kb
            )
            print("[LOG SAVE OK] " + sn + " ch=" + str(ch_id))
            return
        except Exception as e:
            print("[LOG EDIT ERR] " + str(e))

    # اگه edit نشد، پیام جدید
    await msg.reply_text("✅ کانال لاگ " + sn + " ثبت شد!" + NL + "📢 " + str(title))


def register(app):
    global _LOGGER_REGISTERED
    if _LOGGER_REGISTERED:
        print("ℹ️ logger already registered, skipping")
        return
    _LOGGER_REGISTERED = True
    try:
        init_log_tables()
        print("OK log tables initialized")
    except Exception as e:
        print("[LOG INIT ERR] " + str(e))
    try:
        app.add_handler(CallbackQueryHandler(log_cb, pattern="^log_"), group=2)
        app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, log_text_handler), group=2)
        print("OK module logger loaded at group=+2")
    except Exception as e:
        print("[LOG REG ERR] " + str(e))

def register(app):
    print("[LOGGER REGISTER] called")
    try:
        init_log_tables()
        print("OK log tables initialized")
    except Exception as e:
        print("[LOG INIT ERR] " + str(e))
    try:
        # group=-1000 → قبل از همه چیز
        app.add_handler(CallbackQueryHandler(log_cb, pattern="^log_"), group=-1000)
        app.add_handler(MessageHandler(filters.ALL, log_text_handler), group=-1000)
        print("OK module logger loaded at group=-1000")
    except Exception as e:
        print("[LOG REG ERR] " + str(e))


# [STATS-PANEL-V2-START]
def build_stats_panel_v2(uid):
    text = "📊 آمار لاگ — انتخاب بازه:" + NL + "━━━━━━━━━━━━━━━━━━" + NL
    btns = [
        [InlineKeyboardButton("📅 امروز", callback_data="log_st_1:" + str(uid))],
        [InlineKeyboardButton("📅 هفته", callback_data="log_st_7:" + str(uid))],
        [InlineKeyboardButton("📅 ماه", callback_data="log_st_30:" + str(uid))],
        [InlineKeyboardButton("📅 کل", callback_data="log_st_0:" + str(uid))],
        [InlineKeyboardButton("🏠 آمار گروه‌ها", callback_data="log_groups:" + str(uid))],
        [InlineKeyboardButton("👑 آمار سودوها", callback_data="log_sudos:" + str(uid))],
        [InlineKeyboardButton("🔍 جستجو", callback_data="log_search:" + str(uid))],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="log_g_panel:" + str(uid))],
    ]
    return text, InlineKeyboardMarkup(btns)


def build_stats_detail_v2(uid, days):
    d = None if days == 0 else days
    txt = "📊 آمار " + ("کل" if days == 0 else str(days) + " روز") + NL + "━━━━━━━━━━━━━━━━━━" + NL
    total = count_log_events(days=d)
    txt += "📋 مجموع: " + str(total) + NL + NL
    txt += "🔝 دسته‌ها:" + NL
    for cat, lbl in CATEGORIES.items():
        cnt = count_log_events(action=cat, days=d)
        if cnt > 0:
            txt += "• " + lbl + ": " + str(cnt) + NL
    btns = [[InlineKeyboardButton("🔙 بازگشت", callback_data="log_stats:" + str(uid))]]
    return txt, InlineKeyboardMarkup(btns)


def build_groups_stats(uid, page=0):
    rows = log_stats_by_chat(days=30)
    if not rows:
        txt = "🏠 آماری نیست."
        btns = [[InlineKeyboardButton("🔙 بازگشت", callback_data="log_stats:" + str(uid))]]
        return txt, InlineKeyboardMarkup(btns)
    per_page = 5
    start = page * per_page
    end = start + per_page
    subset = rows[start:end]
    txt = "🏠 آمار گروه‌ها (۳۰ روز اخیر)" + NL + "━━━━━━━━━━━━━━━━━━" + NL
    btns = []
    for chat_id, cnt in subset:
        txt += "• " + str(chat_id) + " — " + str(cnt) + " رخداد" + NL
        btns.append([InlineKeyboardButton("📄 " + str(chat_id)[-10:],
                     callback_data="log_chat:" + str(uid) + ":" + str(chat_id))])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️ قبلی", callback_data="log_groups:" + str(uid) + ":" + str(page-1)))
    if end < len(rows):
        nav.append(InlineKeyboardButton("بعدی ▶️", callback_data="log_groups:" + str(uid) + ":" + str(page+1)))
    if nav: btns.append(nav)
    btns.append([InlineKeyboardButton("🔙 بازگشت", callback_data="log_stats:" + str(uid))])
    return txt, InlineKeyboardMarkup(btns)


def build_chat_detail(uid, chat_id):
    txt = "🏠 گروه " + str(chat_id) + NL + "━━━━━━━━━━━━━━━━━━" + NL
    total = count_log_events(chat_id=chat_id, days=30)
    txt += "📋 مجموع ۳۰ روز: " + str(total) + NL + NL
    txt += "🔝 دسته‌ها:" + NL
    for cat, lbl in CATEGORIES.items():
        cnt = count_log_events(action=cat, chat_id=chat_id, days=30)
        if cnt > 0:
            txt += "• " + lbl + ": " + str(cnt) + NL
    btns = [
        [InlineKeyboardButton("📜 آخرین رخدادها", callback_data="log_events:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="log_groups:" + str(uid))],
    ]
    return txt, InlineKeyboardMarkup(btns)


def build_recent_events(uid, chat_id, offset=0):
    events = get_log_events(chat_id=chat_id, limit=10, offset=offset)
    if not events:
        txt = "📜 رخدادی نیست."
        btns = [[InlineKeyboardButton("🔙 بازگشت", callback_data="log_chat:" + str(uid) + ":" + str(chat_id))]]
        return txt, InlineKeyboardMarkup(btns)
    txt = "📜 آخرین رخدادهای " + str(chat_id) + NL + "━━━━━━━━━━━━━━━━━━" + NL
    for ev in events:
        _id, scope, cid, act, aid, aname, tid, tname, det, ts = ev
        lbl = CATEGORIES.get(act, act)
        txt += "• " + str(lbl) + " | " + str(ts)[:16] + NL
        if tname: txt += "  👤 " + str(tname)[:20] + NL
    nav = []
    if offset > 0:
        nav.append(InlineKeyboardButton("◀️ قبلی", callback_data="log_events:" + str(uid) + ":" + str(chat_id) + ":" + str(max(0, offset-10))))
    if len(events) == 10:
        nav.append(InlineKeyboardButton("بعدی ▶️", callback_data="log_events:" + str(uid) + ":" + str(chat_id) + ":" + str(offset+10)))
    btns = []
    if nav: btns.append(nav)
    btns.append([InlineKeyboardButton("🔙 بازگشت", callback_data="log_chat:" + str(uid) + ":" + str(chat_id))])
    return txt, InlineKeyboardMarkup(btns)


async def collect_system_stats(context=None):
    try:
        import subprocess, sqlite3, time as _t
        from config import DATABASE_PATH
        # ping به تلگرام
        ping_ms = 0
        try:
            _t0 = _t.time()
            if context:
                await context.bot.get_me()
            ping_ms = int((_t.time() - _t0) * 1000)
        except Exception:
            ping_ms = 0
        # RAM / CPU
        ram_mb = 0.0
        cpu_pct = 0.0
        try:
            ps = subprocess.run(["ps", "-o", "rss,pcpu", "-p", str(os.getpid())],
                                capture_output=True, text=True, timeout=5)
            lines = ps.stdout.strip().split("\n")
            if len(lines) > 1:
                parts = lines[-1].split()
                if len(parts) >= 2:
                    ram_mb = float(parts[0]) / 1024
                    cpu_pct = float(parts[1])
        except Exception:
            pass
        # Disk
        disk_mb = 0.0
        try:
            st = os.statvfs(str(Path.home() / "groupbot"))
            disk_mb = (st.f_blocks - st.f_bfree) * st.f_frsize / (1024*1024)
        except Exception:
            pass
        # DB size
        db_kb = 0.0
        try:
            db_kb = os.path.getsize(DATABASE_PATH) / 1024
        except Exception:
            pass
        save_system_stats(ping_ms, ram_mb, cpu_pct, disk_mb, db_kb, 0, 0, 0)
        # اگه کانال گلوبال فعاله، آمار روزانه/ساعتی بفرست
        if context:
            try:
                row = get_log_channel('global', 0)
                if row and row[3] == 1:
                    # هر ساعت یه بار
                    from datetime import datetime
                    now_min = datetime.now().minute
                    if now_min < 5:  # فقط توی ۵ دقیقه اول هر ساعت
                        txt = ("💻 آمار سیستم" + NL + "━━━━━━━━━━━━━━━━━━" + NL +
                               "⏱ Ping: " + str(ping_ms) + "ms" + NL +
                               "💾 RAM: " + str(round(ram_mb, 1)) + " MB" + NL +
                               "⚙️ CPU: " + str(round(cpu_pct, 1)) + "%" + NL +
                               "💿 Disk: " + str(round(disk_mb, 1)) + " MB" + NL +
                               "📊 DB: " + str(round(db_kb, 1)) + " KB" + NL +
                               "⏰ " + datetime.now().strftime("%Y/%m/%d - %H:%M"))
                        try:
                            await context.bot.send_message(row[1], txt)
                        except Exception:
                            pass
            except Exception:
                pass
        return True
    except Exception as e:
        print("[SYS STATS ERR] " + str(e))
        return False
# [STATS-PANEL-V2-END]

