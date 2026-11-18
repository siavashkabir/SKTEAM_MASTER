#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_autosave_$TS"
echo "✅ بک‌آپ: $ST.bak_autosave_$TS"

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    content = f.read()

# ★ اضافه کردن auto-save توی persian_handler یا یه جای مرکزی
# بهترین جا: بعد از `_uid_rm = update.effective_user.id` توی persian_handler

old = '''    _uid_rm = update.effective_user.id
    except Exception:
        _uid_rm = None'''

new = '''    _uid_rm = update.effective_user.id
    except Exception:
        _uid_rm = None
    
    # ★ auto-save ادمین‌ها توی دیتابیس
    try:
        from database import is_admin, add_admin_to_db
        _msg = update.effective_message
        _chat = update.effective_chat
        if _msg and _chat and _chat.type in ("group", "supergroup") and _msg.from_user:
            _uid = _msg.from_user.id
            _fname = _msg.from_user.first_name or "?"
            # چک کن ادمین تلگرامه
            if _uid != context.bot.id:
                try:
                    _member = await context.bot.get_chat_member(_chat.id, _uid)
                    if _member.status in ("creator", "administrator"):
                        # اگه توی دیتابیس نیست، اضافه کن
                        if not is_admin(_chat.id, _uid):
                            add_admin_to_db(_chat.id, _uid, _fname)
                            print(f"[AUTO-SAVE ADMIN] {_fname} ({_uid}) in {_chat.id}")
                except Exception:
                    pass
    except Exception as _e:
        print(f"[AUTO-SAVE ERR] {_e}")'''

if old in content:
    content = content.replace(old, new, 1)
    print("✅ auto-save اضافه شد")
else:
    print("❌ الگو پیدا نشد")
    idx = content.find("_uid_rm = update.effective_user.id")
    if idx > 0:
        print("context:")
        print(content[idx-100:idx+200])
    exit(1)

with open(ST, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_autosave_$TS" "$ST"
    exit 1
fi
echo ""

echo "═══ چک ═══"
grep -n "AUTO-SAVE ADMIN" "$ST"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo ""
echo "بعد توی گروه HERITAGE:"
echo "1. از ۴-۵ ادمین بخواه یه پیام بفرستن"
echo "2. ادمین‌ها auto-save می‌شن"
echo "3. «پیکربندی» بزن — باید ببینی"
echo "═══════════════════════════════════════════════════"
