import os, shutil, py_compile, time, re

print("="*80)
print("🔧 ایجاد «بخش سازنده» + انتقال ۵ دکمه")
print("="*80)

# ==== 1. بکاپ ====
ts = time.strftime("%H%M%S")
bak = f'modules/start.py.bak_section_{ts}'
shutil.copy('modules/start.py', bak)
print(f"✅ بکاپ: {bak}")

# ==== 2. خواندن خطوط ====
with open('modules/start.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# ==== 3. پیدا کردن owner_manage_menu ====
func_start = None
for i, line in enumerate(lines):
    if line.startswith('def owner_manage_menu('):
        func_start = i
        break

if func_start is None:
    print("❌ owner_manage_menu پیدا نشد!")
    exit(1)
print(f"📍 owner_manage_menu در خط {func_start+1}")

# ==== 4. پیدا کردن انتهای تابع ====
func_end = len(lines)
for j in range(func_start + 1, len(lines)):
    if lines[j].startswith('def ') or lines[j].startswith('async def '):
        func_end = j
        break
print(f"📍 انتهای تابع در خط {func_end}")

# ==== 5. چک اینکه از قبل انجام نشده ====
already = any('owner_section_menu' in lines[k] for k in range(func_start, func_end))
if already:
    print("⚠️ از قبل «بخش سازنده» اضافه شده!")
    exit(0)

# ==== 6. پیدا کردن ۵ دکمه برای حذف ====
print("\n=== حذف ۵ دکمه از منوی اصلی ===")

buttons_to_move = [
    'menu_owners:',       # مدیریت ادمین‌های ربات
    'menu_admins:',       # مدیریت گروه‌ها
    'menu_vip:',          # جوین اجباری
    'menu_deputies:',     # آمار سودوها
    'menu_admin_perms:',  # آمار گروه‌ها
]

to_remove = []
for i in range(func_start, func_end):
    line = lines[i]
    if 'InlineKeyboardButton' not in line:
        continue
    for btn in buttons_to_move:
        if f'callback_data="{btn}' in line or f'callback_data=f"{btn}' in line:
            to_remove.append(i)
            print(f"🗑 خط {i+1}: {btn}")
            break

if len(to_remove) != 5:
    print(f"❌ فقط {len(to_remove)} دکمه از ۵ پیدا شد!")
    exit(1)

# ==== 7. پیدا کردن محل درج دکمه جدید (قبل از menu_close) ====
insert_at = None
for i in range(func_start, func_end):
    if 'menu_close:' in lines[i] and 'InlineKeyboardButton' in lines[i]:
        insert_at = i
        break

if insert_at is None:
    print("❌ menu_close پیدا نشد!")
    exit(1)
print(f"📍 محل درج دکمه جدید: خط {insert_at+1}")

# ==== 8. ساخت دکمه جدید ====
# indent از خط insert_at
indent = ' ' * (len(lines[insert_at]) - len(lines[insert_at].lstrip()))
new_button = f'{indent}[InlineKeyboardButton("🔧 بخش سازنده", callback_data="owner_section_menu:" + str(uid) + ":" + str(chat_id))],\n'

# ==== 9. حذف دکمه‌های قدیمی + درج دکمه جدید ====
# اول حذف (از آخر به اول)
new_lines = []
for i, line in enumerate(lines):
    if i in to_remove:
        continue
    if i == insert_at:
        new_lines.append(new_button)
    new_lines.append(line)

lines = new_lines
print(f"✅ دکمه‌های قدیمی حذف و دکمه جدید اضافه شد.")

# ==== 10. پیدا کردن محل درج تابع owner_section_menu (قبل از owner_manage_menu) ====
func_start2 = None
for i, line in enumerate(lines):
    if line.startswith('def owner_manage_menu('):
        func_start2 = i
        break

# ==== 11. ساخت تابع جدید ====
section_func = '''def owner_section_menu(uid, chat_id=0):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 مدیریت ادمین‌های ربات", callback_data="menu_owners:" + str(uid))],
        [InlineKeyboardButton("🌐 مدیریت گروه‌ها", callback_data="menu_admins:" + str(uid))],
        [InlineKeyboardButton("🔒 جوین اجباری", callback_data="menu_vip:" + str(uid))],
        [InlineKeyboardButton("📊 آمار سودوها", callback_data="menu_deputies:" + str(uid))],
        [InlineKeyboardButton("📈 آمار گروه‌ها", callback_data="menu_admin_perms:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="owner_section_back:" + str(uid))],
    ])


'''

lines.insert(func_start2, section_func)
print(f"✅ تابع owner_section_menu اضافه شد.")

# ==== 12. اضافه کردن هندلرها ====
# پیدا کردن owner_manage_menu برای anchor
anchor_idx = None
for i, line in enumerate(lines):
    if line.startswith('def owner_manage_menu('):
        anchor_idx = i
        break

# پیدا کردن هندلرهای داخل actionها - دنبال "if action == "menu_status":"
handler_anchor = None
for i, line in enumerate(lines):
    if 'if action == "menu_status"' in line:
        handler_anchor = i
        break

if handler_anchor is None:
    # دنبال هر action از owner_manage_menu
    for i, line in enumerate(lines):
        if 'if action == "menu_owners"' in line or 'if action == "menu_admins"' in line:
            handler_anchor = i
            break

if handler_anchor is None:
    print("❌ anchor هندلر پیدا نشد!")
    exit(1)

indent_h = ' ' * (len(lines[handler_anchor]) - len(lines[handler_anchor].lstrip()))
hib = ' ' * (len(lines[handler_anchor]) - len(lines[handler_anchor].lstrip()) + 4)

new_handlers = (
    f'{indent_h}if action == "owner_section_menu":\n'
    f'{hib}try:\n'
    f'{hib}    await query.edit_message_text("🔧 بخش سازنده\\n\\nگزینه مورد نظر را انتخاب کنید:", reply_markup=owner_section_menu(uid, chat_id))\n'
    f'{hib}except Exception as e:\n'
    f'{hib}    print("[SECTION MENU ERR] " + str(e))\n'
    f'{hib}return\n'
    f'\n'
    f'{indent_h}if action == "owner_section_back":\n'
    f'{hib}try:\n'
    f'{hib}    await query.edit_message_text("👑 منوی اصلی - بخش مورد نظر:", reply_markup=owner_manage_menu(uid, chat_id))\n'
    f'{hib}except Exception as e:\n'
    f'{hib}    print("[SECTION BACK ERR] " + str(e))\n'
    f'{hib}return\n'
    f'\n'
)

lines.insert(handler_anchor, new_handlers)
print(f"✅ ۲ هندلر جدید اضافه شد.")

# ==== 13. اضافه کردن actionها به pattern ====
with open('modules/start.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

content = ''.join(lines)
# پیدا کردن pattern شامل menu_owners
pattern_match = re.search(r'pattern="([^"]*menu_owners[^"]*)"', content)
if pattern_match and 'owner_section_menu' not in pattern_match.group(1):
    old_pat = pattern_match.group(1)
    new_pat = old_pat + '|owner_section_menu|owner_section_back'
    content = content.replace(f'pattern="{old_pat}"', f'pattern="{new_pat}"', 1)
    with open('modules/start.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ actionها به pattern اضافه شدند.")
else:
    print("⚠️ pattern پیدا نشد یا از قبل هست.")

# ==== 14. کامپایل ====
print("\n=== کامپایل ===")
try:
    py_compile.compile('modules/start.py', doraise=True)
    print("✅ کامپایل موفق.")
except Exception as e:
    print(f"❌ خطای کامپایل: {e}")
    shutil.copy(bak, 'modules/start.py')
    print("⚠️ Auto-Rollback انجام شد.")
    exit(1)

# ==== 15. نمایش ناحیه تغییر ====
print("\n=== تأیید نهایی ===")
with open('modules/start.py', 'r', encoding='utf-8') as f:
    nl = f.readlines()

print("\n[owner_manage_menu - دکمه جدید]:")
for i, line in enumerate(nl):
    if 'owner_section_menu:' in line and 'InlineKeyboardButton' in line:
        for j in range(max(0, i-3), min(len(nl), i+3)):
            print(f"   {j+1}: {nl[j].rstrip()}")
        break

print("\n[owner_section_menu - تابع]:")
for i, line in enumerate(nl):
    if line.startswith('def owner_section_menu('):
        for j in range(i, min(i+8, len(nl))):
            print(f"   {j+1}: {nl[j].rstrip()}")
        break

# ==== 16. ری‌استارت ====
print("\n=== ری‌استارت ربات ===")
os.system('pkill -9 -f "main.py"')
time.sleep(3)
os.system('cd ~/groupbot && bash -c "source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &"')
time.sleep(8)
os.system('tail -n 8 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ تمام شد!")
print("="*80)
print("""
📌 منوی اصلی سازنده حالا:
   • 💎 مدیریت اشتراک‌ها
   • 🔧 بخش سازنده  ← جدید (شامل ۵ دکمه)
   • 👥 ورود به پنل گروه
   • 📖 راهنمای کامل
   • ❌ بستن منو
""")
