#!/data/data/com.termux/files/usr/bin/bash

NSFW=modules/nsfw.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$NSFW" "$NSFW.bak_dbg2_$TS"
echo "✅ بک‌آپ: $NSFW.bak_dbg2_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
NSFW = "/data/data/com.termux/files/home/groupbot/modules/nsfw.py"

with open(NSFW, "r", encoding="utf-8") as f:
    content = f.read()

# جایگزینی debug خط RET-3 با نسخه‌ی جزئی‌تر
old = '''    if not is_enabled(chat.id):
        print("[NSFW-DBG-RET-3] at line ~10")
        return'''

new = '''    print(f"[NSFW-DBG] chat.id={chat.id}, chat.type={chat.type}")
    try:
        from modules.nsfw import is_group_toggle_on, is_nsfw_sub_activated
        print(f"[NSFW-DBG] is_group_toggle_on({chat.id})={is_group_toggle_on(chat.id)}")
        print(f"[NSFW-DBG] is_nsfw_sub_activated({chat.id})={is_nsfw_sub_activated(chat.id)}")
    except Exception as e:
        print(f"[NSFW-DBG] err checking: {e}")
    en = is_enabled(chat.id)
    print(f"[NSFW-DBG] is_enabled({chat.id})={en}")
    if not en:
        print("[NSFW-DBG-RET-3] at line ~10 - is_enabled False")
        return'''

if old in content:
    content = content.replace(old, new, 1)
    print("✅ debug RET-3 جزئی‌تر شد")
else:
    print("❌ RET-3 پیدا نشد")
    exit(1)

with open(NSFW, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$NSFW" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$NSFW.bak_dbg2_$TS" "$NSFW"
    exit 1
fi
echo ""

echo "═══════════════════════════════════════════════════"
echo "🎯 ری‌استارت کن:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo ""
echo "بعد یه استیکر بفرست و این رو بزن:"
echo "tail -n 30 ~/groupbot_bot.log | grep NSFW"
echo "═══════════════════════════════════════════════════"
