#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_direct_$TS"
echo "✅ بک‌آپ: $ST.bak_direct_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    lines = f.readlines()

# پیدا کردن pm_toggle و خط "perms = PROMOTE_WAIT[uid]["perms"]"
toggle_idx = -1
perms_line_idx = -1

for i, line in enumerate(lines):
    if 'if action.startswith("pm_toggle_"):' in line:
        toggle_idx = i
    if toggle_idx >= 0 and 'perms = PROMOTE_WAIT[uid]["perms"]' in line:
        # مطمئن شیم توی pm_toggle هست
        if i - toggle_idx < 30:
            perms_line_idx = i
            break

if toggle_idx == -1:
    print("❌ pm_toggle پیدا نشد")
    exit(1)
if perms_line_idx == -1:
    print("❌ خط perms پیدا نشد")
    exit(1)

print(f"✅ pm_toggle: خط {toggle_idx + 1}")
print(f"✅ perms line: خط {perms_line_idx + 1}")

# indent رو از خط perms بگیر
indent = lines[perms_line_idx][:len(lines[perms_line_idx]) - len(lines[perms_line_idx].lstrip())]
print(f"indent: {len(indent)} فاصله")

# کد جدید — بعد از perms line اضافه کن
new_code = [
    "\n",
    indent + "# ★ ذخیره مستقیم توی admin_permissions\n",
    indent + "try:\n",
    indent + "    _info = PROMOTE_WAIT.get(uid, {})\n",
    indent + '    _cid = _info.get("chat_id")\n',
    indent + '    _tid = _info.get("target_id")\n',
    indent + "    if _cid and _tid:\n",
    indent + '        from database import set_admin_perm\n',
    indent + '        _TG2BOT = {\n',
    indent + '            "can_delete_messages": "purge",\n',
    indent + '            "can_restrict_members": "ban",\n',
    indent + '            "can_pin_messages": "pin",\n',
    indent + '            "can_invite_users": "admin_add",\n',
    indent + '            "can_manage_video_chats": "vcall",\n',
    indent + '            "can_change_info": "group_info",\n',
    indent + '            "can_promote_members": "admin_add",\n',
    indent + '            "can_manage_chat": "panel",\n',
    indent + '        }\n',
    indent + '        _bot_key = _TG2BOT.get(perm_name, perm_name)\n',
    indent + '        _val = 1 if PROMOTE_WAIT[uid]["perms"][perm_name] else 0\n',
    indent + '        set_admin_perm(_cid, _tid, "admin", _bot_key, _val)\n',
    indent + '        print(f"[PM_TOGGLE SAVED] {perm_name} -> {_bot_key} = {_val}")\n',
    indent + "except Exception as _e:\n",
    indent + '    print(f"[PM_TOGGLE SAVE ERR] {_e}")\n',
]

# اضافه کردن بعد از خط perms
new_lines = lines[:perms_line_idx + 1] + new_code + lines[perms_line_idx + 1:]

with open(ST, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("✅ کد ذخیره مستقیم اضافه شد")
PYEOF

echo ""

# کامپایل
if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_direct_$TS" "$ST"
    exit 1
fi
echo ""

echo "─── چک: خط new ───"
LINE=$(grep -n "PM_TOGGLE SAVED" "$ST" | head -1 | cut -d: -f1)
if [ -n "$LINE" ]; then
    sed -n "$((LINE-15)),$((LINE+3))p" "$ST"
fi
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo ""
echo "بعد توی تلگرام:"
echo "1. روی کاربر ریپلای کن"
echo "2. افزودن مدیر"
echo "3. یه تیک بزن"
echo "4. تایید"
echo ""
echo "بعد این رو بزن و نتیجه رو بفرست:"
echo "tail -n 50 ~/groupbot_bot.log | grep -E 'PM_TOGGLE|PM_CONFIRM'"
echo "═══════════════════════════════════════════════════"
