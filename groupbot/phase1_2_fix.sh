#!/data/data/com.termux/files/usr/bin/bash

DB=database.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$DB" "$DB.bak_phase1_2_$TS"
echo "✅ بک‌آپ: $DB.bak_phase1_2_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
import re

DB = "/data/data/com.termux/files/home/groupbot/database.py"

with open(DB, "r", encoding="utf-8") as f:
    content = f.read()

# ═══ ۱. VIP_PERMS ═══
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
else:
    # اگه نبود، بعد از ADMIN_PERMS اضافه کن
    print("⚠️ VIP_PERMS پیدا نشد")

# ═══ ۲. ADMIN_PERMS ═══
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

# ═══ ۳. DEPUTY_PERMS ═══
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

with open(DB, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$DB" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$DB.bak_phase1_2_$TS" "$DB"
    exit 1
fi
echo ""

echo "─── چک ───"
echo "VIP_PERMS:"
grep -A 3 "^VIP_PERMS" "$DB" | head -4
echo ""
echo "ADMIN_PERMS:"
grep -A 3 "^ADMIN_PERMS" "$DB" | head -4
echo ""
echo "DEPUTY_PERMS:"
grep -A 3 "^DEPUTY_PERMS" "$DB" | head -4
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
