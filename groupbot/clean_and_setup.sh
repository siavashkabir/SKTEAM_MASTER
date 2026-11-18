#!/data/data/com.termux/files/usr/bin/bash

BK=~/groupbot_backups/perms_setup_$(date +%Y%m%d_%H%M%S)
mkdir -p "$BK"

echo "═══════════════════════════════════════════════════"
echo "🧹 پاکسازی + پیش‌فرض ادمین‌ها"
echo "═══════════════════════════════════════════════════"
echo ""

cp data/groupbot.db "$BK/groupbot.db.bak"
echo "✅ بک‌آپ: $BK/groupbot.db.bak"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
import sqlite3
from config import DATABASE_PATH

conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()

# ۱. نمایش وضعیت قبل
print("─── قبل ───")
c.execute("SELECT COUNT(*) FROM admin_permissions")
print(f"کل ردیف‌ها: {c.fetchone()[0]}")
print()

# ۲. پاک کردن همه
c.execute("DELETE FROM admin_permissions")
print(f"✅ {c.rowcount} ردیف پاک شد")
print()

# ۳. گرفتن همه ادمین‌های فعلی
c.execute("SELECT chat_id, user_id, name FROM group_admins")
admins = c.fetchall()
print(f"✅ {len(admins)} ادمین:")
for a in admins:
    print(f"   chat={a[0]}, user={a[1]}, name={a[2]}")
print()

# ۴. perms پیش‌فرض
default_perms = {
    "panel": 1,        # باز کردن پنل
    "vip": 1,          # VIP دادن
    "tag": 1,          # تگ کردن
    "link": 1,         # لینک گروه
    "pin": 1,          # پین کردن
    "mute": 1,         # سکوت (ادمین می‌تونه آنمیوت کنه)
    "purge": 0,        # پاکسازی - غیرفعال
    "ban": 0,          # بن - غیرفعال
    "vcall": 0,        # مدیریت ویس کال - غیرفعال
    "special": 0,      # تنظیم ویژه - غیرفعال
    "stats_call": 0,   # آمار کال - غیرفعال
    "stats_chat": 0,   # آمار چت - غیرفعال
}

# ۵. اضافه کردن برای هر ادمین
print("─── ذخیره perms پیش‌فرض ───")
for chat_id, user_id, name in admins:
    for perm, val in default_perms.items():
        c.execute(
            "INSERT OR REPLACE INTO admin_permissions (chat_id, user_id, role, perm_name, enabled) VALUES (?, ?, ?, ?, ?)",
            (chat_id, user_id, "admin", perm, val)
        )
    print(f"✅ {name} ({user_id}): {len(default_perms)} perm")

conn.commit()

# ۶. نمایش وضعیت بعد
print()
print("─── بعد ───")
c.execute("SELECT COUNT(*) FROM admin_permissions")
print(f"کل ردیف‌ها: {c.fetchone()[0]}")
print()

c.execute("SELECT user_id, perm_name, enabled FROM admin_permissions WHERE chat_id=-1004349813270 ORDER BY user_id, perm_name LIMIT 40")
print("نمونه (40 ردیف اول):")
for r in c.fetchall():
    mark = "✅" if r[2] else "❌"
    print(f"  {mark} user={r[0]} {r[1]}")

conn.close()
print()
print("✅ پاکسازی و پیش‌فرض انجام شد")
PYEOF

echo ""
echo "═══════════════════════════════════════════════════"
echo "✅ تمام"
echo ""
echo "🎯 حالا:"
echo "1. ری‌استارت:"
echo "   pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo ""
echo "2. برو تلگرام:"
echo "   - «دسترسی» روی کاربر ادمین → باید 6 تا ✅ داشته باشه"
echo "   - «پیکربندی» → باید هر 3 ادمین رو نشون بده"
echo "═══════════════════════════════════════════════════"
