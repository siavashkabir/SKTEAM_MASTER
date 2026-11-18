#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_alladmins_$TS"
echo "✅ بک‌آپ: $ST.bak_alladmins_$TS"

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    lines = f.readlines()

# پیدا کردن شروع حلقه ادمین‌ها (خط `for _a in _db_admins:` توی do_refresh)
start = -1
for i, line in enumerate(lines):
    if 1560 <= i <= 1580 and 'for _a in _db_admins:' in line:
        start = i
        break

if start == -1:
    print("❌ پیدا نشد")
    exit(1)

print(f"✅ حلقه ادمین‌ها: خط {start + 1}")

# پیدا کردن انتهای حلقه (خط `lines.append` که آخرین append هست)
end = -1
for i in range(start, start + 30):
    if 'lines.append(f"🛡️ {_fname}{_uname_str} — ادمین")' in lines[i]:
        end = i
        break

if end == -1:
    print("❌ انتهای حلقه پیدا نشد")
    exit(1)

print(f"✅ انتها: خط {end + 1}")

# indent
base = lines[start][:len(lines[start]) - len(lines[start].lstrip())]

# کد جدید — ترکیب تلگرام + دیتابیس
new_block = (
    base + '# ★ ترکیب ادمین‌های تلگرام و دیتابیس\n' +
    base + '_all_admins = {}\n' +
    base + '\n' +
    base + '# ۱. ادمین‌های تلگرام (واقعی توی گروه)\n' +
    base + 'for _ta in _tg_admins:\n' +
    base + '    if _ta.user.id in _owner_ids or _ta.user.id == _bot_id:\n' +
    base + '        continue\n' +
    base + '    _all_admins[_ta.user.id] = {\n' +
    base + '        "name": _ta.user.first_name or "?",\n' +
    base + '        "username": _ta.user.username,\n' +
    base + '        "is_bot": getattr(_ta.user, "is_bot", False),\n' +
    base + '    }\n' +
    base + '\n' +
    base + '# ۲. ادمین‌های دیتابیس (اگه تکراری نباشن)\n' +
    base + 'for _a in _db_admins:\n' +
    base + '    _uid = _a.get("user_id")\n' +
    base + '    if _uid in _owner_ids or _uid == _bot_id:\n' +
    base + '        continue\n' +
    base + '    if _uid in _all_admins:\n' +
    base + '        continue\n' +
    base + '    _info = _members_info.get(_uid, {})\n' +
    base + '    _fname = _info.get("first_name") or _a.get("name") or "?"\n' +
    base + '    _is_bot = _fname.lower().endswith("bot") or "bot" in _fname.lower()\n' +
    base + '    _all_admins[_uid] = {\n' +
    base + '        "name": _fname,\n' +
    base + '        "username": _info.get("username"),\n' +
    base + '        "is_bot": _is_bot,\n' +
    base + '    }\n' +
    base + '\n' +
    base + '# ۳. نمایش\n' +
    base + 'for _uid, _info in _all_admins.items():\n' +
    base + '    _fname = _info["name"]\n' +
    base + '    _uname = _info["username"]\n' +
    base + '    _uname_str = f" (@{_uname})" if _uname else ""\n' +
    base + '    if _info["is_bot"]:\n' +
    base + '        lines.append(f"🤖{_uname_str} — ادمین")\n' +
    base + '    else:\n' +
    base + '        lines.append(f"🛡️ {_fname}{_uname_str} — ادمین")\n'
)

new_lines = lines[:start] + [new_block] + lines[end + 1:]

with open(ST, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("✅ حلقه ترکیبی جایگزین شد")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_alladmins_$TS" "$ST"
    exit 1
fi
echo ""

echo "═══ چک ═══"
grep -n "_all_admins" "$ST" | head -5
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
