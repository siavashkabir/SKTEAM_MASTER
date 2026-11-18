#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_pmperms_$TS"
echo "✅ بک‌آپ: $ST.bak_pmperms_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    content = f.read()

# پیدا کردن بخش pm_confirm
old = '''        # ارتقا در تلگرام
        try:
            from modules.admin import add_admin_to_db
            add_admin_to_db(chat_id, target_id, "Admin")
        except ImportError:
            from database import add_admin_to_db
            add_admin_to_db(chat_id, target_id, "Admin")
        
        await query.answer("✅ کاربر با موفقیت به عنوان مدیر گروه ارتقا یافت.", show_alert=True)'''

new = '''        # ارتقا در تلگرام
        try:
            from modules.admin import add_admin_to_db
            add_admin_to_db(chat_id, target_id, "Admin")
        except ImportError:
            from database import add_admin_to_db
            add_admin_to_db(chat_id, target_id, "Admin")
        
        # ★ ذخیره perms در admin_permissions
        try:
            from database import set_admin_perm
            perms = PROMOTE_WAIT[uid].get("perms", {})
            print(f"[PM_CONFIRM] ذخیره {len(perms)} perm برای user {target_id}")
            for perm_name, enabled in perms.items():
                set_admin_perm(chat_id, target_id, "admin", perm_name, 1 if enabled else 0)
                print(f"  ✅ {perm_name} = {enabled}")
        except Exception as e:
            print(f"[PM_CONFIRM PERMS ERR] {e}")
            import traceback
            traceback.print_exc()
        
        # پاک کردن state
        try:
            del PROMOTE_WAIT[uid]
        except Exception:
            pass
        
        await query.answer("✅ کاربر با موفقیت به عنوان مدیر گروه ارتقا یافت.", show_alert=True)'''

if old in content:
    content = content.replace(old, new, 1)
    print("✅ pm_confirm اصلاح شد — perms ذخیره می‌شن")
else:
    print("❌ الگو پیدا نشد — تلاش با regex")
    import re
    pattern = r'# ارتقا در تلگرام\s*\n\s*try:\s*\n\s*from modules\.admin import add_admin_to_db.*?await query\.answer\("✅ کاربر با موفقیت به عنوان مدیر گروه ارتقا یافت\.", show_alert=True\)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        content = content.replace(match.group(0), new, 1)
        print("✅ با regex اصلاح شد")
    else:
        print("❌ پیدا نشد")
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
    cp "$ST.bak_pmperms_$TS" "$ST"
    exit 1
fi
echo ""

echo "─── چک ───"
grep -n "set_admin_perm" "$ST"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
