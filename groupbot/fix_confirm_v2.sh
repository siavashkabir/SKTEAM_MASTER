#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$AC" "$AC.bak_confirm_v2_$TS"
echo "✅ بک‌آپ: $AC.bak_confirm_v2_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
import re

AC = "/data/data/com.termux/files/home/groupbot/modules/access.py"

with open(AC, "r", encoding="utf-8") as f:
    content = f.read()

# ═══ قدم ۱: برگردون handler acc_confirm به acc_back ═══
old_handler = '''    if action == "acc_confirm":
        chat_id = int(parts[2]) if len(parts) > 2 else query.message.chat_id
        target_id = int(parts[3]) if len(parts) > 3 else None
        was_changed = ACCESS_CHANGED.pop((chat_id, target_id), False)
        
        try:
            await query.message.delete()
        except Exception:
            pass
        
        try:
            if was_changed:
                msg = await context.bot.send_message(
                    chat_id=chat_id,
                    text="✅ تغییرات با موفقیت اعمال شد."
                )
            else:
                msg = await context.bot.send_message(
                    chat_id=chat_id,
                    text="ℹ️ تغییری اعمال نشد."
                )
            async def _auto_del(m):
                await asyncio.sleep(5)
                try:
                    await m.delete()
                except Exception:
                    pass
            asyncio.create_task(_auto_del(msg))
        except Exception as e:
            print("[ACCESS CONFIRM MSG ERR] " + str(e))
        return'''

new_handler = '''    if action == "acc_back":
        try:
            await query.message.delete()
        except Exception:
            pass
        return'''

if old_handler in content:
    content = content.replace(old_handler, new_handler, 1)
    print("✅ handler برگشت به acc_back")
else:
    print("⚠️ handler acc_confirm پیدا نشد")

# ═══ قدم ۲: دکمه‌ها با regex ═══
# pattern انعطاف‌پذیر
pattern = r'keyboard\.append\(\[InlineKeyboardButton\("[^"]*", callback_data="acc_back:" \+ str\(uid\) \+ ":" \+ str\(chat_id\)\)\]\)'
replacement = 'keyboard.append([InlineKeyboardButton("✅ تایید و بستن", callback_data="acc_confirm:" + str(uid) + ":" + str(chat_id) + ":" + str(target_id))])'

matches = re.findall(pattern, content)
print(f"✅ {len(matches)} تا دکمه acc_back پیدا شد")
content = re.sub(pattern, replacement, content)

# ═══ قدم ۳: handler acc_back → acc_confirm با منطق پیام ═══
old_h = '''    if action == "acc_back":
        try:
            await query.message.delete()
        except Exception:
            pass
        return'''

new_h = '''    if action == "acc_confirm":
        chat_id = int(parts[2]) if len(parts) > 2 else query.message.chat_id
        target_id = int(parts[3]) if len(parts) > 3 else None
        was_changed = ACCESS_CHANGED.pop((chat_id, target_id), False)
        
        try:
            await query.message.delete()
        except Exception:
            pass
        
        try:
            if was_changed:
                msg = await context.bot.send_message(
                    chat_id=chat_id,
                    text="✅ تغییرات با موفقیت اعمال شد."
                )
            else:
                msg = await context.bot.send_message(
                    chat_id=chat_id,
                    text="ℹ️ تغییری اعمال نشد."
                )
            async def _auto_del(m):
                await asyncio.sleep(5)
                try:
                    await m.delete()
                except Exception:
                    pass
            asyncio.create_task(_auto_del(msg))
        except Exception as e:
            print("[ACCESS CONFIRM MSG ERR] " + str(e))
        return'''

if old_h in content:
    content = content.replace(old_h, new_h, 1)
    print("✅ handler acc_confirm اضافه شد")
else:
    print("⚠️ handler acc_back برای تغییر پیدا نشد")

with open(AC, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$AC" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$AC.bak_confirm_v2_$TS" "$AC"
    exit 1
fi
echo ""

echo "─── چک نهایی ───"
echo "acc_confirm (دکمه): $(grep -c 'acc_confirm' "$AC")"
echo "acc_back (باقی‌مونده): $(grep -c 'acc_back' "$AC")"
echo "ACCESS_CHANGED: $(grep -c 'ACCESS_CHANGED' "$AC")"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
