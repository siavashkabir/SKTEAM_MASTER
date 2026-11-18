#!/data/data/com.termux/files/usr/bin/bash

BK=~/groupbot_backups/reset_admins_$(date +%Y%m%d_%H%M%S)
mkdir -p "$BK"

cp data/groupbot.db "$BK/groupbot.db.bak"
echo "✅ بک‌آپ: $BK/groupbot.db.bak"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
import sqlite3
from config import DATABASE_PATH

conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()

# نمایش قبل
print("─── قبل ───")
c.execute("SELECT chat_id, user_id, name FROM group_admins")
print("group_admins:")
for r in c.fetchall(): print(f"  {r}")
c.execute("SELECT COUNT(*) FROM admin_permissions")
print(f"admin_permissions: {c.fetchone()[0]} ردیف")
print()

# ★ پاک کردن همه
c.execute("DELETE FROM group_admins")
print(f"✅ {c.rowcount} ادمین پاک شد")

c.execute("DELETE FROM admin_permissions")
print(f"✅ {c.rowcount} perm پاک شد")

# ★ ولی مالکین گروه رو از تلگرام نگه دار
# (اون‌ها جدا هستن و به is_group_owner کار دارن)

conn.commit()
conn.close()

print()
print("✅ پاکسازی کامل")
print()
print("🎯 حالا برو تلگرام:")
print("1. «افزودن مدیر» روی هر کی می‌خوای ادمین ربات باشه")
print("2. تیک‌هاش رو بزن، تایید")
print("3. این‌طوری فقط اونایی که تو می‌خوای ادمین می‌شن")
PYEOF

echo ""
echo "═══════════════════════════════════════════════════"
echo "✅ تمام"
echo ""
echo "🎯 حالا برو تلگرام:"
echo "1. «افزودن مدیر» روی Sk.team video player"
echo "2. تیک‌های دلخواه، تایید"
echo "3. همین‌طور برای بقیه"
echo ""
echo "«پیکربندی» → فقط اونایی که تو اضافه کردی رو نشون می‌ده"
echo "═══════════════════════════════════════════════════"
