import re

# الگوی یونیکد برای «آمار کال» و «امار کال»
AMAR_VCALL_REGEX = re.compile(u"^[\u0622\u0627]\u0645\u0627\u0631 \u06a9\u0627\u0644$")

"""
ماژول آمار کال - Voice Call Stats Module

این ماژول وظیفه دریافت و نمایش آمار ویس‌کال رو داره.
ربات موزیک پلیر اطلاعات رو از طریق یه پیام خاص به این ربات می‌فرسته.

فرمت پیام:
    VCSTAT:{API_KEY}:{chat_id}:{date}:{json_data}

مثال:
    VCSTAT:secret123:-1001234567890:2024-10-15:{"total_seconds":11520,"users":[{"user_id":123,"username":"ali","first_name":"Ali","total_seconds":3540,"session_count":2}]}

تاریخچه تغییرات:
- نسخه 1.0: ساخت اولیه، پشتیبانی از VCSTAT
"""

import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, CommandHandler, filters

NL = chr(10)


def format_duration(seconds):
    """تبدیل ثانیه به فرمت ساعت و دقیقه"""
    if not seconds:
        return "0 دقیقه"
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return str(h) + " ساعت و " + str(m) + " دقیقه"
    elif m > 0:
        return str(m) + " دقیقه و " + str(s) + " ثانیه"
    else:
        return str(s) + " ثانیه"


def format_persian_date(date_str):
    """تبدیل تاریخ میلادی به شمسی (تقریبی)"""
    try:
        from datetime import datetime
        d = datetime.strptime(date_str, "%Y-%m-%d")
        # تبدیل تقریبی میلادی به شمسی
        # فرمول ساده: هر سال میلادی ≈ 621.5 سال شمسی
        import datetime as dt
        # اینجا از یه کتابخانه یا فرمول دقیق استفاده می‌کنیم
        return date_str  # فعلاً همون میلادی
    except Exception:
        return date_str


def _get_medal(rank):
    """دریافت مدال بر اساس رتبه"""
    if rank == 1:
        return "🥇"
    elif rank == 2:
        return "🥈"
    elif rank == 3:
        return "🥉"
    else:
        return str(rank) + " -"


async def vcstat_receiver(update, context):
    """
    دریافت پیام VCSTAT از ربات موزیک پلیر.
    فرمت: VCSTAT:{API_KEY}:{chat_id}:{date}:{json_data}
    """
    msg = update.effective_message
    if not msg or not msg.text:
        return
    text = msg.text.strip()
    if not text.startswith("VCSTAT:"):
        return
    
    try:
        from config import MUSIC_BOT_API_KEY
        parts = text.split(":", 4)  # حداکثر 5 بخش
        if len(parts) < 5:
            print("[VCSTAT] Invalid format: " + text[:100])
            return
        
        _, api_key, chat_id_str, date, json_data = parts
        if api_key != MUSIC_BOT_API_KEY:
            print("[VCSTAT] Invalid API key")
            await msg.reply_text("❌ Invalid API key")
            return
        
        chat_id = int(chat_id_str)
        data = json.loads(json_data)
        total_seconds = data.get("total_seconds", 0)
        users_list = data.get("users", [])
        
        from database import save_voice_call_report
        save_voice_call_report(chat_id, date, total_seconds, users_list)
        
        print("[VCSTAT] Saved report for chat " + str(chat_id) + " date " + date + " (" + str(len(users_list)) + " users)")
        await msg.reply_text("✅ آمار دریافت شد (" + str(len(users_list)) + " کاربر)")
    except Exception as e:
        print("[VCSTAT ERR] " + str(e))
        await msg.reply_text("❌ خطا: " + str(e)[:200])


async def vcall_stats_cmd(update, context):
    """
    دستور «آمار کال» - نمایش آمار ویس‌کال
    استفاده: 
        آمار کال
        یا
        /vcall_stats
    """
    msg = update.effective_message
    chat = update.effective_chat
    if chat.type not in ("group", "supergroup"):
        await msg.reply_text("❌ این دستور فقط توی گروه کار می‌کند.")
        return
    
    try:
        from database import get_voice_call_stats, get_voice_call_last_date
        chat_id = chat.id
        
        # اگه تاریخ داده شده بود استفاده کن، وگرنه آخرین تاریخ
        args = context.args if context.args else []
        if args:
            date = args[0]
        else:
            date = get_voice_call_last_date(chat_id)
            if not date:
                await msg.reply_text("📭 هنوز هیچ آماری از کال ثبت نشده.")
                return
        
        total, rows = get_voice_call_stats(chat_id, date)
        
        if not rows:
            await msg.reply_text("📭 هیچ آماری برای تاریخ " + date + " موجود نیست.")
            return
        
        text = ("📊 آمار کال گروه" + NL + "━━━━━━━━━━━━━━" + NL +
                "📅 تاریخ: " + date + NL +
                "⏱️ زمان کل: " + format_duration(total) + NL +
                "━━━━━━━━━━━━━━" + NL + NL)
        
        for i, (uid_db, uname, fname, secs, s_cnt) in enumerate(rows, 1):
            name = fname or "بدون نام"
            un_str = " | @" + uname if uname else ""
            percent = int((secs / total) * 100) if total > 0 else 0
            medal = _get_medal(i)
            text += medal + " " + name + un_str + NL
            text += "   ⏱️ " + format_duration(secs) + " | " + str(percent) + "%" + NL
            text += "   " + "─" * 20 + NL
        
        await msg.reply_text(text)
    except Exception as e:
        print("[VCALL STATS CMD ERR] " + str(e))
        try:
            await msg.reply_text("❌ خطا: " + str(e)[:200])
        except Exception:
            pass



async def invitecall_cmd(update, context):
    """دعوت اعضای آخرین کال ذخیره‌شده"""
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user:
        return
    if chat.type not in ("group", "supergroup"):
        return

    # دسترسی: Owner، Sudo، مالک گروه، ادمین گروه
    allowed = False
    try:
        from config import OWNER_ID
        from database import is_bot_owner_or_sudo, is_group_owner
        if user.id == OWNER_ID or is_bot_owner_or_sudo(user.id) or is_group_owner(chat.id, user.id):
            allowed = True
    except Exception:
        pass
    if not allowed:
        try:
            member = await chat.get_member(user.id)
            if member.status in ("creator", "administrator"):
                allowed = True
        except Exception:
            pass
    if not allowed:
        return

    from database import get_voice_call_participants, get_voice_call_save_time
    rows = get_voice_call_participants(chat.id)
    if not rows:
        await msg.reply_text("⚠️ لیستی برای دعوت وجود نداره.\n\nبعد از پایان کال، ربات موزیک لیست رو ذخیره می‌کنه.")
        return

    saved_at = get_voice_call_save_time(chat.id) or "نامعلوم"

    header = "🔔 دعوت به ویس چت\n\n📅 آخرین کال: " + saved_at + "\n\n"

    mentions = []
    for uid, fn, un, ts, sc, _ in rows:
        if un:
            mentions.append("[" + (fn or un) + "](https://t.me/" + un + ")")
        else:
            mentions.append("[" + (fn or "کاربر") + "](tg://user?id=" + str(uid) + ")")

    body = " ".join(mentions)
    full_text = header + body + "\n\n🔊 بیاید کال، منتظرتونیم!"
    if len(full_text) > 3800:
        full_text = full_text[:3800] + "..."

    try:
        await msg.reply_text(full_text, parse_mode="Markdown", disable_web_page_preview=True)
    except Exception:
        # fallback بدون Markdown
        plain = "🔔 دعوت به ویس چت\n📅 " + saved_at + "\n\n"
        for uid, fn, un, ts, sc, _ in rows:
            plain += "• " + (fn or "کاربر")
            if un:
                plain += " (@" + un + ")"
            plain += "\n"
        try:
            await msg.reply_text(plain[:3800])
        except Exception as e:
            print("[INVITECALL ERR]", str(e))


def register(app):
    """
    ثبت هندلرها.
    
    - MessageHandler برای دریافت VCSTAT از ربات موزیک پلیر
    - CommandHandler برای /vcall_stats
    - MessageHandler برای «آمار کال»
    """
    from telegram.ext import MessageHandler, CommandHandler, filters
    
    # دریافت VCSTAT (اولویت بالا - group=1)
    app.add_handler(
        MessageHandler(filters.Regex(r"^VCSTAT:") & filters.ChatType.PRIVATE, vcstat_receiver),
        group=1
    )
    
    # دستور /vcall_stats
    app.add_handler(CommandHandler("vcall_stats", vcall_stats_cmd))

    # دستور /invitecall
    app.add_handler(CommandHandler("invitecall", invitecall_cmd))
    
    # دستور نوشتاری «آمار کال»
    app.add_handler(
        MessageHandler(filters.Regex(AMAR_VCALL_REGEX) & filters.ChatType.GROUPS, vcall_stats_cmd),
        group=16
    )
    
    print("OK module voice_stats loaded")
