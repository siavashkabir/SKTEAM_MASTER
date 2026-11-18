#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$AC" "$AC.bak_adminrole2_$TS"
echo "✅ بک‌آپ: $AC.bak_adminrole2_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
import re

AC = "/data/data/com.termux/files/home/groupbot/modules/access.py"

with open(AC, "r", encoding="utf-8") as f:
    content = f.read()

# ═══ ۱. import is_admin ═══
# ببین آیا is_admin توی import هست؟
if "is_admin" not in content.split("def ")[0]:
    # اضافه کن به import از database
    pattern = r'from database import \(([^)]+)\)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        imports = match.group(1)
        if "is_admin" not in imports:
            new_imports = imports.rstrip() + "\n    is_admin,\n    is_deputy,\n    is_vip,\n"
            content = content.replace(match.group(0), "from database import (" + new_imports + ")", 1)
            print("✅ is_admin/is_deputy/is_vip به import اضافه شد")
    else:
        # تک خطی
        if "from database import" in content:
            content = content.replace(
                "from database import ",
                "from database import is_admin, is_deputy, is_vip, ",
                1
            )
            print("✅ is_admin به import (تک خطی) اضافه شد")

# ═══ ۲. get_target_role ═══
old_role = '''def get_target_role(chat_id, user_id):
    """تشخیص نقش کاربر توی گروه"""
    try:
        if user_id == OWNER_ID:
            return "bot_owner"
        if is_bot_admin(user_id):
            return "bot_admin"
        if is_group_owner(chat_id, user_id):
            return "group_owner"
        if is_deputy(chat_id, user_id):
            return "deputy"
        if is_vip(chat_id, user_id):
            return "vip"
    except Exception:
        pass
    return "member"'''

new_role = '''def get_target_role(chat_id, user_id):
    """تشخیص نقش کاربر توی گروه"""
    try:
        if user_id == OWNER_ID:
            return "bot_owner"
        if is_bot_admin(user_id):
            return "bot_admin"
        if is_group_owner(chat_id, user_id):
            return "group_owner"
        # ★ ادمین رو قبل از deputy چک کن
        try:
            if is_admin(chat_id, user_id):
                return "admin"
        except Exception:
            pass
        if is_deputy(chat_id, user_id):
            return "deputy"
        if is_vip(chat_id, user_id):
            return "vip"
    except Exception:
        pass
    return "member"'''

if old_role in content:
    content = content.replace(old_role, new_role, 1)
    print("✅ get_target_role اصلاح شد")
else:
    print("⚠️ get_target_role با الگوی دقیق پیدا نشد")

# ═══ ۳. role_label — اضافه کردن admin ═══
old_label = '''    labels = {
        "bot_owner": "مالک ربات",
        "bot_admin": "ادمین ربات (سودو)",
        "group_owner": "مالک گروه",
        "deputy": "معاون",
        "vip": "عضو ویژه (VIP)",
        "member": "عضو عادی",
    }'''

new_label = '''    labels = {
        "bot_owner": "مالک ربات",
        "bot_admin": "ادمین ربات (سودو)",
        "group_owner": "مالک گروه",
        "admin": "مدیر گروه",
        "deputy": "معاون",
        "vip": "عضو ویژه (VIP)",
        "member": "عضو عادی",
    }'''

if old_label in content:
    content = content.replace(old_label, new_label, 1)
    print("✅ role_label اصلاح شد")

# role_emoji
old_emoji = '''    labels = {
        "bot_owner": "👑",
        "bot_admin": "⭐",
        "group_owner": "🏆",
        "deputy": "🎖️",
        "vip": "💎",
        "member": "👤",
    }'''

new_emoji = '''    labels = {
        "bot_owner": "👑",
        "bot_admin": "⭐",
        "group_owner": "🏆",
        "admin": "🛡️",
        "deputy": "🎖️",
        "vip": "💎",
        "member": "👤",
    }'''

if old_emoji in content:
    content = content.replace(old_emoji, new_emoji, 1)
    print("✅ role_emoji اصلاح شد")

# ═══ ۴. build_access_menu — اضافه کردن admin case ═══
# پیدا کردن elif role in ("vip", "member"):
old_menu = '''    # VIP یا member → VIP_PERMS
    elif role in ("vip", "member"):'''

new_menu = '''    # ادمین → ADMIN_PERMS
    elif role == "admin":
        # خواندن از admin_permissions
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
        if not perms:
            perms = {k: True for k, _ in ADMIN_PERMS}
        keyboard.append([InlineKeyboardButton("🛡️ مدیر گروه", callback_data="acc_noop:" + str(uid) + ":" + str(chat_id))])
        for key, label in ADMIN_PERMS:
            en = perms.get(key, True)
            mark = "✅" if en else "❌"
            keyboard.append([InlineKeyboardButton(mark + " " + label, callback_data="acc_ap_" + key + ":" + str(uid) + ":" + str(chat_id) + ":" + str(target_id))])

    # VIP یا member → VIP_PERMS
    elif role in ("vip", "member"):'''

if old_menu in content:
    content = content.replace(old_menu, new_menu, 1)
    print("✅ build_access_menu (admin case) اضافه شد")

with open(AC, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$AC" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$AC.bak_adminrole2_$TS" "$AC"
    exit 1
fi
echo ""

echo "─── چک ───"
echo "is_admin در import: $(grep -c 'is_admin' "$AC")"
echo "role == admin case: $(grep -c 'role == \"admin\"' "$AC")"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
