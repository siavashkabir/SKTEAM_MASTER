#!/data/data/com.termux/files/usr/bin/bash

AD=modules/admin.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$AD" "$AD.bak_load3_$TS"
echo "✅ بک‌آپ: $AD.bak_load3_$TS"

source venv/bin/activate

python3 << 'PYEOF'
AD = "/data/data/com.termux/files/home/groupbot/modules/admin.py"

with open(AD, "r", encoding="utf-8") as f:
    lines = f.readlines()

# پیدا کردن خط شروع PROMOTE_WAIT[user.id] = {
start = -1
for i, line in enumerate(lines):
    if 'PROMOTE_WAIT[user.id] = {' in line:
        start = i
        break

if start == -1:
    print("❌ PROMOTE_WAIT[user.id] پیدا نشد")
    exit(1)

print(f"✅ شروع: خط {start + 1}")

# شمارش براکت‌ها تا بسته شدن
depth = 0
end = -1
for i in range(start, len(lines)):
    depth += lines[i].count('{')
    depth -= lines[i].count('}')
    if depth == 0 and i > start:
        end = i
        break

if end == -1:
    print("❌ انتهای بلاک پیدا نشد")
    exit(1)

print(f"✅ پایان: خط {end + 1}")

# indent
indent = lines[start][:len(lines[start]) - len(lines[start].lstrip())]
print(f"indent: {len(indent)} فاصله")

# کد جدید
new_block = [
    indent + "# ★ خوندن perms از دیتابیس\n",
    indent + "_TG2BOT = {\n",
    indent + '    "can_delete_messages": "purge",\n',
    indent + '    "can_restrict_members": "ban",\n',
    indent + '    "can_pin_messages": "pin",\n',
    indent + '    "can_invite_users": "admin_add",\n',
    indent + '    "can_manage_video_chats": "vcall",\n',
    indent + '    "can_change_info": "group_info",\n',
    indent + "}\n",
    indent + "_loaded = {}\n",
    indent + "try:\n",
    indent + "    from database import get_all_perms\n",
    indent + "    _saved = get_all_perms(chat.id, target)\n",
    indent + '    print(f"[PROMOTE LOAD] saved = {_saved}")\n',
    indent + "    for _tg, _bot in _TG2BOT.items():\n",
    indent + '        _loaded[_tg] = bool(_saved.get(_bot, _saved.get(_tg, False)))\n',
    indent + "except Exception as _e:\n",
    indent + '    print(f"[PROMOTE LOAD ERR] {_e}")\n',
    indent + "    _loaded = {k: False for k in _TG2BOT.keys()}\n",
    "\n",
    indent + "PROMOTE_WAIT[user.id] = {\n",
    indent + '    "chat_id": chat.id,\n',
    indent + '    "target_id": target,\n',
    indent + '    "target_name": target_name or "?",\n',
    indent + '    "perms": _loaded\n',
    indent + "}\n",
]

new_lines = lines[:start] + new_block + lines[end + 1:]

with open(AD, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("✅ PROMOTE_WAIT جایگزین شد")
PYEOF

echo ""

if python3 -m py_compile "$AD" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$AD.bak_load3_$TS" "$AD"
    exit 1
fi
echo ""

echo "─── چک ───"
grep -n "PROMOTE LOAD" "$AD"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
