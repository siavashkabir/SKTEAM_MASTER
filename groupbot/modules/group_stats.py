import re

# الگوی یونیکد برای «آمار» و «امار»
AMAR_REGEX = re.compile(u"^[\u0622\u0627]\u0645\u0627\u0631$")

"""
ماژول آمار گروه (Group Stats)

وقتی کاربر توی گروه «آمار» می‌زنه، این ماژول اطلاعات کامل رو می‌فرسته:
- بهترین عضوکننده امروز (اد)
- فعال‌ترین اعضای امروز (پیام)
- فعال‌ترین اعضای کل (پیام)
- بهترین عضوکننده‌های کل (اد)
"""

from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters

NL = chr(10)


def _fmt_user(uid, uname, fname):
    """فرمت نمایش کاربر"""
    name = fname or "بدون نام"
    un = " | @" + uname if uname else ""
    return name + un


def _medal(i):
    if i == 1:
        return "🥇"
    elif i == 2:
        return "🥈"
    elif i == 3:
        return "🥉"
    else:
        return str(i) + " -"


async def group_stats_cmd(update, context):
    """دستور آمار گروه"""
    msg = update.effective_message
    chat = update.effective_chat
    if chat.type not in ("group", "supergroup"):
        await msg.reply_text("❌ این دستور فقط توی گروه کار می‌کند.")
        return

    try:
        from database import (
            get_top_active_daily, get_top_active_total,
            get_top_adders_daily, get_top_adders_total
        )
        today = datetime.now().strftime("%Y-%m-%d")
        cid = chat.id

        # بهترین عضوکننده امروز
        adders_today = get_top_adders_daily(cid, today, 5)
        # فعال‌ترین اعضای امروز
        active_today = get_top_active_daily(cid, today, 3)
        # فعال‌ترین اعضای کل
        active_total = get_top_active_total(cid, 3)
        # بهترین عضوکننده‌های کل
        adders_total = get_top_adders_total(cid, 3)

        text = "📊 آمار گروه" + NL
        text += "━━━━━━━━━━━━━━" + NL + NL

        # بهترین عضوکننده امروز
        text += "🏆 بهترین عضوکننده امروز:" + NL
        if adders_today:
            for i, (uid, un, fn, cnt) in enumerate(adders_today, 1):
                text += _medal(i) + " " + _fmt_user(uid, un, fn) + NL
                text += "   👥 " + str(cnt) + " اد" + NL
        else:
            text += "❌ امروز عضوی اد نشده." + NL
        text += NL

        # فعال‌ترین اعضای امروز
        text += "💬 فعال‌ترین اعضای امروز:" + NL
        if active_today:
            for i, (uid, un, fn, cnt) in enumerate(active_today, 1):
                text += _medal(i) + " " + _fmt_user(uid, un, fn) + NL
                text += "   💬 " + str(cnt) + " پیام" + NL
        else:
            text += "❌ امروز پیامی ثبت نشده." + NL
        text += NL

        # فعال‌ترین اعضای کل
        text += "🔥 فعال‌ترین اعضای کل:" + NL
        if active_total:
            for i, (uid, un, fn, cnt) in enumerate(active_total, 1):
                text += _medal(i) + " " + _fmt_user(uid, un, fn) + NL
                text += "   💬 " + str(cnt) + " پیام" + NL
        else:
            text += "❌ هنوز آماری نیست." + NL
        text += NL

        # بهترین عضوکننده‌های کل
        text += "🎁 بهترین عضوکننده‌های کل:" + NL
        if adders_total:
            for i, (uid, un, fn, cnt) in enumerate(adders_total, 1):
                text += _medal(i) + " " + _fmt_user(uid, un, fn) + NL
                text += "   👥 " + str(cnt) + " اد" + NL
        else:
            text += "❌ هنوز آماری نیست." + NL
        text += NL + "━━━━━━━━━━━━━━"

        await msg.reply_text(text)
    except Exception as e:
        print("[GROUP STATS CMD ERR] " + str(e))
        try:
            await msg.reply_text("❌ خطا: " + str(e)[:200])
        except Exception:
            pass


def register(app):
    """ثبت هندلرها"""
    app.add_handler(CommandHandler("stats", group_stats_cmd))
    app.add_handler(
        MessageHandler(filters.Regex(AMAR_REGEX) & filters.ChatType.GROUPS, group_stats_cmd),
        group=17
    )
    print("OK module group_stats loaded")
