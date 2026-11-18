#!/data/data/com.termux/files/usr/bin/bash

MW=modules/middleware.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$MW" "$MW.bak_simple_$TS"
echo "✅ بک‌آپ: $MW.bak_simple_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
MW = "/data/data/com.termux/files/home/groupbot/modules/middleware.py"

with open(MW, "r", encoding="utf-8") as f:
    lines = f.readlines()

# پیدا کردن خط "if active:" و "raise ApplicationHandlerStop" توی check_group_active_message
# و بعدش user authorized رو حذف کن

# قدم ۱: پیدا کردن تابع check_group_active_message
start = -1
end = -1
for i, line in enumerate(lines):
    if 'async def check_group_active_message' in line:
        start = i
    elif start >= 0 and line.startswith('async def '):
        end = i
        break
    elif start >= 0 and line.startswith('def ') and 'check_group_active' not in line:
        end = i
        break

if start == -1 or end == -1:
    print(f"❌ تابع پیدا نشد. start={start}, end={end}")
    exit(1)

print(f"تابع از خط {start+1} تا {end}")

# قدم ۲: توی این محدوده، کد user authorized رو حذف کن
# دنبال "if not active:" بگرد، بعدش active رو return کن

new_lines = []
skip_mode = False
modified = False

for i, line in enumerate(lines):
    # توی تابع؟
    if start <= i < end:
        # دنبال "if not active:" بگرد
        if not modified and 'if not active:' in line:
            indent = line[:len(line) - len(line.lstrip())]
            new_lines.append(line)
            new_lines.append(indent + '    raise ApplicationHandlerStop\n')
            # خطوط بعدی رو skip کن: print(...), raise ApplicationHandlerStop, + user authorized part
            skip_mode = True
            modified = True
            continue
        
        # اگه توی skip mode هستیم، خطوط user authorized رو skip کن
        if skip_mode:
            # پایان skip: وقتی به انتهای تابع رسیدیم یا خط مهم دیگه‌ای
            if 'async def ' in line or (line.strip() == '' and i+1 < len(lines) and 'async def ' in lines[i+1]):
                skip_mode = False
                new_lines.append(line)
            # وگرنه skip
            continue
    
    new_lines.append(line)

if not modified:
    print("❌ 'if not active:' پیدا نشد")
    exit(1)

print(f"✅ اصلاح شد — {len(lines) - len(new_lines)} خط حذف")

with open(MW, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$MW" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$MW.bak_simple_$TS" "$MW"
    exit 1
fi
echo ""

echo "─── کد بعد از fix ───"
START=$(grep -n "async def check_group_active_message" "$MW" | head -1 | cut -d: -f1)
sed -n "${START},$((START+50))p" "$MW" | grep -n "if not active:\|if active:\|raise ApplicationHandlerStop\|user authorized\|no active sub"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
