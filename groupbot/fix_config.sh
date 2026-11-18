#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_cfg_$TS"
echo "✅ بک‌آپ: $ST.bak_cfg_$TS"

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    content = f.read()

# تغییر get_group_admins_list به get_group_admins
if "get_group_admins_list" in content:
    # اول import
    content = content.replace(
        "from modules.admin_perms import get_group_admins_list",
        "from database import get_group_admins"
    )
    # بعد صدا زدن
    content = content.replace(
        "get_group_admins_list(",
        "get_group_admins("
    )
    print("✅ get_group_admins_list → get_group_admins")
else:
    print("⚠️ get_group_admins_list پیدا نشد")

with open(ST, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

# کامپایل
if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_cfg_$TS" "$ST"
    exit 1
fi
echo ""

# چک نهایی
echo "─── چک ───"
grep -n "get_group_admins" "$ST" | head -5
echo ""

# تست
echo "─── تست ───"
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
from database import get_group_admins
admins = get_group_admins(-1004349813270)
print(f"✅ تعداد ادمین‌ها از دیتابیس: {len(admins)}")
for a in admins:
    print(f"  • {a.get('name')} (id={a.get('user_id')})")
PYEOF
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
