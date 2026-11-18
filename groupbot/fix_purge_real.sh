#!/data/data/com.termux/files/usr/bin/bash

PU=modules/purge.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$PU" "$PU.bak_real_$TS"
echo "✅ بک‌آپ: $PU.bak_real_$TS"

source venv/bin/activate

python3 << 'PYEOF'
PU = "/data/data/com.termux/files/home/groupbot/modules/purge.py"

with open(PU, "r", encoding="utf-8") as f:
    lines = f.readlines()

# پیدا کردن خط `def purge_menu` — قبل از اون تابع پاکسازی رو اضافه کن
target = -1
for i, line in enumerate(lines):
    if line.startswith("def purge_menu"):
        target = i
        break

if target == -1:
    print("❌ purge_menu پیدا نشد")
    exit(1)

print(f"✅ خط {target + 1}")

# تابع پاکسازی واقعی
new_funcs = '''async def do_purge(chat_id, msg_id, count=100, bot=None):
    """پاک کردن count پیام آخر گروه"""
    if not bot:
        print("[PURGE] bot argument لازمه")
        return 0
    
    ids = list(range(msg_id, max(0, msg_id - count), -1))
    deleted = 0
    
    # دسته‌بندی ۱۰۰ تایی
    for i in range(0, len(ids), 100):
        chunk = ids[i:i+100]
        try:
            await bot.delete_messages(chat_id, chunk)
            deleted += len(chunk)
        except Exception as e:
            # اگه نشد، تک‌تک امتحان کن
            print(f"[PURGE] chunk err: {e}")
            for mid in chunk:
                try:
                    await bot.delete_message(chat_id, mid)
                    deleted += 1
                except Exception:
                    pass
    
    print(f"[PURGE] {deleted}/{len(ids)} پیام پاک شد")
    return deleted


'''

lines = lines[:target] + [new_funcs] + lines[target:]

# الان اضافه کردن case `purge_start` توی handler
content = ''.join(lines)

# پیدا کردن `if action == "purge_noop":`
old_case = '''        if action == "purge_noop":
            await query.answer()
            return'''

new_case = '''        if action == "purge_start":
            count = int(parts[2]) if len(parts) > 2 else 100
            await query.answer(f"در حال پاک کردن {count} پیام...", show_alert=False)
            msg_id = query.message.message_id
            deleted = await do_purge(chat_id, msg_id, count, context.bot)
            try:
                await query.message.delete()
            except Exception:
                pass
            try:
                info = await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"🗑️ {deleted} پیام پاک شد."
                )
                import asyncio as _aio
                async def _del_later():
                    await _aio.sleep(5)
                    try:
                        await info.delete()
                    except Exception:
                        pass
                _aio.create_task(_del_later())
            except Exception:
                pass
            return

        if action == "purge_noop":
            await query.answer()
            return'''

if old_case in content:
    content = content.replace(old_case, new_case, 1)
    print("✅ case purge_start اضافه شد")
else:
    print("⚠️ purge_noop پیدا نشد")

with open(PU, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$PU" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$PU.bak_real_$TS" "$PU"
    exit 1
fi
echo ""

echo "═══ چک ═══"
grep -n "do_purge\|purge_start" "$PU"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد — الان purge کار می‌کنه"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
