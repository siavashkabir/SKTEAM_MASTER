#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_pmperms2_$TS"
echo "✅ بک‌آپ: $ST.bak_pmperms2_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    lines = f.readlines()

# پیدا کردن خط دوم add_admin_to_db (بعد از except ImportError)
count = 0
target_idx = -1

for i, line in enumerate(lines):
    if 'add_admin_to_db(chat_id, target_id, "Admin")' in line:
        count += 1
        if count == 2:  # خط دوم
            target_idx = i
            print(f"✅ خط دوم add_admin_to_db: خط {i+1}")
            print(f"   محتوا: {line.rstrip()}")
            break

if target_idx == -1:
    print("❌ خط دوم add_admin_to_db پیدا نشد")
    exit(1)

# کد جدید — بعد از add_admin_to_db
indent = "        "  # 8 فاصله

new_code = [
    "\n",
    indent + "# ★ ذخیره perms در admin_permissions\n",
    indent + "try:\n",
    indent + "    from database import set_admin_perm\n",
    indent + "    _perms = PROMOTE_WAIT.get(uid, {}).get(\"perms\", {})\n",
    indent + "    print(f\"[PM_CONFIRM] ذخیره {len(_perms)} perm برای user {target_id}\")\n",
    indent + "    for _perm_name, _enabled in _perms.items():\n",
    indent + "        set_admin_perm(chat_id, target_id, \"admin\", _perm_name, 1 if _enabled else 0)\n",
    indent + "except Exception as _e:\n",
    indent + "    print(f\"[PM_CONFIRM PERMS ERR] {_e}\")\n",
    indent + "    import traceback\n",
    indent + "    traceback.print_exc()\n",
]

new_lines = lines[:target_idx + 1] + new_code + lines[target_idx + 1:]

with open(ST, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("✅ کد ذخیره perms اضافه شد")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_pmperms2_$TS" "$ST"
    exit 1
fi
echo ""

echo "─── چک ───"
LINE=$(grep -n "PM_CONFIRM\] ذخیره" "$ST" | head -1 | cut -d: -f1)
if [ -n "$LINE" ]; then
    sed -n "$((LINE-6)),$((LINE+10))p" "$ST"
fi
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
