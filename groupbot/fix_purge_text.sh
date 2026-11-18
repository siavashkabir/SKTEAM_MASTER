#!/data/data/com.termux/files/usr/bin/bash

RP=modules/reply.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$RP" "$RP.bak_purgetext_$TS"
echo "✅ بک‌آپ: $RP.bak_purgetext_$TS"

source venv/bin/activate

python3 << 'PYEOF'
RP = "/data/data/com.termux/files/home/groupbot/modules/reply.py"

with open(RP, "r", encoding="utf-8") as f:
    lines = f.readlines()

# پیدا کردن خط "if t_low_clean in" یا پایان تابع reply_handler
# بهترین جا: قبل از `# [MOD-INLINE]`
target = -1
for i, line in enumerate(lines):
    if "# [MOD-INLINE]" in line:
        target = i
        break

if target == -1:
    # تلاش دیگه: پیدا کردن `async def reply_handler`
    for i, line in enumerate(lines):
        if "async def reply_handler" in line:
            target = i + 20  # بیست خط بعد
            break

if target == -1:
    print("❌ پیدا نشد")
    exit(1)

print(f"✅ خط {target + 1}")

# indent پایه (داخل تابع)
indent = "    "

# کد جدید — هندلر پاکسازی
new_code = '''    # ★ هندلر پاکسازی (شروع پاکسازی ۱۰۰ / حذف ۱۰۰)
    import re as _re
    _purge_match = _re.match(r'^(شروع پاکسازی|حذف|پاکسازی)\\s+(\\d+)$', text_low.strip())
    if _purge_match:
        try:
            _count = int(_purge_match.group(2))
            if _count < 1 or _count > 1000:
                await msg.reply_text("❌ عدد باید بین ۱ تا ۱۰۰۰ باشه.")
                return
            # چک ادمین
            try:
                _member = await chat.get_member(user.id)
                if _member.status not in ("creator", "administrator"):
                    await msg.reply_text("❌ فقط ادمین‌ها می‌تونن پاکسازی کنن.")
                    return
            except Exception:
                pass
            # حذف پیام دستور
            try:
                await msg.delete()
            except Exception:
                pass
            # پاک کردن count پیام
            _deleted = 0
            _msg_id = msg.message_id
            _ids = list(range(_msg_id, max(0, _msg_id - _count), -1))
            for _i in range(0, len(_ids), 100):
                _chunk = _ids[_i:_i+100]
                try:
                    await context.bot.delete_messages(chat.id, _chunk)
                    _deleted += len(_chunk)
                except Exception as _e:
                    print(f"[PURGE TEXT] chunk err: {_e}")
                    for _mid in _chunk:
                        try:
                            await context.bot.delete_message(chat.id, _mid)
                            _deleted += 1
                        except Exception:
                            pass
            # پیام تایید
            _info = await context.bot.send_message(chat.id, f"🗑️ {_deleted} پیام پاک شد.")
            import asyncio as _aio
            async def _del_later_p():
                await _aio.sleep(5)
                try:
                    await _info.delete()
                except Exception:
                    pass
            _aio.create_task(_del_later_p())
            print(f"[PURGE TEXT] {_deleted} پیام پاک شد توسط {user.id}")
            return
        except Exception as _e:
            print(f"[PURGE TEXT ERR] {_e}")
            return

'''

lines = lines[:target] + [new_code] + lines[target:]

with open(RP, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("✅ هندلر اضافه شد")
PYEOF

echo ""

if python3 -m py_compile "$RP" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$RP.bak_purgetext_$TS" "$RP"
    exit 1
fi
echo ""

echo "═══ چک ═══"
grep -n "PURGE TEXT\|شروع پاکسازی" "$RP"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo ""
echo "بعد توی تلگرام:"
echo "  «حذف 100» یا «شروع پاکسازی 100»"
echo "═══════════════════════════════════════════════════"
