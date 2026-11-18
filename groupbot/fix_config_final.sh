#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_cfgfinal_$TS"
echo "✅ بک‌آپ: $ST.bak_cfgfinal_$TS"

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    lines = f.readlines()

# پیدا کردن خط `admins = await context.bot.get_chat_administrators(chat.id)`
target = -1
for i, line in enumerate(lines):
    if 'admins = await context.bot.get_chat_administrators(chat.id)' in line:
        target = i
        break

if target == -1:
    print("❌ پیدا نشد")
    exit(1)

print(f"✅ خط {target + 1}")

# indent
indent = lines[target][:len(lines[target]) - len(lines[target].lstrip())]

# جایگزین کردن با کد جدید — ادغام تلگرام + دیتابیس
new_lines = [
    indent + "# ★ از دیتابیس هم بخون\n",
    indent + "from database import get_group_admins\n",
    indent + "_db_admins = get_group_admins(chat.id)\n",
    indent + "print(f\"[CFG DBG] tg_admins={len(admins)}, db_admins={len(_db_admins)}\")\n",
    indent + "print(f\"[CFG DBG] db_admins data: {_db_admins}\")\n",
    "\n",
]

# پیدا کردن خط owners =
owners_idx = -1
for j in range(target, target + 5):
    if 'owners =' in lines[j]:
        owners_idx = j
        break

if owners_idx == -1:
    print("⚠️ owners پیدا نشد — فقط بعد از admins اضافه می‌کنم")
    lines = lines[:target + 1] + new_lines + lines[target + 1:]
else:
    print(f"✅ owners خط {owners_idx + 1}")
    # بین admins و owners، کد جدید رو بذار
    lines = lines[:target + 1] + new_lines + lines[target + 1:]

with open(ST, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("✅ debug اضافه شد")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_cfgfinal_$TS" "$ST"
    exit 1
fi
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Debug اضافه شد — حالا باید ببینیم چی می‌شه"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo ""
echo "بعد توی تلگرام «پیکربندی» بزن"
echo "بعد این رو بزن:"
echo "tail -n 50 ~/groupbot_bot.log | grep 'CFG DBG'"
echo "═══════════════════════════════════════════════════"
