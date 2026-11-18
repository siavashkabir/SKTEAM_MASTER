#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_impfinal_$TS"
echo "✅ بک‌آپ: $ST.bak_impfinal_$TS"

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    content = f.read()

# fix همه جا
old1 = "from database import get_group_admins, admin_list_menu"
new1 = "from database import get_group_admins\n        from modules.admin_perms import admin_list_menu"

count1 = content.count(old1)
if count1 > 0:
    content = content.replace(old1, new1)
    print(f"✅ Import جدا شد ({count1} جا)")

# fix دوم — اگه با indent متفاوت باشه
old2 = "        from database import get_group_admins, admin_list_menu"
new2 = "        from database import get_group_admins\n        from modules.admin_perms import admin_list_menu"

count2 = content.count(old2)
if count2 > 0:
    content = content.replace(old2, new2)
    print(f"✅ Import با indent جدا شد ({count2} جا)")

with open(ST, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_impfinal_$TS" "$ST"
    exit 1
fi
echo ""

echo "─── چک ───"
grep -n "from database import get_group_admins\|from modules.admin_perms import admin_list_menu" "$ST"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
