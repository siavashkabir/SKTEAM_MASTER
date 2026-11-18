#!/data/data/com.termux/files/usr/bin/bash

MW=modules/middleware.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$MW" "$MW.bak_final_$TS"
echo "✅ بک‌آپ: $MW.bak_final_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
import re

MW = "/data/data/com.termux/files/home/groupbot/modules/middleware.py"

with open(MW, "r", encoding="utf-8") as f:
    content = f.read()

# پیدا کردن تابع check_group_active_message تا قبل از check_group_active_callback
pattern = r'(async def check_group_active_message\(update, context\):.*?)(?=\nasync def check_group_active_callback)'
match = re.search(pattern, content, re.DOTALL)

if not match:
    print("❌ تابع پیدا نشد")
    exit(1)

old_func = match.group(1)
print(f"قدیمی: {len(old_func)} کاراکتر")

# تابع جدید و درست
new_func = '''async def check_group_active_message(update, context):
    """Middleware - چک اشتراک گروه برای پیام"""
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    
    if not chat:
        return
    if chat.type not in ("group", "supergroup"):
        return
    
    # 1. Owner یا sudo → allow
    try:
        if user and (user.id == OWNER_ID or is_bot_admin(user.id)):
            return
    except Exception:
        pass
    
    # 2. چک groups + subscriptions
    active = False
    import sqlite3
    from config import DATABASE_PATH
    from datetime import datetime
    
    DATE_FORMATS = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M")
    
    def is_future_date(date_str):
        if not date_str:
            return True
        for fmt in DATE_FORMATS:
            try:
                return datetime.strptime(date_str, fmt) > datetime.now()
            except Exception:
                continue
        return False
    
    # چک groups
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("SELECT expire_date, enabled FROM groups WHERE chat_id=?", (chat.id,))
        row = c.fetchone()
        conn.close()
        if row:
            exp_date, enabled = row
            if enabled and is_future_date(exp_date):
                active = True
    except Exception as e:
        print("[MIDDLEWARE GRP CHK ERR] " + str(e))
    
    # چک subscriptions
    if not active:
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            c = conn.cursor()
            c.execute("SELECT sub_type, expire_date, enabled FROM subscriptions WHERE chat_id=?", (chat.id,))
            rows = c.fetchall()
            conn.close()
            for row in rows:
                sub_type, exp_date, enabled = row
                if enabled and is_future_date(exp_date):
                    active = True
                    print("[MIDDLEWARE] active via sub " + str(sub_type))
                    break
        except Exception as e:
            print("[MIDDLEWARE SUB CHK ERR] " + str(e))
    
    # 3. اگه اشتراک فعاله → allow (NSFW و بقیه پیام رو بگیرن)
    if active:
        return
    
    # 4. اگه کاربر ادمین گروه یا مالک باشه → allow
    try:
        from database import is_group_owner
        if is_group_owner(chat.id, user.id):
            return
    except Exception as e:
        print("[MIDDLEWARE ROLE ERR] " + str(e))
    
    try:
        member = await chat.get_member(user.id)
        if member.status in ("creator", "administrator"):
            return
    except Exception as e:
        print("[MIDDLEWARE MEMBER ERR] " + str(e))
    
    # 5. کاربر عادی + اشتراک غیرفعال → بلاک
    print("[MIDDLEWARE] blocked msg in chat " + str(chat.id) + " (no active sub & not admin)")
    raise ApplicationHandlerStop

'''

content = content.replace(old_func, new_func, 1)
print(f"جدید: {len(new_func)} کاراکتر")
print("✅ تابع بازنویسی شد")

with open(MW, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$MW" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$MW.bak_final_$TS" "$MW"
    exit 1
fi
echo ""

echo "─── تست منطق ───"
source venv/bin/activate
python3 << 'PYEOF'
import sqlite3
from config import DATABASE_PATH
from datetime import datetime

DATE_FORMATS = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M")

def is_future_date(date_str):
    if not date_str:
        return True
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(date_str, fmt) > datetime.now()
        except: continue
    return False

for chat_id in [-1004349813270, -100191141484]:
    print(f"=== chat {chat_id} ===")
    active = False
    
    # groups
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT expire_date, enabled FROM groups WHERE chat_id=?", (chat_id,))
    row = c.fetchone()
    conn.close()
    if row:
        exp_date, enabled = row
        print(f"  groups: exp={exp_date}, enabled={enabled}, future={is_future_date(exp_date)}")
        if enabled and is_future_date(exp_date):
            active = True
    
    # subscriptions
    if not active:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("SELECT sub_type, expire_date, enabled FROM subscriptions WHERE chat_id=?", (chat_id,))
        rows = c.fetchall()
        conn.close()
        for row in rows:
            sub_type, exp_date, enabled = row
            if enabled and is_future_date(exp_date):
                active = True
                print(f"  ✅ active via {sub_type}")
                break
    
    print(f"  نتیجه: active={active}")
    print()
PYEOF
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
