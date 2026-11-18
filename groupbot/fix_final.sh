#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$AC" "$AC.bak_final_$TS"
echo "✅ بک‌آپ: $AC.bak_final_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
AC = "/data/data/com.termux/files/home/groupbot/modules/access.py"

with open(AC, "r", encoding="utf-8") as f:
    content = f.read()

# ═══ fix 1: default False در case admin ═══
old1 = '''        for key, label in ADMIN_PERMS:
            if key in perms:
                en = perms[key]
            elif _MAP.get(key) in perms:
                en = perms[_MAP[key]]
            else:
                en = True
            mark = "✅" if en else "❌"'''

new1 = '''        for key, label in ADMIN_PERMS:
            if key in perms:
                en = perms[key]
            elif _MAP.get(key) in perms:
                en = perms[_MAP[key]]
            else:
                en = False
            mark = "✅" if en else "❌"'''

if old1 in content:
    content = content.replace(old1, new1, 1)
    print("✅ default False شد")
else:
    print("⚠️ الگو ۱ پیدا نشد")

# ═══ fix 2: acc_ap_ با هر دو key ذخیره کن ═══
old2 = '''        from database import get_admin_perm, set_admin_perm
        _cur = get_admin_perm(chat_id, target_id, key)
        set_admin_perm(chat_id, target_id, "admin", key, 0 if _cur else 1)'''

new2 = '''        from database import get_admin_perm, set_admin_perm
        _REV_MAP = {
            "purge": "can_delete_messages",
            "ban": "can_restrict_members",
            "pin": "can_pin_messages",
            "admin_add": "can_invite_users",
            "vcall": "can_manage_video_chats",
            "group_info": "can_change_info",
        }
        _cur = get_admin_perm(chat_id, target_id, key)
        _new = 0 if _cur else 1
        set_admin_perm(chat_id, target_id, "admin", key, _new)
        if key in _REV_MAP:
            set_admin_perm(chat_id, target_id, "admin", _REV_MAP[key], _new)
        print(f"[ACC_AP] {key} = {_new}")'''

if old2 in content:
    content = content.replace(old2, new2, 1)
    print("✅ acc_ap_ با هر دو key")
else:
    print("⚠️ الگو ۲ پیدا نشد")

# ═══ fix 3: role_emoji و role_label برای admin ═══
if '"admin": "🛡️"' not in content and '"admin":' not in content:
    # role_label
    if '        "admin": "مدیر گروه",' not in content:
        content = content.replace(
            '        "group_owner": "مالک گروه",',
            '        "group_owner": "مالک گروه",\n        "admin": "مدیر گروه",',
            1
        )
        print("✅ role_label admin")
    # role_emoji
    if '"admin": "🛡️"' not in content:
        content = content.replace(
            '        "group_owner": "🏆",',
            '        "group_owner": "🏆",\n        "admin": "🛡️",',
            1
        )
        print("✅ role_emoji admin")

with open(AC, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$AC" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$AC.bak_final_$TS" "$AC"
    exit 1
fi
echo ""

echo "─── چک نهایی ───"
grep -n "_REV_MAP\|default False\|en = False" "$AC" | head -5
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
