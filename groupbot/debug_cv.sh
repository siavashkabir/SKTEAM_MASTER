#!/data/data/com.termux/files/usr/bin/bash

AP=modules/admin_perms.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$AP" "$AP.bak_dbgcv_$TS"
echo "✅ بک‌آپ: $AP.bak_dbgcv_$TS"

source venv/bin/activate

python3 << 'PYEOF'
AP = "/data/data/com.termux/files/home/groupbot/modules/admin_perms.py"

with open(AP, "r", encoding="utf-8") as f:
    lines = f.readlines()

# پیدا کردن def admin_list_menu
target = -1
for i, line in enumerate(lines):
    if 'def admin_list_menu' in line:
        target = i
        break

if target == -1:
    print("❌ پیدا نشد")
    exit(1)

# اضافه کردن print بعد از خط def
indent = lines[target + 1][:len(lines[target + 1]) - len(lines[target + 1].lstrip())]

debug_lines = [
    indent + 'print(f"[ADMIN_LIST DBG] uid={uid}, chat_id={chat_id}, admins_count={len(admins)}")\n',
    indent + 'print(f"[ADMIN_LIST DBG] admins={admins}")\n',
]

lines = lines[:target + 1] + debug_lines + lines[target + 1:]

with open(AP, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("✅ debug اضافه شد")
PYEOF

echo ""

if python3 -m py_compile "$AP" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$AP.bak_dbgcv_$TS" "$AP"
    exit 1
fi
echo ""

echo "═══════════════════════════════════════════════════"
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo ""
echo "بعد توی تلگرام:"
echo "  1. «پیکربندی» بزن"
echo ""
echo "بعد این رو بزن و بفرست:"
echo "  tail -n 30 ~/groupbot_bot.log | grep ADMIN_LIST"
echo "═══════════════════════════════════════════════════"
