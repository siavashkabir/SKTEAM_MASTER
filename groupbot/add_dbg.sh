#!/data/data/com.termux/files/usr/bin/bash

NSFW=~/groupbot/modules/nsfw.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$NSFW" "$NSFW.bak_dbg_$TS"
echo "✅ بک‌آپ: $NSFW.bak_dbg_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
import re

NSFW = "/data/data/com.termux/files/home/groupbot/modules/nsfw.py"

with open(NSFW, "r", encoding="utf-8") as f:
    content = f.read()

# پیدا کردن تابع check_nsfw
pattern = r'(async def check_nsfw\(update, context\):)(.*?)(?=\nasync def |\ndef |\Z)'
match = re.search(pattern, content, re.DOTALL)

if not match:
    print("❌ check_nsfw پیدا نشد")
    exit(1)

func_header = match.group(1)
func_body = match.group(2)
print(f"✅ check_nsfw پیدا شد ({len(func_body)} کاراکتر)")

# اضافه کردن print برای هر return
# روش ساده: اضافه کردن print بعد از خط print اصلی
new_body = func_body

# قبل از هر "return" یه print بذار که بگه کجای کد بوده
lines = new_body.split('\n')
new_lines = []
marker_count = 0

for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped == 'return' and i > 0:
        # پیدا کردن indent
        indent = line[:len(line) - len(line.lstrip())]
        marker_count += 1
        new_lines.append(indent + f'print("[NSFW-DBG-RET-{marker_count}] at line ~{i+1}")')
    new_lines.append(line)

new_body = '\n'.join(new_lines)

content = content.replace(match.group(0), func_header + new_body, 1)

with open(NSFW, "w", encoding="utf-8") as f:
    f.write(content)

print(f"✅ {marker_count} تا return با print علامت‌گذاری شد")
print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$NSFW" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$NSFW.bak_dbg_$TS" "$NSFW"
    exit 1
fi
echo ""

echo "═══════════════════════════════════════════════════"
echo "🎯 حالا این کارا رو بکن:"
echo ""
echo "1. ری‌استارت:"
echo "   pkill -9 -f 'python3 -u'; sleep 3; rm -f ~/groupbot/.bot.lock; cd ~/groupbot && source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo ""
echo "2. با یه اکانت دیگه یه استیکر بفرست"
echo ""
echo "3. این رو بزن و نتیجه رو بفرست:"
echo "   tail -n 30 ~/groupbot_bot.log | grep NSFW"
echo "═══════════════════════════════════════════════════"
