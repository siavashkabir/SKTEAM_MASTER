#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_botself_$TS"
echo "✅ بک‌آپ: $ST.bak_botself_$TS"

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    lines = f.readlines()

# پیدا کردن خط `_members_info = {}`
target = -1
for i, line in enumerate(lines):
    if '_members_info = {}' in line:
        target = i
        break

if target == -1:
    print("❌ پیدا نشد")
    exit(1)

print(f"✅ خط {target + 1}")
indent = lines[target][:len(lines[target]) - len(lines[target].lstrip())]

# پیدا کردن خط `_owner_count = len(_owner_ids)`
end = -1
for i in range(target, target + 50):
    if '_owner_count = len(_owner_ids)' in lines[i]:
        end = i
        break

if end == -1:
    print("❌ انتها پیدا نشد")
    exit(1)

print(f"✅ انتها: خط {end + 1}")

# کد جدید
new_block = [
    indent + "# ★ اطلاعات اعضای گروه (از دیتابیس)\n",
    indent + "_members_info = {}\n",
    indent + "try:\n",
    indent + "    import sqlite3 as _sq\n",
    indent + "    from config import DATABASE_PATH as _DBP\n",
    indent + "    _conn = _sq.connect(_DBP)\n",
    indent + "    _cur = _conn.cursor()\n",
    indent + '    _cur.execute("SELECT user_id, first_name, username FROM members WHERE chat_id=?", (chat.id,))\n',
    indent + "    for _row in _cur.fetchall():\n",
    indent + '        _members_info[_row[0]] = {"first_name": _row[1], "username": _row[2]}\n',
    indent + "    _conn.close()\n",
    indent + "except Exception as _e:\n",
    indent + '    print(f"[CFG MEMBERS ERR] {_e}")\n',
    "\n",
    indent + "# ★ گرفتن آیدی خود ربات\n",
    indent + "_bot_id = context.bot.id\n",
    indent + '_bot_info = {"first_name": "🤖 ربات مدیریت گروه", "username": context.bot.username}\n',
    "\n",
    indent + "lines = []\n",
    "\n",
    indent + "# ★ اول مالک گروه\n",
    indent + "for _a in _db_admins:\n",
    indent + '    _uid = _a.get("user_id")\n',
    indent + "    if _uid not in _owner_ids:\n",
    indent + "        continue\n",
    indent + '    _info = _members_info.get(_uid, {})\n',
    indent + '    _fname = _info.get("first_name") or _a.get("name") or "?"\n',
    indent + '    _uname = _info.get("username")\n',
    indent + '    _uname_str = f" (@{_uname})" if _uname else ""\n',
    indent + '    lines.append(f"👑 {_fname}{_uname_str} — مالک")\n',
    "\n",
    indent + "# ★ بعد ربات (خودش)\n",
    indent + '_bot_uname = _bot_info.get("username")\n',
    indent + '_bot_uname_str = f" (@{_bot_uname})" if _bot_uname else ""\n',
    indent + 'lines.append(f"🤖 ربات مدیریت گروه{_bot_uname_str} — ادمین")\n',
    "\n",
    indent + "# ★ بعد بقیه ادمین‌ها (نه مالک، نه ربات)\n",
    indent + "for _a in _db_admins:\n",
    indent + '    _uid = _a.get("user_id")\n',
    indent + "    if _uid in _owner_ids or _uid == _bot_id:\n",
    indent + "        continue\n",
    indent + '    _info = _members_info.get(_uid, {})\n',
    indent + '    _fname = _info.get("first_name") or _a.get("name") or "?"\n',
    indent + '    _uname = _info.get("username")\n',
    indent + '    _uname_str = f" (@{_uname})" if _uname else ""\n',
    indent + '    lines.append(f"🛡️ {_fname}{_uname_str} — ادمین")\n',
    "\n",
    indent + "_owner_count = len(_owner_ids)\n",
    indent + "_admin_count = len(lines) - _owner_count\n",
    indent + 'details = NL.join(lines) if lines else "─ هیچ ادمینی ثبت نشده ─"\n',
]

new_lines = lines[:target] + new_block + lines[end + 1:]

with open(ST, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("✅ جایگزین شد")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_botself_$TS" "$ST"
    exit 1
fi
echo ""

echo "─── چک ───"
grep -n "_bot_id\|ربات مدیریت گروه" "$ST" | head -5
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo ""
echo "بعد توی تلگرام «پیکربندی» بزن"
echo "═══════════════════════════════════════════════════"
