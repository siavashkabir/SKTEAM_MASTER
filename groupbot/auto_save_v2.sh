#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_autosave2_$TS"
echo "✅ بک‌آپ: $ST.bak_autosave2_$TS"

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    lines = f.readlines()

# پیدا کردن خط `_uid_rm = None` توی persian_handler
target = -1
for i, line in enumerate(lines):
    if '_uid_rm = None' in line and i > 100:
        # چک کن خط بعدی خالی یا خط بعدی `if _uid_rm` باشه
        target = i
        break

if target == -1:
    print("❌ پیدا نشد")
    exit(1)

print(f"✅ خط {target + 1}")

# indent
indent = lines[target][:len(lines[target]) - len(lines[target].lstrip())]
# indent بالاتر از try (که ۴ فاصله کم‌تره)
i_outer = indent[:-4] if len(indent) >= 4 else indent

# اضافه کردن auto-save بعد از _uid_rm = None
new_code = [
    "\n",
    i_outer + "# ★ auto-save ادمین‌ها\n",
    i_outer + "try:\n",
    i_outer + "    from database import is_admin, add_admin_to_db\n",
    i_outer + "    _msg = update.effective_message\n",
    i_outer + "    _chat = update.effective_chat\n",
    i_outer + '    if _msg and _chat and _chat.type in ("group", "supergroup") and _msg.from_user:\n',
    i_outer + "        _uid = _msg.from_user.id\n",
    i_outer + '        _fname = _msg.from_user.first_name or "?"\n',
    i_outer + "        if _uid != context.bot.id:\n",
    i_outer + "            try:\n",
    i_outer + "                _member = await context.bot.get_chat_member(_chat.id, _uid)\n",
    i_outer + '                if _member.status in ("creator", "administrator"):\n',
    i_outer + "                    if not is_admin(_chat.id, _uid):\n",
    i_outer + "                        add_admin_to_db(_chat.id, _uid, _fname)\n",
    i_outer + '                        print(f"[AUTO-SAVE ADMIN] {_fname} ({_uid}) in {_chat.id}")\n',
    i_outer + "            except Exception:\n",
    i_outer + "                pass\n",
    i_outer + "except Exception as _e:\n",
    i_outer + '    print(f"[AUTO-SAVE ERR] {_e}")\n',
    "\n",
]

lines = lines[:target + 1] + new_code + lines[target + 1:]

with open(ST, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("✅ auto-save اضافه شد")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_autosave2_$TS" "$ST"
    exit 1
fi
echo ""

echo "═══ چک ═══"
grep -n "AUTO-SAVE ADMIN" "$ST"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo ""
echo "بعد توی گروه HERITAGE از ادمین‌ها بخواه پیام بفرستن"
echo "بعد «پیکربندی» بزن"
echo "═══════════════════════════════════════════════════"
