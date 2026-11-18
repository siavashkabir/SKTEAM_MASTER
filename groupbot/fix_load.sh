#!/data/data/com.termux/files/usr/bin/bash

AD=modules/admin.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$AD" "$AD.bak_load_$TS"
echo "✅ بک‌آپ: $AD.bak_load_$TS"

source venv/bin/activate

python3 << 'PYEOF'
AD = "/data/data/com.termux/files/home/groupbot/modules/admin.py"

with open(AD, "r", encoding="utf-8") as f:
    content = f.read()

# پیدا کردن جای ساخت PROMOTE_WAIT
old = '''    PROMOTE_WAIT[user.id] = {
        "chat_id": chat.id,
        "target_id": target,
        "target_name": target_name or "?",
        "perms": {
            "can_delete_messages": False,
            "can_restrict_members": False,
            "can_pin_messages": False,
            "can_invite_users": False,
            "can_manage_video_chats": False,
            "can_change_info": False,
        }
    }'''

new = '''    # ★ خوندن perms فعلی از دیتابیس
    _TG2BOT = {
        "can_delete_messages": "purge",
        "can_restrict_members": "ban",
        "can_pin_messages": "pin",
        "can_invite_users": "admin_add",
        "can_manage_video_chats": "vcall",
        "can_change_info": "group_info",
    }
    _loaded = {}
    try:
        from database import get_all_perms
        _saved = get_all_perms(chat.id, target)
        print(f"[PROMOTE LOAD] saved perms: {_saved}")
        for _tg, _bot in _TG2BOT.items():
            _loaded[_tg] = bool(_saved.get(_bot, _saved.get(_tg, False)))
    except Exception as _e:
        print(f"[PROMOTE LOAD ERR] {_e}")
        _loaded = {k: False for k in _TG2BOT.keys()}

    PROMOTE_WAIT[user.id] = {
        "chat_id": chat.id,
        "target_id": target,
        "target_name": target_name or "?",
        "perms": _loaded
    }'''

if old in content:
    content = content.replace(old, new, 1)
    print("✅ PROMOTE_WAIT از دیتابیس پر می‌شه")
else:
    print("❌ الگو پیدا نشد")

with open(AD, "w", encoding="utf-8") as f:
    f.write(content)
PYEOF

echo ""

if python3 -m py_compile "$AD" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$AD.bak_load_$TS" "$AD"
    exit 1
fi
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
