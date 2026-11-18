#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_autoclose_$TS"
echo "✅ بک‌آپ: $ST.bak_autoclose_$TS"

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    lines = f.readlines()

# پیدا کردن اولین `await progress.edit_text(text)` توی do_refresh
target = -1
for i, line in enumerate(lines):
    if 1550 <= i <= 1650 and 'await progress.edit_text(text)' in line:
        target = i
        break

if target == -1:
    print("❌ پیدا نشد")
    exit(1)

print(f"✅ خط {target + 1}")

# indent
indent = lines[target][:len(lines[target]) - len(lines[target].lstrip())]

# اضافه کردن auto-close بعدش
new_code = [
    "\n",
    indent + "# ★ پاک کردن خودکار بعد از ۱۵ ثانیه\n",
    indent + "import asyncio as _aio2\n",
    indent + "async def _auto_del_msg():\n",
    indent + "    await _aio2.sleep(15)\n",
    indent + "    try:\n",
    indent + "        await progress.delete()\n",
    indent + "    except Exception:\n",
    indent + "        pass\n",
    indent + "_aio2.create_task(_auto_del_msg())\n",
]

lines = lines[:target + 1] + new_code + lines[target + 1:]

with open(ST, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("✅ auto-close اضافه شد")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_autoclose_$TS" "$ST"
    exit 1
fi
echo ""

echo "═══ چک ═══"
grep -n "_auto_del_msg" "$ST"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
