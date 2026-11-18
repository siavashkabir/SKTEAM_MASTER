import os, shutil, py_compile, time, re

print("="*80)
print("🔧 انتقال تنظیمات AI به زیرمنو")
print("="*80)

ts = time.strftime("%H%M%S")
bak = f'modules/owner_set_group.py.bak_aimenu_{ts}'
shutil.copy('modules/owner_set_group.py', bak)
print(f"✅ بکاپ: {bak}")

with open('modules/owner_set_group.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# ==== 1. پیدا کردن و حذف دکمه‌های AI ====
print("\n=== 1. حذف ۵ دکمه AI از منوی اصلی ===")

# الگوهایی که باید حذف بشن
ai_patterns = [
    'owner_set_ai_on:',
    'owner_set_ai_p:',
    'owner_set_ai_t:',
    'owner_set_ai_a:',
    'owner_set_ai_del:',
]

# پیدا کردن ایندکس دکمه‌ها
to_remove = []
insert_point = None
for i, line in enumerate(lines):
    for pat in ai_patterns:
        if pat in line and 'InlineKeyboardButton' in line:
            to_remove.append(i)
            if insert_point is None:
                insert_point = i
            print(f"🗑 حذف خط {i+1}: {pat}")
            break

if not to_remove:
    print("❌ هیچ دکمه AI پیدا نشد!")
    exit(1)

# ==== 2. اضافه کردن دکمه جدید در محل اولین دکمه AI ====
print("\n=== 2. اضافه کردن دکمه «پاسخگویی هوش مصنوعی» ===")

# indent از اولین دکمه حذفی
indent = ' ' * (len(lines[to_remove[0]]) - len(lines[to_remove[0]].lstrip()))

new_btn = f'{indent}[InlineKeyboardButton("🗣️ پاسخگویی هوش مصنوعی", callback_data=f"ai_menu:{{uid}}:{{chat_id}}")],\n'

# جایگزینی اولین دکمه با دکمه جدید، حذف بقیه
lines[to_remove[0]] = new_btn
for i in sorted(to_remove[1:], reverse=True):
    del lines[i]

print(f"✅ دکمه «پاسخگویی هوش مصنوعی» اضافه شد.")

# ==== 3. ایجاد تابع _build_ai_menu ====
print("\n=== 3. ساخت تابع _build_ai_menu ===")

# پیدا کردن تابع _build_menu
menu_start = None
for i, line in enumerate(lines):
    if line.startswith('def _build_menu('):
        menu_start = i
        break

if menu_start is None:
    print("❌ _build_menu پیدا نشد!")
    exit(1)

# این تابع رو باید قبل از _build_menu اضافه کنیم
ai_menu_func = '''def _build_ai_menu(uid, chat_id):
    """زیرمنوی تنظیمات هوش مصنوعی"""
    cd = get_chat_cooldown(chat_id)
    ai_on = get_ai_setting(chat_id, "ai_enabled", "0") == "1"
    ai_p = get_ai_setting(chat_id, "ai_personality", "persian")
    ai_t = get_ai_setting(chat_id, "ai_trigger", "mention")
    ai_a = get_ai_setting(chat_id, "ai_adult", "0") == "1"

    ai_on_lbl = "✅ فعال" if ai_on else "❌ غیرفعال"
    p_labels = {"persian": "😐 نرمال", "formal": "🎩 رسمی", "funny": "😂 شوخ", "cool": "😎 خونسرد", "rude": "😈 خبیث"}
    t_labels = {"mention": "📢 فقط منشن", "30percent": "30% پیام‌ها", "50percent": "50% پیام‌ها", "always": "همه پیام‌ها"}

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🤖 پاسخ هوشمند: {ai_on_lbl}", callback_data=f"owner_set_ai_on:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"😈 شخصیت: {p_labels.get(ai_p, '😐')}", callback_data=f"owner_set_ai_p:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"🗣️ فرکانس: {t_labels.get(ai_t, 'متوسط')}", callback_data=f"owner_set_ai_t:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"🔞 حالت بزرگسال: {'✅' if ai_a else '❌'}", callback_data=f"owner_set_ai_a:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"💬 حذف جواب AI: {fmt_sec(get_ai_setting(chat_id, 'ai_delete_seconds', get_ai_setting(0, 'sys_ai_delete_seconds', '0')))}", callback_data=f"owner_set_ai_del:{uid}:{chat_id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data=f"ai_back:{uid}:{chat_id}")],
    ])


'''

lines.insert(menu_start, ai_menu_func)
print("✅ تابع _build_ai_menu اضافه شد.")

# ==== 4. اصلاح هندلرهای owner_set_ai_* (برگشت به ai_menu) ====
print("\n=== 4. اصلاح هندلرها (برگشت به زیرمنو) ===")

# پیدا کردن هندلرهای ai و تغییر _build_menu به _build_ai_menu
count = 0
for i, line in enumerate(lines):
    if 'action == "owner_set_ai_' in line:
        for j in range(i, min(i + 15, len(lines))):
            if '_build_menu(uid, chat_id)' in lines[j] and 'ai_menu' not in lines[j]:
                lines[j] = lines[j].replace('_build_menu(uid, chat_id)', '_build_ai_menu(uid, chat_id)')
                count += 1

print(f"✅ {count} هندلر AI اصلاح شدند (برگشت به ai_menu).")

# ==== 5. اضافه کردن هندلرهای ai_menu و ai_back ====
print("\n=== 5. اضافه کردن هندلرهای زیرمنو ===")

# پیدا کردن هندلر timer_menu برای درج قبلش
anchor_idx = None
for i, line in enumerate(lines):
    if 'if action == "timer_menu"' in line:
        anchor_idx = i
        break

if anchor_idx is None:
    print("❌ anchor timer_menu پیدا نشد!")
    exit(1)

indent_h = ' ' * (len(lines[anchor_idx]) - len(lines[anchor_idx].lstrip()))
hib = ' ' * (len(lines[anchor_idx]) - len(lines[anchor_idx].lstrip()) + 4)

new_handlers = (
    f'{indent_h}if action == "ai_menu":\n'
    f'{hib}try:\n'
    f'{hib}    await _safe_edit(query, "🗣️ پاسخگویی هوش مصنوعی\\n\\nتنظیمات پاسخ‌دهی خودکار:", reply_markup=_build_ai_menu(uid, chat_id))\n'
    f'{hib}except Exception as e:\n'
    f'{hib}    print("[AI MENU ERR] " + str(e))\n'
    f'{hib}return\n'
    f'\n'
    f'{indent_h}if action == "ai_back":\n'
    f'{hib}try:\n'
    f'{hib}    await _safe_edit(query, "⚙️ تنظیمات این گروه", reply_markup=_build_menu(uid, chat_id))\n'
    f'{hib}except Exception as e:\n'
    f'{hib}    print("[AI BACK ERR] " + str(e))\n'
    f'{hib}return\n'
    f'\n'
)

lines.insert(anchor_idx, new_handlers)
print(f"✅ ۲ هندلر جدید اضافه شد.")

# ==== 6. اضافه کردن actionها به pattern هندلر در start.py ====
print("\n=== 6. اضافه کردن actionها به pattern ===")

with open('modules/start.py', 'r', encoding='utf-8') as f:
    start_content = f.read()

# پیدا کردن pattern که owner_set_ai_on را دارد
pattern_match = re.search(r'pattern="([^"]*owner_set_ai_on[^"]*)"', start_content)
if pattern_match:
    old_pat = pattern_match.group(1)
    if 'ai_menu' not in old_pat:
        new_pat = old_pat + '|ai_menu|ai_back'
        start_content = start_content.replace(f'pattern="{old_pat}"', f'pattern="{new_pat}"', 1)
        with open('modules/start.py', 'w', encoding='utf-8') as f:
            f.write(start_content)
        print("✅ actionها به pattern اضافه شدند.")
    else:
        print("⚠️ از قبل اضافه شده.")
else:
    print("⚠️ pattern پیدا نشد (ممکنه owner_set_ai_on در pattern نباشه).")
    # تلاش برای pattern دیگری
    pattern_match2 = re.search(r'pattern="([^"]*owner_set_[^"]*)"', start_content)
    if pattern_match2:
        old_pat = pattern_match2.group(1)
        if 'ai_menu' not in old_pat:
            new_pat = old_pat + '|ai_menu|ai_back'
            start_content = start_content.replace(f'pattern="{old_pat}"', f'pattern="{new_pat}"', 1)
            with open('modules/start.py', 'w', encoding='utf-8') as f:
                f.write(start_content)
            print("✅ (روش ۲) actionها اضافه شدند.")

# ==== 7. نوشتن ====
with open('modules/owner_set_group.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# ==== 8. کامپایل ====
print("\n=== 7. کامپایل ===")
try:
    py_compile.compile('modules/owner_set_group.py', doraise=True)
    py_compile.compile('modules/start.py', doraise=True)
    print("✅ کامپایل موفق.")
except Exception as e:
    print(f"❌ خطای کامپایل: {e}")
    shutil.copy(bak, 'modules/owner_set_group.py')
    print("⚠️ Auto-Rollback انجام شد.")
    exit(1)

# ==== 9. ری‌استارت ====
print("\n=== 8. ری‌استارت ربات ===")
os.system('pkill -9 -f "main.py"')
time.sleep(3)
os.system('cd ~/groupbot && bash -c "source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &"')
time.sleep(8)
os.system('tail -n 8 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ تمام شد!")
print("="*80)
print("""
📌 منوی اصلی تنظیمات این گروه:
   • ⏱ تنظیمات تایمر
   • 🗣️ پاسخگویی هوش مصنوعی  ← جدید
   • Anti-Raid
   • Anti-Bot
   • 📊 تنظیمات گزارش
   • 🔙 بازگشت

📌 روی «🗣️ پاسخگویی هوش مصنوعی» بزن:
   • 🤖 پاسخ هوشمند: ✅/❌
   • 😈 شخصیت
   • 🗣️ فرکانس
   • 🔞 حالت بزرگسال
   • 💬 حذف جواب AI
   • 🔙 بازگشت
""")
