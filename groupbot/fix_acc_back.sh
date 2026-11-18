#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$AC" "$AC.bak_accback_$TS"
echo "✅ بک‌آپ: $AC.bak_accback_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
AC = "/data/data/com.termux/files/home/groupbot/modules/access.py"

with open(AC, "r", encoding="utf-8") as f:
    lines = f.readlines()

# پیدا کردن خط acc_back
start_idx = -1
for i, line in enumerate(lines):
    if 'if action == "acc_back":' in line:
        start_idx = i
        break

if start_idx == -1:
    print("❌ acc_back پیدا نشد")
    exit(1)

print(f"✅ acc_back در خط {start_idx + 1}")

# پیدا کردن انتهای بلاک — اولین "if action ==" بعدی
end_idx = -1
for i in range(start_idx + 1, len(lines)):
    if 'if action ==' in lines[i] or '# toggle' in lines[i]:
        end_idx = i
        break

if end_idx == -1:
    print("❌ انتهای بلاک پیدا نشد")
    exit(1)

print(f"✅ انتهای بلاک در خط {end_idx + 1}")

# ★ چاپ بلاک قدیمی
print()
print("─── کد قدیمی ───")
for i in range(start_idx, end_idx):
    print(f"  {i+1}: {lines[i].rstrip()}")

# indent رو از خط acc_back بگیر
indent = lines[start_idx][:len(lines[start_idx]) - len(lines[start_idx].lstrip())]
indent_body = indent + "    "

# ★ بلاک جدید
new_block = [
    indent + 'if action == "acc_back":\n',
    indent_body + 'try:\n',
    indent_body + '    await query.message.delete()\n',
    indent_body + 'except Exception:\n',
    indent_body + '    pass\n',
    indent_body + 'return\n',
]

# جایگزینی
new_lines = lines[:start_idx] + new_block + lines[end_idx:]

with open(AC, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print()
print("─── کد جدید ───")
for line in new_block:
    print(f"  {line.rstrip()}")

print()
print(f"✅ {end_idx - start_idx} خط با {len(new_block)} خط جایگزین شد")
PYEOF

echo ""

if python3 -m py_compile "$AC" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$AC.bak_accback_$TS" "$AC"
    exit 1
fi
echo ""

echo "─── چک نهایی: acc_back درست شده؟ ───"
START=$(grep -n 'if action == "acc_back":' "$AC" | head -1 | cut -d: -f1)
sed -n "${START},$((START+6))p" "$AC"
echo ""

echo "─── چک: edit_message_reply_markup چند جا هست؟ ───"
grep -c "edit_message_reply_markup" "$AC"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
