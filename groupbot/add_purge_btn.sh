#!/data/data/com.termux/files/usr/bin/bash

PU=modules/purge.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$PU" "$PU.bak_btn_$TS"
echo "✅ بک‌آپ: $PU.bak_btn_$TS"

source venv/bin/activate

python3 << 'PYEOF'
PU = "/data/data/com.termux/files/home/groupbot/modules/purge.py"

with open(PU, "r", encoding="utf-8") as f:
    content = f.read()

# پیدا کردن دکمه close که آخر منو هست
old_btn = '''keyboard.append([InlineKeyboardButton("🔙 بستن", callback_data="menu_close:" + str(uid))])
    return InlineKeyboardMarkup(keyboard)'''

new_btn = '''keyboard.append([InlineKeyboardButton("🗑️ شروع پاکسازی (۱۰۰ پیام)", callback_data="purge_start:" + str(uid) + ":100")])
    keyboard.append([InlineKeyboardButton("🗑️ شروع پاکسازی (۵۰۰ پیام)", callback_data="purge_start:" + str(uid) + ":500")])
    keyboard.append([InlineKeyboardButton("🗑️ شروع پاکسازی (۱۰۰۰ پیام)", callback_data="purge_start:" + str(uid) + ":1000")])
    keyboard.append([InlineKeyboardButton("🔙 بستن", callback_data="menu_close:" + str(uid))])
    return InlineKeyboardMarkup(keyboard)'''

if old_btn in content:
    content = content.replace(old_btn, new_btn, 1)
    print("✅ دکمه شروع اضافه شد")
else:
    print("❌ الگوی دکمه پیدا نشد")
    # دیاگ — آخر تابع purge_menu رو چاپ کن
    idx = content.find("def purge_menu")
    if idx > 0:
        end = content.find("async def handler", idx)
        print("context آخر purge_menu:")
        print(content[end-300:end])
    exit(1)

# ★ حالا case purge_start توی handler
# پیدا کردن if action == "purge_menu":
old_case = '''if action == "purge_menu":'''
# اینجا case جدید رو قبلش اضافه می‌کنیم
new_case = '''if action.startswith("purge_start:"):
        count = int(action.split(":")[1]) if ":" in action else 100
        await query.answer()
        msg_id = query.message.message_id
        try:
            deleted = await do_purge(chat_id, msg_id, count, context.bot)
            try:
                await query.message.delete()
            except Exception:
                pass
            import asyncio as _aio
            info = await context.bot.send_message(
                chat_id=chat_id,
                text=f"🗑️ {deleted} پیام پاک شد."
            )
            async def _del_later():
                await _aio.sleep(5)
                try:
                    await info.delete()
                except Exception:
                    pass
            _aio.create_task(_del_later())
        except Exception as _e:
            print(f"[PURGE ERR] {_e}")
        return

    if action == "purge_menu":'''

if old_case in content:
    content = content.replace(old_case, new_case, 1)
    print("✅ case purge_start اضافه شد")
else:
    print("❌ purge_menu پیدا نشد")

with open(PU, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$PU" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$PU.bak_btn_$TS" "$PU"
    python3 -m py_compile "$PU" 2>&1 | head -5
    exit 1
fi
echo ""

echo "═══ چک ═══"
grep -n "purge_start" "$PU"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
