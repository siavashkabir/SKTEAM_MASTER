#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
AC=modules/access.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_complete_$TS"
cp "$AC" "$AC.bak_complete_$TS"
echo "✅ بک‌آپ گرفته شد"

source venv/bin/activate

# ۱. پاک کردن admin_permissions قدیمی (key های تلگرام)
python3 -c "
import sqlite3
from config import DATABASE_PATH
conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()
c.execute(\"DELETE FROM admin_permissions WHERE chat_id=-1004349813270\")
print(f'✅ {c.rowcount} ردیف قدیمی پاک شد')
conn.commit()
conn.close()
"
echo ""

# ۲. fix start.py — pm_confirm با mapping
python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"
with open(ST, "r", encoding="utf-8") as f:
    content = f.read()

old = '''            from database import set_admin_perm
            _perms = PROMOTE_WAIT.get(uid, {}).get("perms", {})
            print(f"[PM_CONFIRM] perms count = {len(_perms)}")
            for _perm_name, _enabled in _perms.items():
                set_admin_perm(chat_id, target_id, "admin", _perm_name, 1 if _enabled else 0)
        except Exception as _e:
            print(f"[PM_CONFIRM PERMS ERR] {_e}")'''

new = '''            from database import set_admin_perm
            _TG2BOT = {
                "can_delete_messages": "purge",
                "can_restrict_members": "ban",
                "can_pin_messages": "pin",
                "can_invite_users": "admin_add",
                "can_manage_video_chats": "vcall",
                "can_change_info": "group_info",
                "can_promote_members": "admin_add",
                "can_manage_chat": "panel",
            }
            _perms = PROMOTE_WAIT.get(uid, {}).get("perms", {})
            print(f"[PM_CONFIRM] perms count = {len(_perms)}")
            for _tg_name, _enabled in _perms.items():
                _bot_key = _TG2BOT.get(_tg_name, _tg_name)
                set_admin_perm(chat_id, target_id, "admin", _bot_key, 1 if _enabled else 0)
                print(f"[PM_CONFIRM] {_tg_name} → {_bot_key} = {_enabled}")
        except Exception as _e:
            print(f"[PM_CONFIRM PERMS ERR] {_e}")'''

if old in content:
    content = content.replace(old, new, 1)
    print("✅ pm_confirm با mapping")
else:
    print("⚠️ pm_confirm - الگو نبود")

with open(ST, "w", encoding="utf-8") as f:
    f.write(content)
PYEOF

# ۳. fix access.py — case admin + acc_ap_ handler
python3 << 'PYEOF'
import re
AC = "/data/data/com.termux/files/home/groupbot/modules/access.py"
with open(AC, "r", encoding="utf-8") as f:
    content = f.read()

# case admin ساده
old_case = '''    # ★ ادمین → ADMIN_PERMS
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
            keyboard.append([InlineKeyboardButton(mark + " " + label, callback_data="acc_ap_" + key + ":" + str(uid) + ":" + str(chat_id) + ":" + str(target_id))])'''

new_case = '''    # ★ ادمین → ADMIN_PERMS
    elif role == "admin":
        import sqlite3
        from config import DATABASE_PATH
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            c = conn.cursor()
            c.execute("SELECT perm_name, enabled FROM admin_permissions WHERE chat_id=? AND user_id=? AND role='admin'", (chat_id, target_id))
            perms = {r[0]: bool(r[1]) for r in c.fetchall()}
            conn.close()
        except Exception:
            perms = {}
        keyboard.append([InlineKeyboardButton("🛡️ مدیر گروه", callback_data="acc_noop:" + str(uid) + ":" + str(chat_id))])
        for key, label in ADMIN_PERMS:
            en = perms.get(key, True)
            mark = "✅" if en else "❌"
            keyboard.append([InlineKeyboardButton(mark + " " + label, callback_data="acc_ap_" + key + ":" + str(uid) + ":" + str(chat_id) + ":" + str(target_id))])'''

if old_case in content:
    content = content.replace(old_case, new_case, 1)
    print("✅ case admin")
else:
    print("⚠️ case admin نبود")

# acc_ap_ handler
pattern = r'(if action\.startswith\("acc_ap_"\):.*?)toggle_user_perm\(chat_id, target_id, key\)'
match = re.search(pattern, content, re.DOTALL)
if match:
    new_ap = match.group(1) + '''from database import get_admin_perm, set_admin_perm
        _cur = get_admin_perm(chat_id, target_id, key)
        set_admin_perm(chat_id, target_id, "admin", key, 0 if _cur else 1)'''
    content = content.replace(match.group(0), new_ap, 1)
    print("✅ acc_ap_ handler")
else:
    print("⚠️ acc_ap_ نبود")

with open(AC, "w", encoding="utf-8") as f:
    f.write(content)
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1 && python3 -m py_compile "$AC" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_complete_$TS" "$ST"
    cp "$AC.bak_complete_$TS" "$AC"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════"
echo "✅ Fix کامل انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
