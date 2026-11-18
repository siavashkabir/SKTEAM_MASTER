#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""جایگزینی کامل بلاک fj_set با نسخه ساده + افزودن /setfj"""
import os, shutil, py_compile, time, re

TARGET = "modules/start.py"
ts = time.strftime("%H%M%S")
bak = f"{TARGET}.bak_replacefj_{ts}"

print("="*70)
print("🔧 جایگزینی fj_set + افزودن /setfj")
print("="*70)
shutil.copy(TARGET, bak)
print(f"✅ بکاپ: {bak}")

with open(TARGET, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# ── ۱. پیدا کردن بلاک fj_set اول (خط 3983)
start = None
for i, l in enumerate(lines):
    if l.strip() == 'if action == "fj_set":':
        start = i
        break

if start is None:
    print("❌ fj_set پیدا نشد")
    exit(1)

print(f"🎯 fj_set در خط {start+1}")

# ── ۲. پیدا کردن انتهای بلاک (اولین `    if action ==` بعدی)
end = None
for k in range(start+1, min(start+60, len(lines))):
    if lines[k].startswith('    if action ==') or lines[k].startswith('    if action=='):
        end = k
        break
if end is None:
    end = start + 30

print(f"🎯 انتهای بلاک: خط {end} ({end-start} خط حذف می‌شه)")

# ── ۳. نمایش بلاک قدیمی (۳ خط اول و آخر)
print("\n📋 بلاک قدیمی:")
print(f"   شروع: {lines[start].rstrip()}")
print(f"   آخر:  {lines[end-1].rstrip()}")

# ── ۴. بلاک جدید (ساده)
new_block = '''    if action == "fj_set":
        # [REPLACED] دستور /setfj جایگزین شده
        try:
            _txt = ("🔒 تنظیم جوین اجباری" + NL +
                    "━━━━━━━━━━━━━━━━━━" + NL + NL +
                    "برای تنظیم لینک، این دستور رو توی PV ربات بفرست:" + NL + NL +
                    "/setfj https://t.me/yourlink" + NL + NL +
                    "برای حذف:" + NL +
                    "/setfj")
            await query.edit_message_text(
                _txt,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="s_fj_menu:" + str(uid) + ":" + str(chat_id))]
                ])
            )
            reset_timer(context, chat_id, msg_id)
        except Exception as e:
            print("[FJ SET REPLACED ERR] " + str(e))
        return

'''

new_lines = lines[:start] + [new_block] + lines[end:]
with open(TARGET, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print(f"✅ بلاک fj_set جایگزین شد")

# ── ۵. افزودن /setfj (اگه نبود)
with open(TARGET, 'r', encoding='utf-8') as f:
    content = f.read()

if "async def setfj_cmd" not in content:
    func = '''async def setfj_cmd(update, context):
    """دستور مستقیم تنظیم لینک FJ — فقط سازنده/سودو"""
    msg = update.effective_message
    user = update.effective_user
    args = context.args or []
    if not user or not msg:
        return
    try:
        from config import OWNER_ID
        from database import is_bot_admin
        is_owner = (user.id == OWNER_ID)
        is_sudo = is_bot_admin(user.id) if not is_owner else True
        if not (is_owner or is_sudo):
            await msg.reply_text("⛔ فقط سازنده/سودو")
            return
    except Exception as e:
        print("[SETFJ AUTH ERR] " + str(e))
        return
    if not args:
        try:
            from database import remove_global_force_join
            remove_global_force_join()
            await msg.reply_text("🗑 لینک FJ حذف شد")
        except Exception as e:
            await msg.reply_text("❌ " + str(e))
        return
    link = args[0].strip()
    try:
        from database import set_global_force_join, set_setting
        try:
            set_global_force_join(-1, link, "fj_group")
        except Exception:
            set_setting(0, "fj_link", link)
            set_setting(0, "fj_enabled", "1")
        await msg.reply_text("✅ لینک FJ ذخیره شد!" + chr(10) + chr(10) + "🔗 " + link)
        print("[SETFJ] Saved: " + link)
    except Exception as e:
        print("[SETFJ SAVE ERR] " + str(e))
        await msg.reply_text("❌ خطا: " + str(e))


'''
    content = content.replace("def register(app):", func + "def register(app):", 1)
    print("✅ تابع setfj_cmd اضافه شد")

if 'CommandHandler("setfj"' not in content:
    m = re.search(r'(def register\(app\):\s*\n)', content)
    if m:
        reg = '''    try:
        app.add_handler(CommandHandler("setfj", setfj_cmd))
        print("OK /setfj registered")
    except Exception as _e:
        print("[SETFJ REG ERR] " + str(_e))
'''
        content = content[:m.end()] + reg + content[m.end():]
        print("✅ /setfj ثبت شد")

with open(TARGET, 'w', encoding='utf-8') as f:
    f.write(content)

# ── ۶. py_compile
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
print("✅ آماده")
print("="*70)
print(f"""
📌 تست:
   ۱. توی PV ربات: /setfj https://t.me/test
      🟢 باید ببینی: «✅ لینک FJ ذخیره شد!»
   ۲. توی PV ربات: /setfj
      🟢 باید ببینی: «🗑 لینک FJ حذف شد»
   ۳. توی پنل → جوین اجباری → ➕ تنظیم جوین اجباری
      🟢 باید پیام راهنما با /setfj نشون داده بشه (پنل بسته نمی‌شه)

🔙 rollback:
   cp {bak} {TARGET} && pkill -9 -f main.py && sleep 3 && nohup bash bot_watchdog.sh > ~/groupbot_watchdog.log 2>&1 &
""")
os.system('tail -F ~/groupbot_bot.log')
