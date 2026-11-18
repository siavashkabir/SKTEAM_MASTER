#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_beauty_$TS"
echo "✅ بک‌آپ: $ST.bak_beauty_$TS"

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    lines = f.readlines()

# پیدا کردن text = ( توی do_refresh
start = -1
for i, line in enumerate(lines):
    if 1590 <= i <= 1630 and 'text = (' in line:
        start = i
        break

if start == -1:
    print("❌ text = پیدا نشد")
    exit(1)

end = -1
for j in range(start + 1, start + 50):
    stripped = lines[j].strip()
    if stripped == ')':
        end = j
        break

if end == -1:
    print("❌ ) پیدا نشد")
    exit(1)

print(f"✅ بازه: خط {start + 1} تا {end + 1}")

# indent
base = lines[start][:len(lines[start]) - len(lines[start].lstrip())]
i1 = base + "    "

# ★ فرمت جدید زیبا
new_block = (
    base + 'text = (\n' +
    i1 + '"╔══════════════════════╗" + NL +\n' +
    i1 + '"║  ⚙️  پیکربندی گروه  ║" + NL +\n' +
    i1 + '"╚══════════════════════╝" + NL +\n' +
    i1 + 'NL +\n' +
    i1 + '"📌 اطلاعات کلی:" + NL +\n' +
    i1 + '"├ 👥 گروه: " + (chat.title or "?") + NL +\n' +
    i1 + '"├ 👑 مالکین: " + str(len(_owner_ids)) + NL +\n' +
    i1 + '"└ 🛡️ ادمین‌ها: " + str(_admin_count) + NL +\n' +
    i1 + 'NL +\n' +
    i1 + '"━━━━━━━━━━━━━━━━━━━━━━" + NL +\n' +
    i1 + '"📋 لیست اعضای گروه:" + NL +\n' +
    i1 + 'details + NL +\n' +
    i1 + '"━━━━━━━━━━━━━━━━━━━━━━" + NL +\n' +
    i1 + 'NL +\n' +
    i1 + '"🕐 " + now + NL +\n' +
    i1 + '"⏳ این پیام تا ۱۵ ثانیه دیگر بسته می‌شود"\n' +
    base + ')\n'
)

new_lines = lines[:start] + [new_block] + lines[end + 1:]

with open(ST, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("✅ فرمت جدید جایگزین شد")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_beauty_$TS" "$ST"
    exit 1
fi
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
