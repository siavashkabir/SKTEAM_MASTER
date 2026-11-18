#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_purgepersian_$TS"
echo "✅ بک‌آپ: $ST.bak_purgepersian_$TS"

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    lines = f.readlines()

# پیدا کردن داخل persian_handler — بعد از print("[PERSIAN] got: ")
target = -1
for i, line in enumerate(lines):
    if 'print("[PERSIAN] got: " + text)' in line:
        target = i
        break

if target == -1:
    print("❌ پیدا نشد")
    exit(1)

print(f"✅ خط {target + 1}")

# indent پایه
indent = "    "

# کد جدید — هندلر پاکسازی با اعداد فارسی
new_code = '''    # ★ هندلر پاکسازی (حذف 100 / شروع پاکسازی 50)
    import re as _re_p
    _persian_digits = {"۰": "0", "۱": "1", "۲": "2", "۳": "3", "۴": "4", "۵": "5", "۶": "6", "۷": "7", "۸": "8", "۹": "9"}
    _text_for_purge = text
    for _pd, _ed in _persian_digits.items():
        _text_for_purge = _text_for_purge.replace(_pd, _ed)
    _purge_match = _re_p.match(r'^(حذف|شروع پاکسازی|پاکسازی)\\s+(\\d+)$', _text_for_purge.strip())
    if _purge_match:
        try:
            _count = int(_purge_match.group(2))
            if _count < 1 or _count > 1000:
                await msg.reply_text("❌ عدد باید بین ۱ تا ۱۰۰۰ باشه.")
                return
            _chat = update.effective_chat
            _usr = update.effective_user
            try:
                _member = await _chat.get_member(_usr.id)
                if _member.status not in ("creator", "administrator"):
                    await msg.reply_text("❌ فقط ادمین‌ها می‌تونن پاکسازی کنن.")
                    return
            except Exception:
                pass
            try:
                await msg.delete()
            except Exception:
                pass
            _deleted = 0
            _msg_id = msg.message_id
            _ids = list(range(_msg_id, max(0, _msg_id - _count), -1))
            for _i in range(0, len(_ids), 100):
                _chunk = _ids[_i:_i+100]
                try:
                    await context.bot.delete_messages(_chat.id, _chunk)
                    _deleted += len(_chunk)
                except Exception as _e:
                    print(f"[PURGE P] chunk err: {_e}")
                    for _mid in _chunk:
                        try:
                            await context.bot.delete_message(_chat.id, _mid)
                            _deleted += 1
                        except Exception:
                            pass
            _info = await context.bot.send_message(_chat.id, f"🗑️ {_deleted} پیام پاک شد.")
            import asyncio as _aio_p
            async def _del_later_pp():
                await _aio_p.sleep(5)
                try:
                    await _info.delete()
                except Exception:
                    pass
            _aio_p.create_task(_del_later_pp())
            print(f"[PURGE PERSIAN] {_deleted} پیام پاک شد توسط {_usr.id}")
            return
        except Exception as _e:
            print(f"[PURGE PERSIAN ERR] {_e}")
            return

'''

lines = lines[:target + 1] + [new_code] + lines[target + 1:]

with open(ST, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("✅ هندلر به persian_handler اضافه شد")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_purgepersian_$TS" "$ST"
    exit 1
fi
echo ""

echo "═══ چک ═══"
grep -n "PURGE PERSIAN" "$ST"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo ""
echo "بعد توی تلگرام بنویس:"
echo "  «حذف 50» یا «حذف ۵۰»"
echo "═══════════════════════════════════════════════════"
