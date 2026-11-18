#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$AC" "$AC.bak_phase1_1_1_$TS"
echo "✅ بک‌آپ: $AC.bak_phase1_1_1_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
AC = "/data/data/com.termux/files/home/groupbot/modules/access.py"

with open(AC, "r", encoding="utf-8") as f:
    content = f.read()

# ═══════════════════════════════════════════════════
# FIX ۱: acc_dp_ → بعد از toggle، منو رو edit کن
# ═══════════════════════════════════════════════════
old_dp = '''    toggle_deputy_perm(chat_id, key)
    try:
        await query.message.delete()
    except Exception:
        pass
    return'''

new_dp = '''    toggle_deputy_perm(chat_id, key)
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
        print("[ACCESS DP EDIT ERR] " + str(e))
    return'''

if old_dp in content:
    content = content.replace(old_dp, new_dp, 1)
    print("✅ acc_dp_ fix شد")
else:
    print("⚠️ acc_dp_ pattern پیدا نشد")

# ═══════════════════════════════════════════════════
# FIX ۲ و ۳: acc_vp_ و acc_ap_ (هر دو یه شکل)
# ═══════════════════════════════════════════════════
old_vp_ap = '''    toggle_user_perm(chat_id, target_id, key)
    try:
        await query.message.delete()
    except Exception:
        pass
    return'''

new_vp_ap = '''    toggle_user_perm(chat_id, target_id, key)
    # ★ منو رو آپدیت کن
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

count = content.count(old_vp_ap)
if count >= 1:
    content = content.replace(old_vp_ap, new_vp_ap)
    print(f"✅ acc_vp_/acc_ap_ fix شد ({count} بار)")
else:
    print("⚠️ acc_vp_/acc_ap_ pattern پیدا نشد")

# ═══════════════════════════════════════════════════
# FIX ۳: acc_back → حذف نکن (چون قراره بعداً «تایید و بستن» باشه)
# ولی فعلاً بذار بمونه
# ═══════════════════════════════════════════════════

with open(AC, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$AC" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$AC.bak_phase1_1_1_$TS" "$AC"
    exit 1
fi
echo ""

echo "─── چک: delete() هنوز هست؟ ───"
if grep -n "query.message.delete()" "$AC"; then
    echo "⚠️ هنوز delete هست — ولی تعدادش کم‌تر شده"
else
    echo "✅ هیچ delete() نمونده (به جز acc_back)"
fi
echo ""

echo "─── تعداد edit_message_reply_markup ───"
grep -c "edit_message_reply_markup" "$AC"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ فاز ۱.۱.۱ انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
