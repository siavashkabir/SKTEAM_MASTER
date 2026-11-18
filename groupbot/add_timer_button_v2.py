import os, shutil, py_compile, time

print("="*80)
print("🔧 اضافه کردن دکمه «⏱ تنظیمات تایمر» (روش خط به خط)")
print("="*80)

# ===== 1. بکاپ =====
ts = time.strftime("%H%M%S")
bak = f'modules/start.py.bak_tbtn_{ts}'
shutil.copy('modules/start.py', bak)
print(f"✅ بکاپ: {bak}")

# ===== 2. خواندن خط به خط =====
try:
    with open('modules/start.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # پیدا کردن تابع owner_settings_menu
    func_start = None
    for i, line in enumerate(lines):
        if line.startswith('def owner_settings_menu('):
            func_start = i
            break
    
    if func_start is None:
        print("❌ تابع owner_settings_menu پیدا نشد!")
        shutil.copy(bak, 'modules/start.py')
        exit(1)
    
    print(f"📍 owner_settings_menu در خط {func_start+1}")
    
    # پیدا کردن انتهای تابع (اولین def یا async def در سطح صفر بعد از func_start)
    func_end = None
    for j in range(func_start + 1, len(lines)):
        stripped = lines[j].lstrip()
        if (stripped.startswith('def ') or stripped.startswith('async def ')) and not lines[j].startswith(' '):
            func_end = j
            break
        if j == len(lines) - 1:
            func_end = len(lines)
            break
    
    if func_end is None:
        func_end = len(lines)
    
    print(f"📍 تابع از خط {func_start+1} تا {func_end}")
    
    # پیدا کردن خط menu_close در این تابع
    menu_close_line = None
    for k in range(func_start, func_end):
        if 'menu_close' in lines[k] and 'InlineKeyboardButton' in lines[k]:
            menu_close_line = k
            break
    
    if menu_close_line is None:
        print("❌ خط menu_close پیدا نشد!")
        shutil.copy(bak, 'modules/start.py')
        exit(1)
    
    print(f"📍 خط menu_close در خط {menu_close_line+1}")
    print(f"   محتوا: {lines[menu_close_line].rstrip()[:100]}")
    
    # بررسی اینکه آیا دکمه تایمر از قبل وجود دارد
    for k in range(func_start, func_end):
        if 'owner_timer_panel' in lines[k]:
            print("⚠️ دکمه تایمر از قبل وجود دارد.")
            shutil.copy(bak, 'modules/start.py')
            exit(0)
    
    # ===== 3. اضافه کردن دکمه جدید قبل از خط menu_close =====
    # پیدا کردن indentation خط menu_close
    indent = len(lines[menu_close_line]) - len(lines[menu_close_line].lstrip())
    indent_str = ' ' * indent
    
    # ساخت دکمه جدید با استفاده از emoji مستقیم (نه escape)
    timer_button = f'{indent_str}[InlineKeyboardButton("\u23f1 \u062a\u0646\u0637\u06cc\u0645\u0627\u062a \u062a\u0627\u06cc\u0645\u0631", callback_data=f"owner_timer_panel:{{uid}}:{{chat_id}}")],\n'
    
    lines.insert(menu_close_line, timer_button)
    print(f"✅ دکمه «⏱ تنظیمات تایمر» به خط {menu_close_line+1} اضافه شد.")
    
except Exception as e:
    print(f"❌ خطا در مرحله 2: {e}")
    import traceback
    traceback.print_exc()
    shutil.copy(bak, 'modules/start.py')
    exit(1)

# ===== 4. اضافه کردن هندلر owner_timer_panel =====
try:
    # پیدا کردن نقطه‌ی اتصال (anchor)
    anchor_idx = None
    for i, line in enumerate(lines):
        if line.startswith('    if action == "aperm_user":') or line.startswith('    if action == "menu_settings":'):
            anchor_idx = i
            break
    
    if anchor_idx is None:
        print("⚠️ نقطه اتصال پیدا نشد. هندلر اضافه نشد.")
    else:
        # بررسی اینکه آیا هندلر از قبل وجود دارد
        has_handler = False
        for line in lines:
            if 'action == "owner_timer_panel"' in line:
                has_handler = True
                break
        
        if not has_handler:
            handler_lines = '''    if action == "owner_timer_panel":
        try:
            from config import OWNER_ID
            uid_check = query.from_user.id
            is_owner = (uid_check == OWNER_ID)
            is_sudo = False
            if not is_owner:
                try:
                    from database import is_sudo as db_is_sudo
                    is_sudo = db_is_sudo(uid_check)
                except Exception:
                    is_sudo = False
            if not is_owner and not is_sudo:
                await query.answer("\u26d4 \u0641\u0642\u0637 \u0633\u0627\u0632\u0646\u062f\u0647 \u0648 \u0633\u0648\u062f\u0648 \u062f\u0633\u062a\u0631\u0633\u06cc \u062f\u0627\u0631\u0646\u062f.", show_alert=True)
                return
            from modules.owner_set_group import build_menu
            await query.edit_message_text(
                "\u23f1 \u062a\u0646\u0637\u06cc\u0645\u0627\u062a \u062a\u0627\u06cc\u0645\u0631 \u067e\u0646\u0644",
                reply_markup=build_menu(uid_check, query.message.chat.id)
            )
        except Exception as e:
            print("[OWNER TIMER PANEL ERR] " + str(e))
        return

'''
            # درج قبل از anchor
            for hl in reversed(handler_lines.split('\n')):
                if hl or hl == '':
                    lines.insert(anchor_idx, hl + '\n')
            print(f"✅ هندلر owner_timer_panel به خط {anchor_idx+1} اضافه شد.")
        else:
            print("⚠️ هندلر از قبل وجود دارد.")
except Exception as e:
    print(f"❌ خطا در مرحله 4: {e}")
    shutil.copy(bak, 'modules/start.py')
    exit(1)

# ===== 5. اضافه کردن action به الگوی هندلر =====
try:
    # خواندن دوباره و بررسی
    content = ''.join(lines)
    if 'owner_timer_panel' not in content[content.find('CallbackQueryHandler'):content.find('CallbackQueryHandler')+5000]:
        # پیدا کردن اولین pattern با menu_settings یا menu_close و اضافه کردن
        for old_anchor in ['menu_settings|', 'menu_close']:
            if f'pattern="[^"]*{old_anchor}' not in content:
                # جستجوی واقعی
                idx = content.find('menu_settings')
                if idx == -1:
                    idx = content.find('menu_close')
                if idx != -1:
                    # پیدا کردن ابتدای pattern="
                    pat_start = content.rfind('pattern="', 0, idx)
                    pat_end = content.find('"', idx)
                    if pat_start != -1 and pat_end != -1:
                        old_pattern = content[pat_start+9:pat_end]
                        new_pattern = old_pattern + '|owner_timer_panel'
                        content = content[:pat_start] + f'pattern="{new_pattern}"' + content[pat_end+1:]
                        print(f"✅ action به الگوی هندلر اضافه شد.")
                        break
        lines = content.split('\n')
except Exception as e:
    print(f"⚠️ هشدار در مرحله 5: {e}")

# ===== 6. نوشتن فایل =====
try:
    with open('modules/start.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("✅ فایل start.py ذخیره شد.")
except Exception as e:
    print(f"❌ خطا در نوشتن: {e}")
    shutil.copy(bak, 'modules/start.py')
    exit(1)

# ===== 7. کامپایل =====
print("\n=== کامپایل ===")
try:
    py_compile.compile('modules/start.py', doraise=True)
    print("✅ کامپایل موفق.")
except Exception as e:
    print(f"❌ خطای کامپایل: {e}")
    shutil.copy(bak, 'modules/start.py')
    print("⚠️ Auto-Rollback انجام شد.")
    exit(1)

# ===== 8. تأیید =====
print("\n=== تأیید ===")
with open('modules/start.py', 'r', encoding='utf-8') as f:
    content = f.read()
count1 = content.count('owner_timer_panel')
count2 = content.count('InlineKeyboardButton("\u23f1')
print(f"تعداد 'owner_timer_panel' در فایل: {count1}")
print(f"تعداد دکمه تایمر: {count2}")

# ===== 9. ری‌استارت =====
print("\n=== ری‌استارت ربات ===")
os.system('pkill -9 -f "main.py"')
time.sleep(3)
os.system('cd ~/groupbot && bash -c "source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &"')
time.sleep(5)
print("✅ ربات ری‌استارت شد.")

print("\n=== 10 خط آخر لاگ ===")
os.system('tail -n 10 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ دکمه «⏱ تنظیمات تایمر» اضافه شد!")
print("="*80)
