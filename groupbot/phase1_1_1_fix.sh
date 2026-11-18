#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$AC" "$AC.bak_phase1_1_1_fix_$TS"
echo "✅ بک‌آپ: $AC.bak_phase1_1_1_fix_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
AC = "/data/data/com.termux/files/home/groupbot/modules/access.py"

with open(AC, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
i = 0
fix_count = 0

while i < len(lines):
    line = lines[i]
    
    # پیدا کردن "try:" که بعدش "await query.message.delete()" هست
    if line.strip() == "try:" and i + 1 < len(lines) and "query.message.delete()" in lines[i+1]:
        # چک کن خطوط بعدی "except Exception:" و "pass" هست
        if (i + 2 < len(lines) and "except Exception" in lines[i+2] and
            i + 3 < len(lines) and lines[i+3].strip() == "pass"):
            
            # indent رو از خط try بگیر
            indent = line[:len(line) - len(line.lstrip())]
            
            # ★ جایگزین کن با edit
            new_lines.append(indent + "# ★ منو رو آپدیت کن (نه delete)\n")
            new_lines.append(indent + "try:\n")
            new_lines.append(indent + '    member = await chat.get_member(target_id)\n')
            new_lines.append(indent + '    target_name = member.user.first_name or "کاربر"\n')
            new_lines.append(indent + "except Exception:\n")
            new_lines.append(indent + '    target_name = "کاربر"\n')
            new_lines.append(indent + "t_role = get_target_role(chat_id, target_id)\n")
            new_lines.append(indent + "v_owner = await is_bot_owner_or_admin(clicker)\n")
            new_lines.append(indent + "new_menu = build_access_menu(clicker, chat_id, target_id, target_name, t_role, v_owner)\n")
            new_lines.append(indent + "try:\n")
            new_lines.append(indent + "    await query.edit_message_reply_markup(reply_markup=new_menu)\n")
            new_lines.append(indent + "except Exception as e:\n")
            new_lines.append(indent + '    print("[ACCESS EDIT ERR] " + str(e))\n')
            
            fix_count += 1
            print(f"✅ fix {fix_count} در خط {i+1}")
            
            # 4 خط skip: try, delete, except, pass
            i += 4
            continue
    
    new_lines.append(line)
    i += 1

with open(AC, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print(f"\n✅ کل {fix_count} تا fix انجام شد")
PYEOF

echo ""

if python3 -m py_compile "$AC" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$AC.bak_phase1_1_1_fix_$TS" "$AC"
    exit 1
fi
echo ""

echo "─── چک: delete() هنوز هست؟ ───"
grep -n "query.message.delete()" "$AC" || echo "✅ هیچ delete() نمونده"
echo ""

echo "─── تعداد edit_message_reply_markup ───"
grep -c "edit_message_reply_markup" "$AC"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ فاز ۱.۱.۱ کامل شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
