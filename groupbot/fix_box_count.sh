#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_box_$TS"
echo "✅ بک‌آپ: $ST.bak_box_$TS"

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    lines = f.readlines()

# ═══ ۱. پیدا کردن text = توی do_refresh و جایگزینی ═══
start = -1
for i, line in enumerate(lines):
    if 1590 <= i <= 1650 and 'text = (' in line:
        start = i
        break

if start == -1:
    print("❌ text = پیدا نشد")
    exit(1)

end = -1
for j in range(start + 1, start + 50):
    if lines[j].strip() == ')':
        end = j
        break

if end == -1:
    print("❌ ) پیدا نشد")
    exit(1)

print(f"✅ text: خط {start + 1} تا {end + 1}")

base = lines[start][:len(lines[start]) - len(lines[start].lstrip())]
i1 = base + "    "

# فرمت جدید — با کادر ساده
new_text_block = (
    base + 'text = (\n' +
    i1 + '"━━━━━━━━━━━━━━━━━━━━" + NL +\n' +
    i1 + '"     ⚙️  پیکربندی گروه" + NL +\n' +
    i1 + '"━━━━━━━━━━━━━━━━━━━━" + NL +\n' +
    i1 + 'NL +\n' +
    i1 + '"📌 اطلاعات کلی:" + NL +\n' +
    i1 + '"├ 👥 گروه: " + (chat.title or "?") + NL +\n' +
    i1 + '"├ 👑 مالکین: " + str(len(_owner_ids)) + NL +\n' +
    i1 + '"└ 🛡️ ادمین‌ها: " + str(sum(1 for _l in lines if "🛡️" in _l or "🤖" in _l)) + NL +\n' +
    i1 + 'NL +\n' +
    i1 + '"━━━━━━━━━━━━━━━━━━━━" + NL +\n' +
    i1 + '"📋 لیست اعضا:" + NL +\n' +
    i1 + 'details + NL +\n' +
    i1 + '"━━━━━━━━━━━━━━━━━━━━" + NL +\n' +
    i1 + 'NL +\n' +
    i1 + '"🕐 " + now + NL +\n' +
    i1 + '"⏳ این پیام تا ۳۰ ثانیه دیگر بسته می‌شود"\n' +
    base + ')\n'
)

# جایگزینی
new_lines = lines[:start] + [new_text_block] + lines[end + 1:]

with open(ST, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("✅ کادر و شمارش درست شد")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_box_$TS" "$ST"
    exit 1
fi
echo ""

echo "═══ چک ═══"
grep -n "پیکربندی گروه\|sum(1 for _l in lines" "$ST"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
