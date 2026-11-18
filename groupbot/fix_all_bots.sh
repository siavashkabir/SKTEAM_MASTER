#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_allbots_$TS"
echo "✅ بک‌آپ: $ST.bak_allbots_$TS"

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    content = f.read()

# پیدا کردن حلقه ادمین‌ها
old = '''for _a in _db_admins:
        _uid = _a.get("user_id")
        if _uid in _owner_ids or _uid == _bot_id:
            continue
        _info = _members_info.get(_uid, {})
        _fname = _info.get("first_name") or _a.get("name") or "?"
        _uname = _info.get("username")
        _uname_str = f" (@{_uname})" if _uname else ""
        lines.append(f"🛡️ {_fname}{_uname_str} — ادمین")'''

new = '''for _a in _db_admins:
        _uid = _a.get("user_id")
        if _uid in _owner_ids or _uid == _bot_id:
            continue
        _info = _members_info.get(_uid, {})
        _fname = _info.get("first_name") or _a.get("name") or "?"
        _uname = _info.get("username")
        _uname_str = f" (@{_uname})" if _uname else ""
        # ★ چک کن بوت هست یا نه
        _is_bot = False
        try:
            _member = await context.bot.get_chat_member(chat_id, _uid)
            _is_bot = getattr(_member.user, "is_bot", False)
        except Exception:
            # اگه نشد از اسم چک کن
            if _fname.lower().endswith("bot") or "bot" in _fname.lower():
                _is_bot = True
        if _is_bot:
            lines.append(f"🤖{_uname_str} — ادمین")
        else:
            lines.append(f"🛡️ {_fname}{_uname_str} — ادمین")'''

if old in content:
    content = content.replace(old, new, 1)
    print("✅ حلقه ادمین‌ها آپدیت شد")
else:
    print("⚠️ الگو پیدا نشد — دیاگ:")
    idx = content.find("for _a in _db_admins:")
    print(content[idx:idx+500])

with open(ST, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_allbots_$TS" "$ST"
    exit 1
fi
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
