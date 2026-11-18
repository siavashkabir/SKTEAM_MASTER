#!/data/data/com.termux/files/usr/bin/bash

source venv/bin/activate

python3 << 'PYEOF'
US = "userbot_service.py"

with open(US, "r", encoding="utf-8") as f:
    content = f.read()

# fix: استفاده از raw ImportChatInvite
old = '''        # ★ لینک کامل رو بدیم به join_chat
        log(f"  لینک: {invite_link}")
        chat = await app.join_chat(invite_link)'''

new = '''        # ★ استخراج hash و استفاده از raw API
        log(f"  لینک: {invite_link}")
        if "+" in invite_link:
            hash_part = invite_link.split("+")[-1].split("/")[0].split("?")[0]
        elif "joinchat" in invite_link:
            hash_part = invite_link.split("joinchat/")[-1].split("/")[0].split("?")[0]
        else:
            hash_part = invite_link.rstrip("/").split("/")[-1].split("?")[0]
        log(f"  hash: {hash_part}")
        
        # raw API
        from pyrogram.raw.functions.messages import ImportChatInvite
        from pyrogram.raw.functions.channels import JoinChannel
        from pyrogram.raw.functions.messages import CheckChatInvite
        
        try:
            # اول check کن
            check = await app.invoke(CheckChatInvite(hash=hash_part))
            log(f"  check: {type(check).__name__}")
            
            # اگه already هست
            if hasattr(check, "chat"):
                chat = check.chat
                chat_id = chat.id
                log(f"  ✅ از قبل عضوه: {getattr(chat, 'title', '?')}")
            else:
                # join کن
                result = await app.invoke(ImportChatInvite(hash=hash_part))
                if hasattr(result, "chats") and result.chats:
                    chat = result.chats[0]
                    log(f"  ✅ join موفق: {getattr(chat, 'title', '?')}")
                else:
                    log(f"  ⚠️ نتیجه: {result}")
        except Exception as _e:
            # احتمالاً از قبل عضو شده
            err_msg = str(_e)
            if "USER_ALREADY_PARTICIPANT" in err_msg:
                log(f"  ✅ از قبل عضوه")
            else:
                raise _e'''

if old in content:
    content = content.replace(old, new, 1)
    print("✅ join_chat با raw API")
else:
    print("⚠️ الگو پیدا نشد")
    idx = content.find("# ★ لینک کامل")
    if idx > 0:
        print(content[idx:idx+300])
    exit(1)

with open(US, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile userbot_service.py 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا"
    exit 1
fi
echo ""

# ری‌استارت + پاک کردن queue
pkill -9 -f "userbot_service.py" 2>/dev/null
sleep 2

python3 -c "
import sqlite3
from config import DATABASE_PATH
conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()
c.execute('DELETE FROM userbot_join_queue')
conn.commit()
conn.close()
print('✅ queue پاک شد')
"

nohup python3 -u userbot_service.py > ~/userbot_service.log 2>&1 &
sleep 8

echo ""
echo "─── لاگ ───"
tail -n 15 ~/userbot_service.log

echo ""
echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 حالا:"
echo "python3 trigger_autojoin.py"
echo ""
echo "بعد ۱۵ ثانیه:"
echo "tail -n 40 ~/userbot_service.log"
echo "═══════════════════════════════════════════════════"
