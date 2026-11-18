#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$AC" "$AC.bak_phase1_2_$TS"
echo "✅ بک‌آپ: $AC.bak_phase1_2_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
import re

AC = "/data/data/com.termux/files/home/groupbot/modules/access.py"

with open(AC, "r", encoding="utf-8") as f:
    content = f.read()

# ═══ ۱. VIP_PERMS جدید ═══
new_vip = '''VIP_PERMS = [
    ("gif", "🎞️ ارسال گیف"),
    ("sticker", "🎨 ارسال استیکر"),
    ("photo", "🖼️ ارسال عکس"),
    ("link", "🔗 ارسال لینک"),
    ("forward", "📎 فوروارد"),
    ("mention", "📣 منشن کردن"),
    ("vcall", "🎤 مدیریت ویس کال"),
]'''

if re.search(r'VIP_PERMS\s*=\s*\[', content):
    content = re.sub(r'VIP_PERMS\s*=\s*\[.*?\]', new_vip, content, count=1, flags=re.DOTALL)
    print("✅ VIP_PERMS عوض شد")

# ═══ ۲. ADMIN_PERMS جدید ═══
new_admin = '''ADMIN_PERMS = [
    ("panel", "🔓 باز کردن پنل ربات"),
    ("vip", "👑 VIP دادن"),
    ("tag", "📢 تگ کردن"),
    ("purge", "🗑️ پاکسازی"),
    ("link", "🔗 لینک گروه"),
    ("pin", "📌 پین کردن"),
    ("ban", "🚫 بن کردن"),
    ("mute", "🔇 سکوت کردن"),
    ("vcall", "🎤 مدیریت ویس کال"),
    ("special", "⭐ تنظیم ویژه"),
    ("stats_call", "📞 آمار کال"),
    ("stats_chat", "💬 آمار چت روزانه"),
]'''

if re.search(r'ADMIN_PERMS\s*=\s*\[', content):
    content = re.sub(r'ADMIN_PERMS\s*=\s*\[.*?\]', new_admin, content, count=1, flags=re.DOTALL)
    print("✅ ADMIN_PERMS عوض شد")

# ═══ ۳. DEPUTY_PERMS جدید ═══
new_deputy = '''DEPUTY_PERMS = [
    ("panel", "🔓 باز کردن پنل ربات"),
    ("vip", "👑 VIP دادن"),
    ("tag", "📢 تگ کردن"),
    ("purge", "🗑️ پاکسازی"),
    ("link", "🔗 لینک گروه"),
    ("pin", "📌 پین کردن"),
    ("ban", "🚫 بن کردن"),
    ("mute", "🔇 سکوت کردن"),
    ("vcall", "🎤 مدیریت ویس کال"),
    ("special", "⭐ تنظیم ویژه"),
    ("stats_call", "📞 آمار کال"),
    ("stats_chat", "💬 آمار چت روزانه"),
    ("locks", "🔒 قفل ها"),
    ("welcome", "👋 خوش‌آمدگویی"),
    ("nsfw", "🔞 NSFW"),
    ("warn", "⚠️ سیستم اخطار"),
    ("config", "⚙️ پیکربندی"),
    ("admin_add", "👮 تعیین ادمین"),
    ("deputy_manage", "🧑‍💼 مدیریت معاون‌ها"),
    ("group_info", "✏️ تغییر اطلاعات گروه"),
    ("group_settings", "🎛️ تنظیمات گروه"),
    ("stats_full", "📊 آمار کل"),
]'''

if re.search(r'DEPUTY_PERMS\s*=\s*\[', content):
    content = re.sub(r'DEPUTY_PERMS\s*=\s*\[.*?\]', new_deputy, content, count=1, flags=re.DOTALL)
    print("✅ DEPUTY_PERMS عوض شد")

# ═══ ۴. build_access_menu جدید ═══
new_func = '''def build_access_menu(uid, chat_id, target_id, target_name, role, is_bot_owner_user=False):
    """ساخت منوی دسترسی بر اساس نقش کاربر"""
    # مالک/سودو ربات → پیام
    if role in ("bot_owner", "bot_admin"):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(role_emoji(role) + " " + role_label(role) + " (ربات)", callback_data="acc_noop:" + str(uid) + ":" + str(chat_id))],
            [InlineKeyboardButton("⚠️ مدیریت این بخش فقط توسط مالک ربات امکان‌پذیر است", callback_data="acc_noop:" + str(uid) + ":" + str(chat_id))],
            [InlineKeyboardButton("✅ تایید و بستن", callback_data="acc_confirm:" + str(uid) + ":" + str(chat_id) + ":" + str(target_id))],
        ])

    keyboard = []
    keyboard.append([InlineKeyboardButton(role_emoji(role) + " " + role_label(role), callback_data="acc_noop:" + str(uid) + ":" + str(chat_id))])
    keyboard.append([InlineKeyboardButton("───────────────", callback_data="acc_noop:" + str(uid) + ":" + str(chat_id))])

    # مالک گروه یا معاون → DEPUTY_PERMS
    if role in ("group_owner", "deputy"):
        perms = get_all_deputy_perms(chat_id)
        if not perms:
            perms = {k: True for k, _ in DEPUTY_PERMS}
        keyboard.append([InlineKeyboardButton("👤 مدیریت گروه / معاون", callback_data="acc_noop:" + str(uid) + ":" + str(chat_id))])
        for key, label in DEPUTY_PERMS:
            en = perms.get(key, True)
            mark = "[X]" if en else "[ ]"
            keyboard.append([InlineKeyboardButton(mark + " " + label, callback_data="acc_dp_" + key + ":" + str(uid) + ":" + str(chat_id) + ":" + str(target_id))])

    # VIP یا member → VIP_PERMS
    elif role in ("vip", "member"):
        perms = get_user_perms(chat_id, target_id)
        if not perms:
            perms = {k: True for k, _ in VIP_PERMS}
        keyboard.append([InlineKeyboardButton("👤 عضو ویژه / عادی", callback_data="acc_noop:" + str(uid) + ":" + str(chat_id))])
        for key, label in VIP_PERMS:
            en = perms.get(key, True)
            mark = "[X]" if en else "[ ]"
            keyboard.append([InlineKeyboardButton(mark + " " + label, callback_data="acc_vp_" + key + ":" + str(uid) + ":" + str(chat_id) + ":" + str(target_id))])

    keyboard.append([InlineKeyboardButton("✅ تایید و بستن", callback_data="acc_confirm:" + str(uid) + ":" + str(chat_id) + ":" + str(target_id))])
    return InlineKeyboardMarkup(keyboard)'''

pattern_func = r'def build_access_menu\(uid, chat_id, target_id, target_name, role, is_bot_owner_user=False\):.*?(?=\nasync def access_handler)'
if re.search(pattern_func, content, re.DOTALL):
    content = re.sub(pattern_func, new_func + "\n\n", content, count=1, flags=re.DOTALL)
    print("✅ build_access_menu عوض شد")
else:
    print("⚠️ build_access_menu پیدا نشد")

with open(AC, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$AC" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$AC.bak_phase1_2_$TS" "$AC"
    exit 1
fi
echo ""

echo "─── چک ───"
echo "VIP_PERMS: $(grep -A 2 'VIP_PERMS = \[' "$AC" | head -3 | tail -1)"
echo "ADMIN_PERMS: $(grep -A 2 'ADMIN_PERMS = \[' "$AC" | head -3 | tail -1)"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ فاز ۱.۲ انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
