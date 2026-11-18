import os, shutil, py_compile, time, re

print("="*80)
print("🔧 جلوگیری از باز شدن چند پنل پشت سر هم")
print("="*80)

ts = time.strftime("%H%M%S")
bak1 = f'modules/reply.py.bak_multipanel_{ts}'
bak2 = f'modules/start.py.bak_multipanel_{ts}'
shutil.copy('modules/reply.py', bak1)
shutil.copy('modules/start.py', bak2)
print(f"✅ بکاپ‌ها: {bak1} | {bak2}")

# === 1. اضافه کردن ACTIVE_PANELS به start.py ===
print("\n=== 1. اضافه کردن ACTIVE_PANELS به start.py ===")
with open('modules/start.py', 'r', encoding='utf-8') as f:
    start_content = f.read()

if 'ACTIVE_PANELS = {}' not in start_content:
    if 'LAST_ACTIVITY = {}' in start_content:
        start_content = start_content.replace(
            'LAST_ACTIVITY = {}',
            'LAST_ACTIVITY = {}\nACTIVE_PANELS = {}  # {(uid, chat_id): message_id}',
            1
        )
        print("✅ ACTIVE_PANELS اضافه شد.")
    else:
        # درج بعد از import‌ها
        lines = start_content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                continue
            lines.insert(i, '\nACTIVE_PANELS = {}  # {(uid, chat_id): message_id}\n')
            break
        start_content = '\n'.join(lines)
        print("✅ ACTIVE_PANELS اضافه شد (روش ۲).")

# === 2. اصلاح auto_close برای پاک کردن از ACTIVE_PANELS ===
print("\n=== 2. اصلاح auto_close ===")
if 'ACTIVE_PANELS.pop' not in start_content:
    # پیدا کردن auto_close
    m = re.search(r'(async def auto_close\(context\):.*?)(?=\nasync def |\ndef |\Z)', start_content, re.DOTALL)
    if m:
        old_func = m.group(1)
        # اضافه کردن پاکسازی در انتهای تابع
        new_func = old_func.rstrip() + '''
    # پاک کردن از لیست پنل‌های فعال
    try:
        keys_to_remove = [k for k, v in ACTIVE_PANELS.items() if v == _msg_id]
        for k in keys_to_remove:
            del ACTIVE_PANELS[k]
            print(f"[ACTIVE PANELS] Removed: {k}")
    except Exception as _ape:
        print("[ACTIVE PANELS CLEAN ERR] " + str(_ape))
'''
        start_content = start_content.replace(old_func, new_func)
        print("✅ auto_close اصلاح شد.")

with open('modules/start.py', 'w', encoding='utf-8') as f:
    f.write(start_content)

py_compile.compile('modules/start.py', doraise=True)
print("✅ start.py کامپایل شد.")

# === 3. اصلاح reply.py: جلوگیری از پنل تکراری ===
print("\n=== 3. اصلاح reply.py ===")
with open('modules/reply.py', 'r', encoding='utf-8') as f:
    reply_content = f.read()

# پیدا کردن بخشی که پنل رو باز می‌کنه
# دنبال "sent = await msg.reply_text" با mark برای پنل
old_panel_start = '''    if t_norm in ("پنل", "panel"):
        # چک کاربر
        is_sudo_user = False
        try:
            if user.id == OWNER_ID:
                is_sudo_user = True
            elif is_bot_admin(user.id):
                is_sudo_user = True
        except Exception:
            pass
        is_gowner_user = is_group_owner(chat.id, user.id)
        is_tg_admin = await is_admin(chat, user.id)

        # اگه هیچ‌کدوم نبود، رد کن
        if not is_sudo_user and not is_gowner_user and not is_tg_admin:
            return

        try:
            from modules.start import (
                sudo_panel_menu, group_owner_panel_menu, group_panel_menu, reset_timer,
                ACTIVE_PANELS
            )
            if is_sudo_user:'''

new_panel_start = '''    if t_norm in ("پنل", "panel"):
        # چک کاربر
        is_sudo_user = False
        try:
            if user.id == OWNER_ID:
                is_sudo_user = True
            elif is_bot_admin(user.id):
                is_sudo_user = True
        except Exception:
            pass
        is_gowner_user = is_group_owner(chat.id, user.id)
        is_tg_admin = await is_admin(chat, user.id)

        # اگه هیچ‌کدوم نبود، رد کن
        if not is_sudo_user and not is_gowner_user and not is_tg_admin:
            return

        # [NEW] چک پنل فعال برای همین کاربر
        try:
            from modules.start import ACTIVE_PANELS
            key = (user.id, chat.id)
            if key in ACTIVE_PANELS:
                old_msg_id = ACTIVE_PANELS[key]
                try:
                    # چک کنیم پیام هنوز وجود داره یا نه
                    await context.bot.delete_message(chat_id=chat.id, message_id=old_msg_id)
                    print(f"[PANEL GUARD] Removed old panel msg={old_msg_id} for user={user.id}")
                except Exception:
                    # پیام پاک شده بود، از لیست حذف کن
                    pass
                del ACTIVE_PANELS[key]

            # پاک کردن پیام "پنل" کاربر
            try:
                await msg.delete()
            except Exception:
                pass
        except Exception as _pge:
            print("[PANEL GUARD ERR] " + str(_pge))

        try:
            from modules.start import (
                sudo_panel_menu, group_owner_panel_menu, group_panel_menu, reset_timer
            )
            if is_sudo_user:'''

if old_panel_start in reply_content:
    reply_content = reply_content.replace(old_panel_start, new_panel_start)
    print("✅ ابتدای هندلر پنل اصلاح شد.")
else:
    print("⚠️ ابتدای هندلر پیدا نشد، جستجو با regex...")
    pattern = r'(if t_norm in \("پنل", "panel"\):.*?)(try:\s*\n\s*from modules\.start import \()'
    match = re.search(pattern, reply_content, re.DOTALL)
    if match:
        # جایگزینی در محل مناسب
        insert_pos = match.end(1)
        guard = '''
        # [NEW] چک پنل فعال برای همین کاربر
        try:
            from modules.start import ACTIVE_PANELS
            key = (user.id, chat.id)
            if key in ACTIVE_PANELS:
                old_msg_id = ACTIVE_PANELS[key]
                try:
                    await context.bot.delete_message(chat_id=chat.id, message_id=old_msg_id)
                    print(f"[PANEL GUARD] Removed old panel msg={old_msg_id}")
                except Exception:
                    pass
                del ACTIVE_PANELS[key]
            try:
                await msg.delete()
            except Exception:
                pass
        except Exception as _pge:
            print("[PANEL GUARD ERR] " + str(_pge))
        
        '''
        reply_content = reply_content[:insert_pos] + guard + reply_content[insert_pos:]
        print("✅ (regex) Guard اضافه شد.")

# === 4. اضافه کردن ذخیره در ACTIVE_PANELS بعد از ارسال پنل ===
# باید بعد از sent = await msg.reply_text (...) اضافه بشه
if 'ACTIVE_PANELS[(user.id, chat.id)]' not in reply_content:
    # پیدا کردن خطی که reset_timer رو صدا می‌زنه
    pattern2 = r'(sent = await msg\.reply_text\([^)]+\)\s*\n\s*reset_timer\(context, sent\.chat\.id, sent\.message_id\))'
    match2 = re.search(pattern2, reply_content, re.DOTALL)
    if match2:
        old_block = match2.group(1)
        new_block = old_block + '''
            # [NEW] ذخیره پنل فعال
            try:
                from modules.start import ACTIVE_PANELS
                ACTIVE_PANELS[(user.id, chat.id)] = sent.message_id
                print(f"[PANEL GUARD] Registered panel msg={sent.message_id} for user={user.id}")
            except Exception as _pse:
                print("[PANEL GUARD SAVE ERR] " + str(_pse))'''
        reply_content = reply_content.replace(old_block, new_block, 1)
        print("✅ ذخیره در ACTIVE_PANELS اضافه شد.")
    else:
        print("⚠️ الگوی reset_timer پیدا نشد!")

with open('modules/reply.py', 'w', encoding='utf-8') as f:
    f.write(reply_content)

try:
    py_compile.compile('modules/reply.py', doraise=True)
    print("✅ reply.py کامپایل شد.")
except Exception as e:
    print(f"❌ خطای کامپایل: {e}")
    shutil.copy(bak1, 'modules/reply.py')
    shutil.copy(bak2, 'modules/start.py')
    exit(1)

# === ری‌استارت ===
print("\n=== ری‌استارت ربات ===")
os.system('pkill -9 -f "main.py"')
time.sleep(3)
os.system('cd ~/groupbot && bash -c "source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &"')
time.sleep(8)
os.system('tail -n 10 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ حالا اگه پنل باز باشه، با زدن 'پنل' دوباره پنل باز نمی‌شه!")
print("="*80)
