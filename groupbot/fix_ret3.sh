#!/data/data/com.termux/files/usr/bin/bash

NSFW=modules/nsfw.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$NSFW" "$NSFW.bak_ret3_$TS"
echo "✅ بک‌آپ: $NSFW.bak_ret3_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
NSFW = "/data/data/com.termux/files/home/groupbot/modules/nsfw.py"

with open(NSFW, "r", encoding="utf-8") as f:
    lines = f.readlines()

# پیدا کردن خط RET-3 و خط قبلی
found = False
for i, line in enumerate(lines):
    if '[NSFW-DBG-RET-3]' in line:
        # خطوط i-1 = شرط is_enabled, i = print, i+1 = return
        # خطوط قبل رو بازنویسی کن
        print(f"خط {i+1}: {line.strip()}")
        print(f"خط {i}: {lines[i-1].strip() if i > 0 else '?'}")
        
        # پیدا کردن خط is_enabled
        for j in range(i-1, max(0, i-5), -1):
            if 'is_enabled' in lines[j]:
                indent = lines[j][:len(lines[j]) - len(lines[j].lstrip())]
                
                # جایگزینی خطوط
                lines[j] = indent + 'from modules.nsfw import is_group_toggle_on, is_nsfw_sub_activated, is_enabled as _ie\n'
                lines.insert(j+1, indent + f'_dbg_chat_id = chat.id\n')
                lines.insert(j+2, indent + f'print(f"[NSFW-DBG] chat.id={{_dbg_chat_id}}, chat.type={{chat.type}}")\n')
                lines.insert(j+3, indent + f'print(f"[NSFW-DBG] is_group_toggle_on({{_dbg_chat_id}})={{is_group_toggle_on(_dbg_chat_id)}}")\n')
                lines.insert(j+4, indent + f'print(f"[NSFW-DBG] is_nsfw_sub_activated({{_dbg_chat_id}})={{is_nsfw_sub_activated(_dbg_chat_id)}}")\n')
                lines.insert(j+5, indent + f'_ie_result = _ie(_dbg_chat_id)\n')
                lines.insert(j+6, indent + f'print(f"[NSFW-DBG] is_enabled={{_ie_result}}")\n')
                lines[j+7] = indent + 'if not _ie_result:\n'
                found = True
                print(f"✅ خطوط {j+1} به بعد جایگزین شد")
                break
        break

if not found:
    print("❌ پیدا نشد")
    exit(1)

with open(NSFW, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$NSFW" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$NSFW.bak_ret3_$TS" "$NSFW"
    exit 1
fi
echo ""

echo "═══════════════════════════════════════════════════"
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo ""
echo "بعد یه استیکر بفرست و این رو بزن:"
echo "tail -n 30 ~/groupbot_bot.log | grep NSFW"
echo "═══════════════════════════════════════════════════"
