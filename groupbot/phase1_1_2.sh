#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$AC" "$AC.bak_confirm_$TS"
echo "✅ بک‌آپ: $AC.bak_confirm_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
AC = "/data/data/com.termux/files/home/groupbot/modules/access.py"

with open(AC, "r", encoding="utf-8") as f:
    content = f.read()

# ═══ ۱. import asyncio ═══
if "import asyncio" not in content:
    content = content.replace("import os\n", "import os\nimport asyncio\n", 1)
    print("✅ import asyncio اضافه شد")

# ═══ ۲. ACCESS_CHANGED dict ═══
if "ACCESS_CHANGED" not in content:
    if "HL = chr(10)" in content:
        content = content.replace(
            "HL = chr(10)",
            "HL = chr(10)\nACCESS_CHANGED = {}  # (chat_id, target_id) -> True",
            1
        )
        print("✅ ACCESS_CHANGED اضافه شد")

# ═══ ۳. تغییر دکمه acc_back → acc_confirm ═══
old_btn = 'keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="acc_back:" + str(uid) + ":" + str(chat_id))])'
new_btn = 'keyboard.append([InlineKeyboardButton("✅ تایید و بستن", callback_data="acc_confirm:" + str(uid) + ":" + str(chat_id) + ":" + str(target_id))])'

count_btn = content.count(old_btn)
if count_btn > 0:
    content = content.replace(old_btn, new_btn)
    print(f"✅ دکمه تایید در {count_btn} جا اضافه شد")
else:
    print("⚠️ دکمه acc_back پیدا نشد")

# ═══ ۴. بعد از toggle، flag رو True کن ═══
if "toggle_deputy_perm(chat_id, key)" in content and "ACCESS_CHANGED[(chat_id, target_id)] = True" not in content:
    content = content.replace(
        "    toggle_deputy_perm(chat_id, key)\n",
        "    toggle_deputy_perm(chat_id, key)\n    ACCESS_CHANGED[(chat_id, target_id)] = True\n",
        1
    )
    print("✅ flag بعد از toggle_deputy اضافه شد")

if "toggle_user_perm(chat_id, target_id, key)" in content:
    content = content.replace(
        "    toggle_user_perm(chat_id, target_id, key)\n",
        "    toggle_user_perm(chat_id, target_id, key)\n    ACCESS_CHANGED[(chat_id, target_id)] = True\n",
    )
    print("✅ flag بعد از toggle_user اضافه شد")

# ═══ ۵. تغییر handler ═══
old_handler = '''    if action == "acc_back":
        try:
            await query.message.delete()
        except Exception:
            pass
        return'''

new_handler = '''    if action == "acc_confirm":
        chat_id = int(parts[2]) if len(parts) > 2 else query.message.chat_id
        target_id = int(parts[3]) if len(parts) > 3 else None
        was_changed = ACCESS_CHANGED.pop((chat_id, target_id), False)
        
        try:
            await query.message.delete()
        except Exception:
            pass
        
        try:
            if was_changed:
                msg = await context.bot.send_message(
                    chat_id=chat_id,
                    text="✅ تغییرات با موفقیت اعمال شد."
                )
            else:
                msg = await context.bot.send_message(
                    chat_id=chat_id,
                    text="ℹ️ تغییری اعمال نشد."
                )
            async def _auto_del(m):
                await asyncio.sleep(5)
                try:
                    await m.delete()
                except Exception:
                    pass
            asyncio.create_task(_auto_del(msg))
        except Exception as e:
            print("[ACCESS CONFIRM MSG ERR] " + str(e))
        return'''

if old_handler in content:
    content = content.replace(old_handler, new_handler, 1)
    print("✅ handler acc_confirm اضافه شد")
else:
    print("⚠️ handler acc_back پیدا نشد")

with open(AC, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$AC" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$AC.bak_confirm_$TS" "$AC"
    exit 1
fi
echo ""

echo "─── چک نهایی ───"
echo "دکمه تایید:"
grep -c "acc_confirm" "$AC"
echo "ACCESS_CHANGED:"
grep -c "ACCESS_CHANGED" "$AC"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ فاز ۱.۱.۲ انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
