#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_pmfinal_$TS"
echo "✅ بک‌آپ: $ST.bak_pmfinal_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    lines = f.readlines()

# پیدا کردن خط اول try (pm_confirm) برای گرفتن indent
try_idx = -1
for i, line in enumerate(lines):
    if 'if action == "pm_confirm":' in line:
        # خط بعدش try هست
        for j in range(i + 1, i + 5):
            if lines[j].strip() == "try:":
                try_idx = j
                break
        break

if try_idx == -1:
    print("❌ try پیدا نشد")
    exit(1)

# indent واقعی try
try_indent = lines[try_idx][:len(lines[try_idx]) - len(lines[try_idx].lstrip())]
print(f"indent واقعی try: {len(try_indent)} فاصله")
print(f"محتوا: {repr(try_indent)}")

# indent داخل try (بدنه)
body_indent = try_indent + "    "
except_indent = try_indent

# پیدا کردن خط دوم add_admin_to_db
count = 0
target_idx = -1
for i, line in enumerate(lines):
    if 'add_admin_to_db(chat_id, target_id, "Admin")' in line:
        count += 1
        if count == 2:
            target_idx = i
            break

if target_idx == -1:
    print("❌ خط دوم add_admin_to_db پیدا نشد")
    exit(1)

print(f"✅ خط دوم add_admin_to_db: خط {target_idx + 1}")

# کد جدید — با indent درست
new_code = [
    "\n",
    body_indent + "# ★ ذخیره perms در admin_permissions\n",
    body_indent + "try:\n",
    body_indent + "    from database import set_admin_perm\n",
    body_indent + '    _perms = PROMOTE_WAIT.get(uid, {}).get("perms", {})\n',
    body_indent + '    print(f"[PM_CONFIRM] perms count = {len(_perms)}")\n',
    body_indent + "    for _perm_name, _enabled in _perms.items():\n",
    body_indent + '        set_admin_perm(chat_id, target_id, "admin", _perm_name, 1 if _enabled else 0)\n',
    body_indent + "except Exception as _e:\n",
    body_indent + '    print(f"[PM_CONFIRM PERMS ERR] {_e}")\n',
]

new_lines = lines[:target_idx + 1] + new_code + lines[target_idx + 1:]

with open(ST, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("✅ کد اضافه شد")
PYEOF

echo ""

# کامپایل
if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_pmfinal_$TS" "$ST"
    python3 -m py_compile "$ST" 2>&1 | head -5
    exit 1
fi
echo ""

echo "─── چک ───"
LINE=$(grep -n "PM_CONFIRM\] perms count" "$ST" | head -1 | cut -d: -f1)
if [ -n "$LINE" ]; then
    sed -n "$((LINE-5)),$((LINE+8))p" "$ST"
fi
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
