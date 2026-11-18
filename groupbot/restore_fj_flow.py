#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""بازگشت جریان FJ + اشتراک FJ_WAIT بین start و force_join"""
import os, shutil, py_compile, time, re

TARGET = "modules/start.py"
ts = time.strftime("%H%M%S")
bak = f"{TARGET}.bak_restorefj_{ts}"

print("="*70)
print("🔧 بازگشت جریان FJ + اشتراک FJ_WAIT")
print("="*70)
shutil.copy(TARGET, bak)
print(f"✅ بکاپ: {bak}")

with open(TARGET, 'r', encoding='utf-8') as f:
    content = f.read()

# ── ۱. اشتراک FJ_WAIT (start.py خط 43)
old_share = "FJ_WAIT = {}"
new_share = """try:
    from modules.force_join import FJ_WAIT as _FJ_SHARED
    FJ_WAIT = _FJ_SHARED
    print("OK FJ_WAIT shared with force_join")
except Exception as _fj_share_err:
    FJ_WAIT = {}
    print("[FJ WAIT SHARE ERR] " + str(_fj_share_err))"""

if "from modules.force_join import FJ_WAIT" in content:
    print("ℹ️ FJ_WAIT قبلاً مشترک شده")
elif old_share in content:
    content = content.replace(old_share, new_share, 1)
    print("✅ FJ_WAIT مشترک شد")
else:
    print("⚠️ FJ_WAIT = {} پیدا نشد")

# ── ۲. پیدا کردن بلاک فعلی fj_set (که با [REPLACED] علامت خورده)
lines = content.split('\n')
start_idx = None
for i, line in enumerate(lines):
    if line.strip() == 'if action == "fj_set":':
        # چک کن خط بعدش [REPLACED] داره
        if i + 1 < len(lines) and '[REPLACED]' in lines[i+1]:
            start_idx = i
            break

if start_idx is None:
    # شاید فقط یه fj_set داره (بدون REPLACED)
    for i, line in enumerate(lines):
        if line.strip() == 'if action == "fj_set":':
            start_idx = i
            break

if start_idx is None:
    print("❌ fj_set پیدا نشد")
    exit(1)

print(f"🎯 fj_set در خط {start_idx+1}")

# انتهای بلاک
end_idx = start_idx + 1
for i in range(start_idx + 1, min(start_idx + 50, len(lines))):
    if lines[i].strip() == 'return' and i > start_idx + 2:
        end_idx = i + 1
        break
print(f"🎯 انتهای بلاک: خط {end_idx}")

# ── ۳. بلاک جدید: جریان قدیمی که منتظر لینک می‌مونه
new_block = '''    if action == "fj_set":
        try:
            from config import OWNER_ID
            if clicker_id != OWNER_ID:
                await query.answer("\u274c \u0641\u0642\u0637 \u0633\u0627\u0632\u0646\u062f\u0647!", show_alert=True)
                return
        except Exception:
            pass
        try:
            FJ_WAIT[uid] = "target"
            print("[FJ-SET] uid=" + str(uid) + " added. Keys=" + str(list(FJ_WAIT.keys())))
            await query.edit_message_text(
                "\U0001f512 \u062a\u0646\u0638\u06cc\u0645 \u062c\u0648\u06cc\u0646 \u0627\u062c\u0628\u0627\u0631\u06cc" + NL +
                "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501" + NL + NL +
                "\U0001f4dd \u0644\u06cc\u0646\u06a9 \u06af\u0631\u0648\u0647 \u06cc\u0627 \u06a9\u0627\u0646\u0627\u0644 \u0631\u0648 \u0628\u0641\u0631\u0633\u062a:" + NL + NL +
                "\u26a0\ufe0f \u0628\u0639\u062f \u0627\u0632 \u0627\u0631\u0633\u0627\u0644\u060c \u062a\u0627\u06cc\u06cc\u062f\u06cc\u0647 \u062f\u0627\u062f\u0647 \u0645\u06cc\u0634\u0647." + NL +
                "\u274c \u0644\u063a\u0648: /start",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("\U0001f519 \u0628\u0627\u0632\u06af\u0634\u062a", callback_data="s_fj_menu:" + str(uid) + ":" + str(chat_id))]
                ])
            )
            reset_timer(context, chat_id, msg_id)
        except Exception as e:
            print("[FJ SET ERR] " + str(e))
            try:
                await query.answer("\u274c \u062e\u0637\u0627", show_alert=True)
            except Exception:
                pass
        return
'''

lines = lines[:start_idx] + new_block.split('\n') + lines[end_idx:]
content = '\n'.join(lines)
print("✅ بلاک fj_set با جریان قدیمی جایگزین شد")

with open(TARGET, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n🔍 py_compile...")
try:
    py_compile.compile(TARGET, doraise=True)
    print("✅ OK")
except Exception as e:
    print(f"❌ {e}")
    shutil.copy(bak, TARGET)
    print("🔄 rollback")
    exit(1)

for root, dirs, files in os.walk('.'):
    if 'venv' in root: continue
    if '__pycache__' in root:
        shutil.rmtree(root, ignore_errors=True)

print("\n🔄 ری‌استارت...")
os.system('pkill -9 -f "main.py"')
time.sleep(3)
os.system('cd ~/groupbot && nohup bash bot_watchdog.sh > ~/groupbot_watchdog.log 2>&1 &')
time.sleep(12)
os.system('tail -n 5 ~/groupbot_bot.log')

print("\n" + "="*70)
print("✅ جریان FJ بازگشت")
print("="*70)
print(f"""
📌 تست (اکانت مالک گروه توی Test robat):
   ۱. پنل → ⚙️ تنظیمات گروه
   ۲. 🔒 جوین اجباری
   ۳. ➕ تنظیم جوین اجباری
      🟢 باید پیام «لینک بفرست» بیاد
   ۴. یه لینک بفرست: https://t.me/test
      🟢 باید ببینی: «✅ لینک جوین اجباری ذخیره شد»

🔙 rollback:
   cp {bak} {TARGET} && pkill -9 -f main.py && sleep 3 && nohup bash bot_watchdog.sh > ~/groupbot_watchdog.log 2>&1 &
""")
os.system('tail -F ~/groupbot_bot.log')
