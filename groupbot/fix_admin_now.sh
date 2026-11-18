#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$AC" "$AC.bak_adminnow_$TS"
echo "✅ بک‌آپ: $AC.bak_adminnow_$TS"

source venv/bin/activate

python3 << 'PYEOF'
AC = "/data/data/com.termux/files/home/groupbot/modules/access.py"

with open(AC, "r", encoding="utf-8") as f:
    content = f.read()

# الگو: قبل از elif role in ("vip", "member"):
old = '''    elif role in ("vip", "member"):'''

new = '''    # ★ ادمین → ADMIN_PERMS
    elif role == "admin":
        import sqlite3
        from config import DATABASE_PATH
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            c = conn.cursor()
            c.execute("SELECT perm_name, enabled FROM admin_permissions WHERE chat_id=? AND user_id=?", (chat_id, target_id))
            perms = {r[0]: bool(r[1]) for r in c.fetchall()}
            conn.close()
        except Exception:
            perms = {}
        _MAP = {
            "purge": "can_delete_messages",
            "ban": "can_restrict_members",
            "pin": "can_pin_messages",
            "admin_add": "can_invite_users",
            "vcall": "can_manage_video_chats",
            "group_info": "can_change_info",
        }
        keyboard.append([InlineKeyboardButton("🛡️ مدیر گروه", callback_data="acc_noop:" + str(uid) + ":" + str(chat_id))])
        for key, label in ADMIN_PERMS:
            if key in perms:
                en = perms[key]
            elif _MAP.get(key) in perms:
                en = perms[_MAP[key]]
            else:
                en = True
            mark = "✅" if en else "❌"
            keyboard.append([InlineKeyboardButton(mark + " " + label, callback_data="acc_ap_" + key + ":" + str(uid) + ":" + str(chat_id) + ":" + str(target_id))])

    elif role in ("vip", "member"):'''

if old in content:
    content = content.replace(old, new, 1)
    print("✅ case admin اضافه شد")
else:
    print("❌ الگو پیدا نشد")
    exit(1)

with open(AC, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$AC" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$AC.bak_adminnow_$TS" "$AC"
    exit 1
fi
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
