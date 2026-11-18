#!/data/data/com.termux/files/usr/bin/bash

MW=modules/middleware.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$MW" "$MW.bak_mwfix_$TS"
echo "✅ بک‌آپ: $MW.bak_mwfix_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
MW = "/data/data/com.termux/files/home/groupbot/modules/middleware.py"

with open(MW, "r", encoding="utf-8") as f:
    content = f.read()

# مشکل: بعد از "no active sub" و "user not authorized" هردو block می‌شن
# راه‌حل: کد "user not authorized" رو حذف کن — یعنی کاربر عادی هم بتونه پیام بفرسته

# الگوی دقیق رو از عکس دیدم:
old = '''    # اگه کاربر ادمین گروه یا مالک باشه → allow
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

    # اگه کاربر مجاز نباشه → بلاک
    print("[MIDDLEWARE] blocked msg in chat " + str(chat.id) + " (user not authorized)")
    raise ApplicationHandlerStop'''

new = '''    # اگه اشتراک فعاله، پیام رو آزاد بذار
    if active:
        return
    
    # اگه کاربر ادمین گروه یا مالک باشه → allow
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

    # اگه اشتراک فعال نیست و کاربر هم ادمین نیست → بلاک کن
    print("[MIDDLEWARE] blocked msg in chat " + str(chat.id) + " (no active sub & not admin)")
    raise ApplicationHandlerStop'''

if old in content:
    content = content.replace(old, new, 1)
    print("✅ middleware اصلاح شد")
else:
    print("❌ الگو پیدا نشد — دنبال الگوی متفاوت...")
    # تلاش برای پیدا کردن دقیق‌تر
    import re
    pattern = r'# اگه کاربر مجاز نباشه.*?raise ApplicationHandlerStop'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        print("✅ الگو با regex پیدا شد")
        content = content[:match.start()] + '    # اگه اشتراک فعال نیست و کاربر هم ادمین نیست → بلاک کن\n    print("[MIDDLEWARE] blocked msg in chat " + str(chat.id) + " (no active sub & not admin)")\n    raise ApplicationHandlerStop' + content[match.end():]
    else:
        print("❌ بازم پیدا نشد")
        exit(1)

with open(MW, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$MW" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$MW.bak_mwfix_$TS" "$MW"
    exit 1
fi
echo ""

echo "─── چک: منطق جدید ───"
grep -n "if active:\|no active sub & not admin" "$MW"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
