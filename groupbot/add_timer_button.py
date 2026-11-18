import os, shutil, py_compile, time, re, subprocess

print("="*80)
print("🔧 اضافه کردن دکمه «⏱ تنظیمات تایمر» به منوی تنظیمات")
print("="*80)

# ===== 1. بکاپ =====
ts = time.strftime("%H%M%S")
bak = f'modules/start.py.bak_timerbtn_{ts}'
shutil.copy('modules/start.py', bak)
print(f"✅ بکاپ: {bak}")

# ===== 2. پیدا کردن owner_settings_menu و اضافه کردن دکمه =====
print("\n=== اصلاح owner_settings_menu ===")
try:
    with open('modules/start.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # پیدا کردن تابع owner_settings_menu
    pattern = re.compile(
        r'(def owner_settings_menu\([^)]*\):.*?return InlineKeyboardMarkup\(\[)(.*?)(\]\))',
        re.DOTALL
    )
    match = pattern.search(content)
    
    if not match:
        print("❌ تابع owner_settings_menu پیدا نشد!")
        shutil.copy(bak, 'modules/start.py')
        exit(1)
    
    func_start = match.group(1)
    buttons_block = match.group(2)
    func_end = match.group(3)
    
    print(f"✅ تابع owner_settings_menu پیدا شد.")
    
    # بررسی اینکه آیا دکمه تایمر از قبل هست یا نه
    if 'owner_timer_panel' in buttons_block:
        print("⚠️ دکمه تایمر از قبل وجود دارد.")
    else:
        # اضافه کردن دکمه جدید قبل از آخرین دکمه (بازگشت)
        # پیدا کردن آخرین [InlineKeyboardButton
        last_btn_pattern = re.compile(r'(\n\s*\[InlineKeyboardButton\([^\]]*callback_data=f?"menu_close[^\]]*\)\],?\s*)$')
        if last_btn_pattern.search(buttons_block):
            # اضافه کردن دکمه قبل از بازگشت
            new_btn = '''\n        [InlineKeyboardButton("\\u23f1 \\u062a\\u0646\\u0637\\u06cc\\u0645\\u0627\\u062a \\u062a\\u0627\\u06cc\\u0645\\u0631", callback_data=f"owner_timer_panel:{uid}:{chat_id}")],'''
            new_buttons = last_btn_pattern.sub(new_btn + r'\1', buttons_block)
        else:
            # اگر الگو نبود، دکمه را به انتهای لیست اضافه کن
            new_btn = ''',\n        [InlineKeyboardButton("\\u23f1 \\u062a\\u0646\\u0637\\u06cc\\u0645\\u0627\\u062a \\u062a\\u0627\\u06cc\\u0645\\u0631", callback_data=f"owner_timer_panel:{uid}:{chat_id}")]'''
            new_buttons = buttons_block.rstrip().rstrip(',') + new_btn
        
        new_func = func_start + new_buttons + func_end
        content = content.replace(match.group(0), new_func)
        print("✅ دکمه «⏱ تنظیمات تایمر» اضافه شد.")
    
    # ===== 3. اضافه کردن هندلر owner_timer_panel =====
    if 'action == "owner_timer_panel"' not in content:
        handler = '''
    # ===== TIMER PANEL HANDLER =====
    if action == "owner_timer_panel":
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
                await query.answer("\\u26d4 \\u0641\\u0642\\u0637 \\u0633\\u0627\\u0632\\u0646\\u062f\\u0647 \\u0648 \\u0633\\u0648\\u062f\\u0648 \\u062f\\u0633\\u062a\\u0631\\u0633\\u06cc \\u062f\\u0627\\u0631\\u0646\\u062f.", show_alert=True)
                return
            from modules.owner_set_group import build_menu
            await query.edit_message_text(
                "\\u23f1 \\u062a\\u0646\\u0637\\u06cc\\u0645\\u0627\\u062a \\u062a\\u0627\\u06cc\\u0645\\u0631 \\u067e\\u0646\\u0644\\n\\n"
                "\\u062a\\u0627\\u06cc\\u0645\\u0631 \\u0628\\u0631 \\u0627\\u0633\\u0627\\u0633 \\u0639\\u062f\\u0645 \\u0641\\u0639\\u0627\\u0644\\u06cc\\u062a \\u0627\\u0633\\u062a \\u0648 \\u0628\\u0627 \\u0647\\u0631 \\u06a9\\u0644\\u06cc\\u06a9 \\u0631\\u06cc\\u0633\\u062a \\u0645\\u06cc\\u200c\\u0634\\u0648\\u062f.",
                reply_markup=build_menu(uid_check, query.message.chat.id)
            )
        except Exception as e:
            print("[OWNER TIMER PANEL ERR] " + str(e))
        return

'''
        # درج قبل از "if action == \\"aperm_user\\""
        anchor_patterns = ['if action == "aperm_user":', 'if action == "menu_settings":']
        inserted = False
        for anchor in anchor_patterns:
            if anchor in content:
                content = content.replace(anchor, handler + anchor, 1)
                inserted = True
                print(f"✅ هندلر owner_timer_panel قبل از '{anchor}' اضافه شد.")
                break
        if not inserted:
            print("⚠️ نقطه اتصال پیدا نشد. هندلر اضافه نشد.")
    
    # ===== 4. اضافه کردن action به الگوی هندلر =====
    if 'owner_timer_panel' not in re.findall(r'pattern="[^"]*"', content):
        # پیدا کردن pattern menu_settings یا menu_close
        for old_anchor in ['menu_settings|menu_status', 'menu_close']:
            m2 = re.search(r'pattern="([^"]*' + re.escape(old_anchor.split('|')[0]) + r'[^"]*)"', content)
            if m2:
                old_pat = m2.group(1)
                new_pat = old_pat + '|owner_timer_panel'
                content = content.replace(f'pattern="{old_pat}"', f'pattern="{new_pat}"')
                print(f"✅ action owner_timer_panel به الگوی هندلر اضافه شد.")
                break
    
    with open('modules/start.py', 'w', encoding='utf-8') as f:
        f.write(content)

except Exception as e:
    print(f"❌ خطا: {e}")
    import traceback
    traceback.print_exc()
    shutil.copy(bak, 'modules/start.py')
    print("⚠️ Auto-Rollback انجام شد.")
    exit(1)

# ===== 5. کامپایل =====
print("\n=== کامپایل start.py ===")
try:
    py_compile.compile('modules/start.py', doraise=True)
    print("✅ کامپایل موفق.")
except Exception as e:
    print(f"❌ خطای کامپایل: {e}")
    shutil.copy(bak, 'modules/start.py')
    print("⚠️ Auto-Rollback انجام شد.")
    exit(1)

# ===== 6. تأیید =====
print("\n=== تأیید نهایی ===")
r = subprocess.run(['grep', '-n', 'owner_timer_panel', 'modules/start.py'], capture_output=True, text=True)
for line in r.stdout.split('\n'):
    if line.strip():
        print(f"   {line.strip()[:150]}")

# ===== 7. ری‌استارت =====
print("\n=== ری‌استارت ربات ===")
os.system('pkill -9 -f "main.py"')
time.sleep(3)
os.system('cd ~/groupbot && bash -c "source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &"')
time.sleep(5)
print("✅ ربات ری‌استارت شد.")

os.system('tail -n 10 ~/groupbot_bot.log')
