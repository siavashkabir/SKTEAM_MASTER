#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_debugt_$TS"
echo "✅ بک‌آپ: $ST.bak_debugt_$TS"

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    lines = f.readlines()

# پیدا کردن pm_toggle handler
target_idx = -1
for i, line in enumerate(lines):
    if 'if action.startswith("pm_toggle_"):' in line:
        target_idx = i
        break

if target_idx == -1:
    print("❌ pm_toggle پیدا نشد")
    exit(1)

print(f"✅ خط pm_toggle: {target_idx + 1}")

# اضافه کردن debug بعد از if perm_name in PROMOTE_WAIT[uid]["perms"]:
# پیدا کردن خط `perm_name = action.replace("pm_toggle_", "")`
for j in range(target_idx, target_idx + 20):
    if 'perm_name = action.replace("pm_toggle_", "")' in lines[j]:
        indent = lines[j][:len(lines[j]) - len(lines[j].lstrip())]
        # اضافه کردن debug بعد از این خط
        debug_lines = [
            indent + 'print(f"[PM_TOGGLE] uid={uid}, perm_name={perm_name}")\n',
            indent + 'print(f"[PM_TOGGLE] uid in PROMOTE_WAIT = {uid in PROMOTE_WAIT}")\n',
            indent + 'if uid in PROMOTE_WAIT:\n',
            indent + '    print(f"[PM_TOGGLE] perms before = {PROMOTE_WAIT[uid].get(\'perms\', {})}")\n',
        ]
        lines = lines[:j+1] + debug_lines + lines[j+1:]
        print(f"✅ debug به خط {j+1} اضافه شد")
        break

with open(ST, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_debugt_$TS" "$ST"
    exit 1
fi
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Debug اضافه شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo ""
echo "بعد توی تلگرام:"
echo "1. روی کاربر ریپلای کن"
echo "2. «افزودن مدیر»"
echo "3. یه تیک بزن"
echo "4. تایید"
echo ""
echo "بعد این رو بزن و نتیجه رو بفرست:"
echo "tail -n 100 ~/groupbot_bot.log | grep PM_TOGGLE"
echo "═══════════════════════════════════════════════════"
