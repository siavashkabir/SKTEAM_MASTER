#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_botline_$TS"
echo "✅ بک‌آپ: $ST.bak_botline_$TS"

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    lines = f.readlines()

# پیدا کردن خط `lines.append(f"🛡️ {_fname}{_uname_str} — ادمین")` توی حلقه ادمین‌ها
target = -1
for i, line in enumerate(lines):
    if 'lines.append(f"🛡️ {_fname}{_uname_str} — ادمین")' in line:
        target = i
        break

if target == -1:
    print("❌ پیدا نشد")
    exit(1)

print(f"✅ خط {target + 1}")

# indent خط
indent = lines[target][:len(lines[target]) - len(lines[target].lstrip())]

# کد جدید — با چک بوت
new_code = (
    indent + "# ★ چک کن بوت هست یا نه\n" +
    indent + "_is_bot = False\n" +
    indent + "if _fname.lower().endswith('bot') or 'bot' in _fname.lower():\n" +
    indent + "    _is_bot = True\n" +
    indent + "if _is_bot:\n" +
    indent + '    lines.append(f"🤖{_uname_str} — ادمین")\n' +
    indent + "else:\n" +
    indent + '    lines.append(f"🛡️ {_fname}{_uname_str} — ادمین")\n'
)

# جایگزینی خط قدیمی با کد جدید
new_lines = lines[:target] + [new_code] + lines[target + 1:]

with open(ST, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("✅ خط append عوض شد")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_botline_$TS" "$ST"
    exit 1
fi
echo ""

echo "═══ چک ═══"
grep -n "_is_bot\|🤖{_uname_str}" "$ST" | head -5
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
