from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import is_sub_active, get_sub_days_remaining, get_vcall_interval
import sqlite3
from config import DATABASE_PATH
from datetime import datetime


def sub_status_menu(uid, chat_id=0):
    try:
        from modules.pv_main import PRICES, NAMES
    except Exception:
        PRICES = {}
        NAMES = {}
    group_active = False
    group_days = 0
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cur = conn.cursor()
        cur.execute("SELECT expire_date, activated FROM groups WHERE chat_id=?", (chat_id,))
        row = cur.fetchone()
        conn.close()
        if row and row[1]:
            try:
                exp = datetime.strptime(row[0], "%Y-%m-%d %H:%M")
                delta = exp - datetime.now()
                group_days = max(0, delta.days)
                group_active = group_days > 0
            except Exception:
                group_active = True
    except Exception as e:
        print("[SUB GROUP ERR] " + str(e))
    t = "💳 اشتراک‌های من" + chr(10) + "━━━━━━━━━━━━━━━━" + chr(10) + chr(10)
    kb = []
    if group_active:
        t += "🤖 اشتراک مدیریت گروه: ✅ " + str(group_days) + " روز مونده" + chr(10)
        kb.append([InlineKeyboardButton("🔄 تمدید مدیریت گروه", callback_data="ord_cat_manager:" + str(uid) + ":" + str(chat_id))])
    else:
        t += "🤖 اشتراک مدیریت گروه: ❌ غیرفعال" + chr(10)
        kb.append([InlineKeyboardButton("🛒 سفارش مدیریت گروه", callback_data="ord_cat_manager:" + str(uid) + ":" + str(chat_id))])
    items = [('nsfw', '🔞 اشتراک NSFW'), ('vcall', '🎙️ اشتراک ضبط ویس‌کال'), ('music', '🎵 اشتراک موزیک')]
    for k, lbl in items:
        if is_sub_active(chat_id, k):
            days = get_sub_days_remaining(chat_id, k)
            t += lbl + ": ✅ " + str(days) + " روز مونده" + chr(10)
            kb.append([InlineKeyboardButton("🔄 تمدید " + lbl, callback_data="ord_cat_" + k + ":" + str(uid) + ":" + str(chat_id))])
        else:
            t += lbl + ": ❌ غیرفعال" + chr(10)
            kb.append([InlineKeyboardButton("🛒 سفارش " + lbl, callback_data="ord_cat_" + k + ":" + str(uid) + ":" + str(chat_id))])
    t += chr(10) + "━━━━━━━━━━━━━━━━" + chr(10)
    t += "💰 تعرفه سالانه:" + chr(10)
    for k in ['manager', 'nsfw', 'vcall', 'music']:
        nm = NAMES.get(k, k)
        if k in PRICES:
            for lbl, pr in PRICES[k]:
                if "۱ ساله" in lbl:
                    t += "• " + nm + " → " + pr + " تومان" + chr(10)
                    break
    t += chr(10) + "💡 تمدید به تاریخ فعلی اضافه می‌شود." + chr(10)
    t += chr(10) + "👤 پشتیبانی: @Siavashska"
    kb.append([InlineKeyboardButton("🔙 بازگشت", callback_data="op_back:" + str(uid) + ":" + str(chat_id))])
    kb.append([InlineKeyboardButton("❌ بستن", callback_data="menu_close:" + str(uid))])
    return t, InlineKeyboardMarkup(kb)


def vcall_sub_menu(uid, chat_id=0):
    if is_sub_active(chat_id, 'vcall'):
        days = get_sub_days_remaining(chat_id, 'vcall')
        cur = get_vcall_interval(chat_id)
        ints = [(1,"۱ دقیقه"),(3,"۳ دقیقه"),(5,"۵ دقیقه"),(10,"۱۰ دقیقه"),(15,"۱۵ دقیقه"),(20,"۲۰ دقیقه"),(30,"۳۰ دقیقه"),(60,"۱ ساعت")]
        t = "🎙️ اشتراک ضبط ویس‌کال" + chr(10) + "━━━━━━━━━━━━━━━━" + chr(10)
        t += "وضعیت: ✅ فعال" + chr(10) + "تاریخ انقضا: " + str(days) + " روز مونده" + chr(10) + chr(10)
        t += "⏱️ بازه ضبط خودکار:" + chr(10)
        for m, l in ints:
            t += "○ " + l + (" ✅" if m == cur else "") + chr(10)
        btns = []
        row = []
        for m, l in ints:
            row.append(InlineKeyboardButton(l, callback_data="vcall_interval_" + str(m) + ":" + str(uid) + ":" + str(chat_id)))
            if len(row) == 2:
                btns.append(row)
                row = []
        if row:
            btns.append(row)
        btns.append([InlineKeyboardButton("🔙 بازگشت", callback_data="sub_status:" + str(uid) + ":" + str(chat_id))])
        btns.append([InlineKeyboardButton("❌ بستن", callback_data="menu_close:" + str(uid))])
        return t, InlineKeyboardMarkup(btns)
    else:
        t = "🎙️ اشتراک ضبط ویس‌کال" + chr(10) + "━━━━━━━━━━━━━━━━" + chr(10)
        t += "وضعیت: ❌ غیرفعال" + chr(10) + chr(10)
        t += "برای فعال‌سازی با پشتیبانی تماس بگیرید:" + chr(10) + "👤 @Siavashska"
        return t, InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 بازگشت", callback_data="sub_status:" + str(uid) + ":" + str(chat_id))],
        ])


def music_sub_menu(uid, chat_id=0):
    if is_sub_active(chat_id, 'music'):
        days = get_sub_days_remaining(chat_id, 'music')
        t = "🎵 اشتراک موزیک" + chr(10) + "━━━━━━━━━━━━━━━━" + chr(10)
        t += "وضعیت: ✅ فعال" + chr(10) + "تاریخ انقضا: " + str(days) + " روز مونده" + chr(10) + chr(10)
        t += "برای تنظیمات پخش، از پنل موزیک استفاده کنید."
    else:
        t = "🎵 اشتراک موزیک" + chr(10) + "━━━━━━━━━━━━━━━━" + chr(10)
        t += "وضعیت: ❌ غیرفعال" + chr(10) + chr(10)
        t += "برای فعال‌سازی با پشتیبانی تماس بگیرید:" + chr(10) + "👤 @Siavashska"
    return t, InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 بازگشت", callback_data="sub_status:" + str(uid) + ":" + str(chat_id))],
    ])


def sub_manage_menu(uid, chat_id=0):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 مدیریت گروه", callback_data="osub_manager:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🔞 مدیریت NSFW", callback_data="osub_nsfw:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("📞 مدیریت ویس‌کال", callback_data="osub_vcall:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🎵 مدیریت موزیک", callback_data="osub_music:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("✏️ تنظیم قیمت‌ها", callback_data="sub_pedit:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="op_back:" + str(uid) + ":" + str(chat_id))],
    ])


def _fmt_price(p):
    s = str(p).replace(",", "").replace("،", "").strip()
    try:
        return "{:,}".format(int(s))
    except Exception:
        return str(p)


def price_cats_menu(uid, chat_id=0):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 مدیر گروه", callback_data="sub_pcat_manager:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🔞 NSFW", callback_data="sub_pcat_nsfw:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🎵 موزیک", callback_data="sub_pcat_music:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("📞 ویس‌کال", callback_data="sub_pcat_vcall:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="sub_manage:" + str(uid) + ":" + str(chat_id))],
    ])


def price_plans_menu(uid, chat_id=0, cat="manager"):
    try:
        from modules.pv_main import PRICES
        plans = PRICES.get(cat, [])
    except Exception:
        plans = []
    btns = []
    for i, item in enumerate(plans):
        try:
            label, price = item
        except Exception:
            continue
        btn_text = label + " | " + _fmt_price(price) + " تومان"
        btns.append([InlineKeyboardButton(btn_text, callback_data="sub_pset_" + cat + "_" + str(i) + ":" + str(uid) + ":" + str(chat_id))])
    btns.append([InlineKeyboardButton("🔙 بازگشت", callback_data="sub_pedit:" + str(uid) + ":" + str(chat_id))])
    return InlineKeyboardMarkup(btns)


def build_vcall_sub_menu(uid, chat_id=0):
    """منوی اشتراک ویس‌کال (پنل سازنده)"""
    from database import get_subscription
    sub = get_subscription(chat_id, "vcall")
    active = False
    remaining = 0
    sub_info = "❌ فعال نیست"
    if sub:
        exp_str, enabled, _ = sub
        if enabled and exp_str:
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
                try:
                    exp = datetime.strptime(exp_str, fmt)
                    if exp > datetime.now():
                        active = True
                        remaining = (exp - datetime.now()).days
                        sub_info = "✅ فعال — " + str(remaining) + " روز باقی‌مانده"
                    else:
                        sub_info = "❌ منقضی شده"
                    break
                except Exception:
                    continue
    keyboard = [
        [InlineKeyboardButton("📊 وضعیت: " + sub_info, callback_data="vsub_noop:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🔓 فعال/غیرفعال", callback_data="vsub_toggle:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("📅 تمدید 30 روز", callback_data="vsub_30:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("📅 تمدید 90 روز", callback_data="vsub_90:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("📅 تمدید 180 روز", callback_data="vsub_180:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("📅 تمدید 365 روز (1 سال)", callback_data="vsub_365:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="sub_manage:" + str(uid) + ":" + str(chat_id))],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_music_sub_menu(uid, chat_id=0):
    """منوی اشتراک موزیک (پنل سازنده)"""
    from database import get_subscription
    sub = get_subscription(chat_id, "music")
    active = False
    remaining = 0
    sub_info = "❌ فعال نیست"
    if sub:
        exp_str, enabled, _ = sub
        if enabled and exp_str:
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
                try:
                    exp = datetime.strptime(exp_str, fmt)
                    if exp > datetime.now():
                        active = True
                        remaining = (exp - datetime.now()).days
                        sub_info = "✅ فعال — " + str(remaining) + " روز باقی‌مانده"
                    else:
                        sub_info = "❌ منقضی شده"
                    break
                except Exception:
                    continue
    keyboard = [
        [InlineKeyboardButton("📊 وضعیت: " + sub_info, callback_data="msub_noop:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🔓 فعال/غیرفعال", callback_data="msub_toggle:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("📅 تمدید 30 روز", callback_data="msub_30:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("📅 تمدید 90 روز", callback_data="msub_90:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("📅 تمدید 180 روز", callback_data="msub_180:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("📅 تمدید 365 روز (1 سال)", callback_data="msub_365:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="sub_manage:" + str(uid) + ":" + str(chat_id))],
    ]
    return InlineKeyboardMarkup(keyboard)
