#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$AC" "$AC.bak_roleadmin_$TS"
echo "✅ بک‌آپ: $AC.bak_roleadmin_$TS"

source venv/bin/activate

python3 << 'PYEOF'
AC = "/data/data/com.termux/files/home/groupbot/modules/access.py"

with open(AC, "r", encoding="utf-8") as f:
    lines = f.readlines()

# پیدا کردن خط is_deputy توی get_target_role
target_idx = -1
for i, line in enumerate(lines):
    if 'if is_deputy(chat_id, user_id):' in line:
        target_idx = i
        break

if target_idx == -1:
    print("❌ is_deputy توی get_target_role پیدا نشد")
    exit(1)

print(f"✅ is_deputy: خط {target_idx + 1}")

# indent
indent = lines[target_idx][:len(lines[target_idx]) - len(lines[target_idx].lstrip())]
print(f"indent: {len(indent)} فاصله")

# اضافه کردن is_admin قبل از is_deputy
new_lines = [
    indent + "# ★ چک ادمین (قبل از معاون)\n",
    indent + "if is_admin(chat_id, user_id):\n",
    indent + '    return "admin"\n',
]

lines = lines[:target_idx] + new_lines + lines[target_idx:]

with open(AC, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("✅ is_admin check اضافه شد")
PYEOF

echo ""

if python3 -m py_compile "$AC" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$AC.bak_roleadmin_$TS" "$AC"
    exit 1
fi
echo ""

# تست
echo "─── تست ───"
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
from modules.access import get_target_role
chat_id = -1004349813270
for uid in [8401175719, 8250087472, 8820561431, 7955185125]:
    print(f"  {uid}: {get_target_role(chat_id, uid)}")
PYEOF
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
