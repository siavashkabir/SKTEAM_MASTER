#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$AC" "$AC.bak_flag_$TS"
echo "✅ بک‌آپ: $AC.bak_flag_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
AC = "/data/data/com.termux/files/home/groupbot/modules/access.py"

with open(AC, "r", encoding="utf-8") as f:
    content = f.read()

# ═══ ۱. acc_dp_ — flag رو با bot_data ═══
old = '''        toggle_deputy_perm(chat_id, key)
        ACCESS_CHANGED[(chat_id, target_id)] = True'''
new = '''        toggle_deputy_perm(chat_id, key)
        context.bot_data.setdefault("access_changed", {})
        context.bot_data["access_changed"][(chat_id, target_id)] = True
        print(f"[ACCESS DBG SET] key=({chat_id}, {target_id})")'''

if old in content:
    content = content.replace(old, new, 1)
    print("✅ acc_dp_ flag fix شد")
else:
    print("⚠️ acc_dp_ flag پیدا نشد")

# ═══ ۲. acc_vp_ و acc_ap_ — flag ═══
old2 = '''        toggle_user_perm(chat_id, target_id, key)
        ACCESS_CHANGED[(chat_id, target_id)] = True'''
new2 = '''        toggle_user_perm(chat_id, target_id, key)
        context.bot_data.setdefault("access_changed", {})
        context.bot_data["access_changed"][(chat_id, target_id)] = True
        print(f"[ACCESS DBG SET] key=({chat_id}, {target_id})")'''

count = content.count(old2)
if count > 0:
    content = content.replace(old2, new2)
    print(f"✅ acc_vp_/acc_ap_ flag fix شد ({count} بار)")
else:
    print("⚠️ acc_vp_ flag پیدا نشد")

# ═══ ۳. acc_confirm — خواندن flag با debug ═══
old3 = '''        was_changed = ACCESS_CHANGED.pop((chat_id, target_id), False)'''
new3 = '''        d = context.bot_data.get("access_changed", {})
        print(f"[ACCESS DBG READ] looking for key=({chat_id}, {target_id}), all keys={list(d.keys())}")
        was_changed = d.pop((chat_id, target_id), False)
        print(f"[ACCESS DBG READ] was_changed={was_changed}")'''

if old3 in content:
    content = content.replace(old3, new3, 1)
    print("✅ acc_confirm read flag fix شد")
else:
    print("⚠️ acc_confirm read flag پیدا نشد")

with open(AC, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$AC" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$AC.bak_flag_$TS" "$AC"
    exit 1
fi
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo ""
echo "بعد توی تلگرام:"
echo "1. «دسترسی» رو بزن"
echo "2. یه دکمه toggle بزن"
echo "3. «✅ تایید و بستن» رو بزن"
echo ""
echo "بعد این رو بزن و نتیجه رو بفرست:"
echo "tail -n 30 ~/groupbot_bot.log | grep 'ACCESS DBG'"
echo "═══════════════════════════════════════════════════"
