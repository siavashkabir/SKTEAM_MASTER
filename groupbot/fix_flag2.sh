#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$AC" "$AC.bak_flag2_$TS"
echo "✅ بک‌آپ: $AC.bak_flag2_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
AC = "/data/data/com.termux/files/home/groupbot/modules/access.py"

with open(AC, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
fix_count = 0

for line in lines:
    stripped = line.strip()
    
    # toggle_deputy_perm(chat_id, key)
    if stripped == "toggle_deputy_perm(chat_id, key)":
        indent = line[:len(line) - len(line.lstrip())]
        new_lines.append(line)
        new_lines.append(indent + 'context.bot_data.setdefault("access_changed", {})\n')
        new_lines.append(indent + 'context.bot_data["access_changed"][(chat_id, target_id)] = True\n')
        new_lines.append(indent + 'print(f"[ACCESS DBG SET] key=({chat_id}, {target_id})")\n')
        fix_count += 1
        continue
    
    # toggle_user_perm(chat_id, target_id, key)
    if stripped == "toggle_user_perm(chat_id, target_id, key)":
        indent = line[:len(line) - len(line.lstrip())]
        new_lines.append(line)
        new_lines.append(indent + 'context.bot_data.setdefault("access_changed", {})\n')
        new_lines.append(indent + 'context.bot_data["access_changed"][(chat_id, target_id)] = True\n')
        new_lines.append(indent + 'print(f"[ACCESS DBG SET] key=({chat_id}, {target_id})")\n')
        fix_count += 1
        continue
    
    new_lines.append(line)

with open(AC, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print(f"✅ {fix_count} تا toggle fix شد")
PYEOF

echo ""

if python3 -m py_compile "$AC" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$AC.bak_flag2_$TS" "$AC"
    exit 1
fi
echo ""

echo "─── چک ───"
echo "ACCESS DBG SET: $(grep -c 'ACCESS DBG SET' "$AC")"
echo "access_changed: $(grep -c 'access_changed' "$AC")"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
