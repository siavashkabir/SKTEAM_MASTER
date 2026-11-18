#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_cfgreal_$TS"
echo "✅ بک‌آپ: $ST.bak_cfgreal_$TS"

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    lines = f.readlines()

# پیدا کردن خط `admins = await context.bot.get_chat_administrators(chat.id)`
start = -1
for i, line in enumerate(lines):
    if 'admins = await context.bot.get_chat_administrators(chat.id)' in line:
        start = i
        break

if start == -1:
    print("❌ پیدا نشد")
    exit(1)

print(f"✅ خط شروع: {start + 1}")

# پیدا کردن `details = NL.join(lines)` بعدش
end = -1
for i in range(start, start + 30):
    if 'details = NL.join(lines)' in lines[i] or 'NL.join(lines)' in lines[i]:
        end = i
        break

if end == -1:
    print("❌ پایان پیدا نشد")
    exit(1)

print(f"✅ خط پایان: {end + 1}")

# indent
indent = lines[start][:len(lines[start]) - len(lines[start].lstrip())]

# کد جدید
new_block = [
    indent + "# ★ از دیتابیس بخون (نه تلگرام)\n",
    indent + "from database import get_group_admins\n",
    indent + "_tg_admins = await context.bot.get_chat_administrators(chat.id)\n",
    indent + "_tg_ids = {a.user.id for a in _tg_admins}\n",
    indent + '_owner_ids = {a.user.id for a in _tg_admins if a.status == "creator"}\n',
    indent + "_db_admins = get_group_admins(chat.id)\n",
    indent + 'print(f"[CFG] db={len(_db_admins)}, tg={len(_tg_admins)}")\n',
    "\n",
    indent + "lines = []\n",
    indent + "for _a in _db_admins:\n",
    indent + '    _uid = _a.get("user_id")\n',
    indent + '    _name = _a.get("name") or "?"\n',
    indent + '    _role = "👑 مالک" if _uid in _owner_ids else "🛡️ ادمین"\n',
    indent + '    lines.append(f"• {_name} ({_role})")\n',
    "\n",
    indent + "_owner_count = len(_owner_ids)\n",
    indent + "_admin_count = len(_db_admins) - _owner_count\n",
]

# جایگزینی خطوط start تا end
new_lines = lines[:start] + new_block + lines[end + 1:]

with open(ST, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("✅ کد جایگزین شد")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_cfgreal_$TS" "$ST"
    exit 1
fi
echo ""

echo "═══ چک: خطوط جدید ═══"
LINE=$(grep -n "get_group_admins" "$ST" | head -1 | cut -d: -f1)
if [ -n "$LINE" ]; then
    sed -n "$((LINE-3)),$((LINE+15))p" "$ST"
fi
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
