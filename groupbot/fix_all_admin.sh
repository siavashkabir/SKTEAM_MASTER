#!/data/data/com.termux/files/usr/bin/bash

DB=database.py
AC=modules/access.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$DB" "$DB.bak_alladmin_$TS"
cp "$AC" "$AC.bak_alladmin_$TS"
echo "✅ بک‌آپ گرفته شد"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
# ═══════════════════════════════════════════════
# ۱. database.py — is_admin, get_group_admins
# ═══════════════════════════════════════════════
DB = "/data/data/com.termux/files/home/groupbot/database.py"

with open(DB, "r", encoding="utf-8") as f:
    db = f.read()

# is_admin
if "def is_admin(" not in db:
    db += '''


def is_admin(chat_id, user_id):
    """چک می‌کنه کاربر ادمین گروهه"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("SELECT user_id FROM group_admins WHERE chat_id=? AND user_id=?", (chat_id, user_id))
        r = c.fetchone()
        conn.close()
        return r is not None
    except Exception as e:
        print(f"[IS_ADMIN ERR] {e}")
        return False


def get_group_admins(chat_id):
    """گرفتن لیست ادمین‌ها"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("SELECT user_id, name FROM group_admins WHERE chat_id=?", (chat_id,))
        rows = c.fetchall()
        conn.close()
        return [{"user_id": r[0], "name": r[1]} for r in rows]
    except Exception as e:
        print(f"[GET GROUP ADMINS ERR] {e}")
        return []


def remove_admin_from_db(chat_id, user_id):
    """حذف ادمین"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM group_admins WHERE chat_id=? AND user_id=?", (chat_id, user_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[REMOVE ADMIN ERR] {e}")
        return False
'''
    print("✅ توابع is_admin/get_group_admins/remove_admin_from_db به database اضافه شد")
else:
    print("⚠️ is_admin از قبل هست")

with open(DB, "w", encoding="utf-8") as f:
    f.write(db)

# ═══════════════════════════════════════════════
# ۲. access.py — import + case admin
# ═══════════════════════════════════════════════
AC = "/data/data/com.termux/files/home/groupbot/modules/access.py"

with open(AC, "r", encoding="utf-8") as f:
    ac = f.read()

# import is_admin
if "is_admin," not in ac and "is_admin " not in ac.split("def ")[0]:
    if "is_bot_admin, is_group_owner" in ac:
        ac = ac.replace(
            "is_bot_admin, is_group_owner",
            "is_bot_admin, is_admin, is_group_owner",
            1
        )
        print("✅ is_admin به import اضافه شد")
    else:
        print("⚠️ is_bot_admin توی import پیدا نشد")

# case admin توی build_access_menu
if 'role == "admin"' not in ac:
    old = '    elif role in ("vip", "member"):'
    new = '''    elif role == "admin":
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
        _MAP = {"purge": "can_delete_messages", "ban": "can_restrict_members",
                "pin": "can_pin_messages", "admin_add": "can_invite_users",
                "vcall": "can_manage_video_chats", "group_info": "can_change_info"}
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
    if old in ac:
        ac = ac.replace(old, new, 1)
        print("✅ case admin اضافه شد")
    else:
        print("⚠️ elif vip پیدا نشد")
else:
    print("⚠️ case admin از قبل هست")

with open(AC, "w", encoding="utf-8") as f:
    f.write(ac)

print("✅ ذخیره شد")
PYEOF

echo ""

# کامپایل
if python3 -m py_compile "$DB" 2>&1 && python3 -m py_compile "$AC" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$DB.bak_alladmin_$TS" "$DB"
    cp "$AC.bak_alladmin_$TS" "$AC"
    exit 1
fi
echo ""

# تست
echo "─── تست نهایی ───"
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
try:
    from database import is_admin, get_group_admins
    chat_id = -1004349813270
    uid = 8401175719
    print(f"is_admin({uid}) = {is_admin(chat_id, uid)}")
    admins = get_group_admins(chat_id)
    print(f"admins count = {len(admins)}")
    for a in admins:
        print(f"  {a}")
except Exception as e:
    print(f"❌ {e}")
    import traceback
    traceback.print_exc()
PYEOF
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix کامل انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
