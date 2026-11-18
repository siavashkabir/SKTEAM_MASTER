#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$AC" "$AC.bak_fix2_$TS"
echo "✅ بک‌آپ: $AC.bak_fix2_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
import re

AC = "/data/data/com.termux/files/home/groupbot/modules/access.py"

with open(AC, "r", encoding="utf-8") as f:
    content = f.read()

# ★ FIX: acc_back رو برگردون به حالت اصلی (delete)
# الگوی فعلی acc_back (بعد از fix اشتباه):
old_acc_back = '''if action == "acc_back":
    # ★ منو رو آپدیت کن (نه delete)
    try:
        member = await chat.get_member(target_id)
        target_name = member.user.first_name or "کاربر"
    except Exception:
        target_name = "کاربر"
    t_role = get_target_role(chat_id, target_id)
    v_owner = await is_bot_owner_or_admin(clicker)
    new_menu = build_access_menu(clicker, chat_id, target_id, target_name, t_role, v_owner)
    try:
        await query.edit_message_reply_markup(reply_markup=new_menu)
    except Exception as e:
        print("[ACCESS EDIT ERR] " + str(e))
    return'''

new_acc_back = '''if action == "acc_back":
    try:
        await query.message.delete()
    except Exception:
        pass
    return'''

if old_acc_back in content:
    content = content.replace(old_acc_back, new_acc_back, 1)
    print("✅ acc_back به حالت اصلی برگشت")
else:
    print("⚠️ acc_back با الگوی دقیق پیدا نشد — تلاش با regex")
    # regex برای پیدا کردن acc_back
    pattern = r'if action == "acc_back":.*?return\n'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        content = content.replace(match.group(0), '''if action == "acc_back":
    try:
        await query.message.delete()
    except Exception:
        pass
    return
''', 1)
        print("✅ acc_back با regex برگشت")
    else:
        print("❌ پیدا نشد — دستی باید بررسی بشه")

with open(AC, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

# ★ دیاگ: چک کن acc_back درست شده
echo "─── acc_back بعد از fix ───"
START=$(grep -n 'if action == "acc_back":' "$AC" | head -1 | cut -d: -f1)
if [ -n "$START" ]; then
    sed -n "${START},$((START+7))p" "$AC"
fi
echo ""

# کامپایل
if python3 -m py_compile "$AC" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$AC.bak_fix2_$TS" "$AC"
    exit 1
fi
echo ""

# ★ دیاگ: توی acc_dp_، خط debug اضافه کن که ببینیم چی می‌شه
python3 << 'PYEOF'
AC = "/data/data/com.termux/files/home/groupbot/modules/access.py"

with open(AC, "r", encoding="utf-8") as f:
    content = f.read()

# اضافه کردن debug به ابتدای access_cb_handler
old = '''async def access_cb_handler(update, context):
    query = update.callback_query
    data = query.data
    clicker = query.from_user.id'''

new = '''async def access_cb_handler(update, context):
    query = update.callback_query
    data = query.data
    clicker = query.from_user.id
    print(f"[ACCESS DBG] callback={data} clicker={clicker}")'''

if old in content:
    content = content.replace(old, new, 1)
    print("✅ debug اضافه شد")
else:
    print("⚠️ debug اضافه نشد")

with open(AC, "w", encoding="utf-8") as f:
    f.write(content)
PYEOF

echo ""

if python3 -m py_compile "$AC" 2>&1; then
    echo "✅ کامپایل نهایی OK"
else
    echo "❌ خطا"
    exit 1
fi
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo ""
echo "بعد از ری‌استارت، توی ترموکس این رو بزن:"
echo "tail -f ~/groupbot_bot.log"
echo ""
echo "بعد توی تلگرام:"
echo "1. «دسترسی» رو بزن"
echo "2. یه دکمه toggle رو بزن"
echo "3. توی ترمینال لاگ رو ببین"
echo ""
echo "باید ببینی:"
echo "  [ACCESS DBG] callback=acc_dp_xxx..."
echo "  [ACCESS EDIT ERR] ... (اگه خطا داشت)"
echo "═══════════════════════════════════════════════════"
