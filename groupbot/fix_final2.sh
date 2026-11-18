#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py
AP=modules/admin_perms.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$AC" "$AC.bak_f2_$TS"
cp "$AP" "$AP.bak_f2_$TS"
echo "✅ بک‌آپ گرفته شد"

source venv/bin/activate

# ═══ fix 1: role_label و role_emoji ═══
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
    if line.startswith('def ') and in_emoji:
        in_emoji = False
    
    # اضافه کردن admin به role_label
    if in_label and '"group_owner": "مالک گروه",' in line and not label_added:
        lines.insert(i+1, '        "admin": "مدیر گروه",\n')
        label_added = True
        print(f"✅ role_label admin: خط {i+2}")
        continue
    
    # اضافه کردن admin به role_emoji
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

# ═══ fix 2: پیکربندی از دیتابیس ═══
python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    content = f.read()

# همه جاهایی که get_group_admins_list صدا زده می‌شه رو با get_group_admins عوض کن
if "get_group_admins_list" in content:
    content = content.replace(
        "from modules.admin_perms import get_group_admins_list",
        "from database import get_group_admins"
    )
    content = content.replace(
        "get_group_admins_list(",
        "get_group_admins("
    )
    with open(ST, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ پیکربندی از دیتابیس")
else:
    print("⚠️ get_group_admins_list پیدا نشد")

PYEOF

echo ""

# کامپایل
if python3 -m py_compile "$AC" 2>&1 && python3 -m py_compile "$AP" 2>&1 && python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$AC.bak_f2_$TS" "$AC"
    cp "$AP.bak_f2_$TS" "$AP"
    cp "$ST.bak_f2_$TS" "$ST"
    exit 1
fi
echo ""

echo "─── چک ───"
grep -n '"admin": "مدیر گروه"\|"admin": "🛡️"' "$AC"
echo ""
grep -n "get_group_admins" "$ST" | head -3
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
