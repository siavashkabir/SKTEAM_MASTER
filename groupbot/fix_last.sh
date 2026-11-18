#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py
ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$AC" "$AC.bak_last_$TS"
cp "$ST" "$ST.bak_last_$TS"
echo "✅ بک‌آپ گرفته شد"

source venv/bin/activate

# ۱. fix default = False
python3 << 'PYEOF'
AC = "/data/data/com.termux/files/home/groupbot/modules/access.py"
with open(AC, "r", encoding="utf-8") as f:
    lines = f.readlines()

# توی case admin، perms.get(key, True) → False
count = 0
for i, line in enumerate(lines):
    if 'en = perms.get(key, True)' in line:
        lines[i] = line.replace('perms.get(key, True)', 'perms.get(key, False)')
        count += 1
        print(f"✅ خط {i+1}: default → False")

with open(AC, "w", encoding="utf-8") as f:
    f.writelines(lines)

print(f"✅ {count} خط اصلاح شد")
PYEOF

echo ""

# ۲. fix پیکربندی — چک کد
echo "─── چک کد پیکربندی ───"
grep -n "admin_list_menu\|get_group_admins" "$ST" | head -10
echo ""

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"
with open(ST, "r", encoding="utf-8") as f:
    content = f.read()

# کد: چک کن get_group_admins صدا زده می‌شه یا get_chat_administrators
if "get_group_admins" in content:
    print("✅ get_group_admins توی start.py هست")
else:
    print("⚠️ get_group_admins نیست")
    
if "get_chat_administrators" in content:
    print("⚠️ get_chat_administrators هم هست (از تلگرام می‌خونه)")

PYEOF

echo ""

if python3 -m py_compile "$AC" 2>&1 && python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$AC.bak_last_$TS" "$AC"
    cp "$ST.bak_last_$TS" "$ST"
    exit 1
fi
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
