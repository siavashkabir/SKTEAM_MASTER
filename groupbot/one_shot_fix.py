#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, shutil, py_compile, time, re, subprocess

TARGET = "modules/start.py"
ts = time.strftime("%H%M%S")
bak = f"{TARGET}.bak_oneshot_{ts}"

print("="*70)
print("🚀 یک‌شات: fix خط 465 + debug handler + restart + live log")
print("="*70)

# ── ۱. بکاپ
shutil.copy(TARGET, bak)
print(f"✅ بکاپ: {bak}")

with open(TARGET, 'r', encoding='utf-8') as f:
    content = f.read()

# ── ۲. fix خط 465 (chat_id تکراری)
old_line = '''[InlineKeyboardButton("بازگشت", callback_data="owner_section_back:" + str(uid) + ":" + str(chat_id) + ":" + str(chat_id))]'''
new_line = '''[InlineKeyboardButton("بازگشت", callback_data="owner_section_back:" + str(uid) + ":" + str(chat_id))]'''

count_465 = content.count(old_line)
if count_465 > 0:
    content = content.replace(old_line, new_line)
    print(f"✅ خط 465 اصلاح شد ({count_465} مورد)")
else:
    print("ℹ️ خط 465 با این الگو پیدا نشد (شاید قبلاً fix شده)")

# ── ۳. debug روی owner_section_back (بدون تغییر ساختار)
# پیدا کردن بلاک try بعد از "if action == \"owner_section_back\":"
pattern = re.compile(
    r'(if action == "owner_section_back":\s*\n)(.*?)(    try:\s*\n        await query\.edit_message_text\()',
    re.DOTALL
)

m = pattern.search(content)
if m:
    # فقط اگه debug قبلاً نیست
    if '[DBG-BACK] BEFORE' not in content:
        # درج ۲ print قبل از try
        insert_text = '''    print("[DBG-BACK] ENTER2 | user=" + str(query.from_user.id))
    print("[DBG-BACK] BEFORE edit | msg=" + str(query.message.message_id) + " | chat=" + str(query.message.chat.id))
'''
        # جایگزینی: بین if و try، print رو اضافه کن
        content = pattern.sub(
            lambda mm: mm.group(1) + mm.group(2) + insert_text + mm.group(3),
            content,
            count=1
        )
        # اضافه کردن print بعد از edit (بعد از خط ")" که try رو می‌بنده)
        pattern2 = re.compile(
            r'(if action == "owner_section_back":.*?await query\.edit_message_text\(.*?\n        \)\n)(\s*except Exception as e:\s*\n\s*print\("\[SECTION BACK ERR\] " \+ str\(e\)\))',
            re.DOTALL
        )
        def repl(m2):
            return m2.group(1) + '        print("[DBG-BACK] AFTER edit OK")\n' + m2.group(2)
        content = pattern2.sub(repl, content, count=1)
        print("✅ debug اضافه شد")
    else:
        print("ℹ️ debug قبلاً اضافه شده")
else:
    print("⚠️ بلاک owner_section_back پیدا نشد")

with open(TARGET, 'w', encoding='utf-8') as f:
    f.write(content)

# ── ۴. کامپایل
print("\n🔍 py_compile...")
try:
    py_compile.compile(TARGET, doraise=True)
    print("✅ کامپایل OK")
except Exception as e:
    print(f"❌ {e}")
    shutil.copy(bak, TARGET)
    print("🔄 rollback شد — اسکریپت متوقف")
    exit(1)

# ── ۵. پاک کش
for root, dirs, files in os.walk('.'):
    if 'venv' in root: continue
    if '__pycache__' in root:
        shutil.rmtree(root, ignore_errors=True)

# ── ۶. ری‌استارت
print("\n🔄 ری‌استارت ربات...")
os.system('pkill -9 -f "main.py"')
time.sleep(3)
os.system('cd ~/groupbot && nohup bash bot_watchdog.sh > ~/groupbot_watchdog.log 2>&1 &')
time.sleep(12)

# ── ۷. نمایش لاگ آماده
print("\n" + "="*70)
print("✅ آماده تست")
print("="*70)
print(f"""
📌 مسیر تست:
   PV → /start → 🔧 بخش سازنده → 👤 مدیریت ادمین‌های ربات → 🔙 بازگشت

📄 لاگ زنده (این دستور رو جدا بزن):
   tail -f ~/groupbot_bot.log

🔙 برگرداندن کد به حالت قبل:
   cp {bak} {TARGET}
   pkill -9 -f main.py
   sleep 3
   nohup bash bot_watchdog.sh > ~/groupbot_watchdog.log 2>&1 &
""")

# ── ۸. اگه ورودی «لایو» بود، خودکار tail کن
print("\n" + "="*70)
print("📄 لاگ زنده (برای خارج شدن Ctrl+C):")
print("="*70 + "\n")
os.system('tail -f ~/groupbot_bot.log')
