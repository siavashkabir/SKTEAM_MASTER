#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$AC" "$AC.bak_roles_$TS"
echo "✅ بک‌آپ: $AC.bak_roles_$TS"

source venv/bin/activate

python3 << 'PYEOF'
AC = "/data/data/com.termux/files/home/groupbot/modules/access.py"

with open(AC, "r", encoding="utf-8") as f:
    lines = f.readlines()

in_label = False
in_emoji = False
label_added = False
emoji_added = False

for i, line in enumerate(lines):
    if 'def role_label' in line:
        in_label = True
        continue
    if 'def role_emoji' in line:
        in_label = False
        in_emoji = True
        continue
    if line.startswith('def ') and in_emoji and 'role_emoji' not in line:
        in_emoji = False
    
    if in_label and '"group_owner": "مالک گروه",' in line and not label_added:
        lines.insert(i+1, '        "admin": "مدیر گروه",\n')
        label_added = True
        print(f"✅ role_label admin: خط {i+2}")
        continue
    
    if in_emoji and '"group_owner": "🏆",' in line and not emoji_added:
        lines.insert(i+1, '        "admin": "🛡️",\n')
        emoji_added = True
        print(f"✅ role_emoji admin: خط {i+2}")
        continue

with open(AC, "w", encoding="utf-8") as f:
    f.writelines(lines)

if not label_added:
    print("⚠️ role_label admin اضافه نشد")
if not emoji_added:
    print("⚠️ role_emoji admin اضافه نشد")
PYEOF

echo ""

if python3 -m py_compile "$AC" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$AC.bak_roles_$TS" "$AC"
    exit 1
fi
echo ""

echo "─── چک ───"
grep -n '"admin": "مدیر گروه"\|"admin": "🛡️"' "$AC"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
