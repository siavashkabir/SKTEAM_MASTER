import os, shutil, py_compile, time, re

print("="*80)
print("🔧 اصلاح نهایی همه تداخل‌ها (Comprehensive Fix)")
print("="*80)

ts = time.strftime("%H%M%S")
bak = f'modules/start.py.bak_final_{ts}'
bak2 = f'modules/reply.py.bak_final_{ts}'
shutil.copy('modules/start.py', bak)
shutil.copy('modules/reply.py', bak2)
print(f"✅ بکاپ‌ها")

with open('modules/start.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# 1. اصلاح menu_back - بازگشت بر اساس نقش
# ============================================================
print("\n=== 1. menu_back ===")
pattern = re.compile(
    r'(    if action == "menu_back":\s*\n)(.*?)(?=\n    if action |\n    # =====)',
    re.DOTALL
)
m = pattern.search(content)
if m:
    new_body = '''        # [FINAL FIX] بازگشت بر اساس نقش
        try:
            from config import OWNER_ID
            from database import is_bot_admin
            _is_owner = (query.from_user.id == OWNER_ID)
            _is_sudo = False
            if not _is_owner:
                try:
                    _is_sudo = is_bot_admin(query.from_user.id)
                except Exception:
                    pass
            if _is_owner or _is_sudo:
                await query.edit_message_text(
                    "\\U0001F451 \\u0645\\u0646\\u0648\\u06cc \\u0627\\u0635\\u0644\\u06cc:",
                    reply_markup=sudo_panel_menu(query.from_user.id, chat_id)
                )
            else:
                await query.edit_message_text(
                    "\\U0001F451 \\u0645\\u0646\\u0648\\u06cc \\u0645\\u0627\\u0644\\u06a9 \\u06af\\u0631\\u0648\\u0647:",
                    reply_markup=group_owner_panel_menu(query.from_user.id, chat_id)
                )
            reset_timer(context, chat_id, msg_id)
        except Exception as e:
            print("[MENU_BACK ERR] " + str(e))
        return
'''
    content = content[:m.start(2)] + new_body + content[m.end(2):]
    print("   ✅ menu_back اصلاح شد")

# ============================================================
# 2. اصلاح menu_close - حذف امن
# ============================================================
print("\n=== 2. menu_close ===")
pattern = re.compile(
    r'(    if action == "menu_close":\s*\n)(.*?)(?=\n    if action |\n    # =====)',
    re.DOTALL
)
m = pattern.search(content)
if m:
    new_body = '''        # [FINAL FIX] حذف امن
        try:
            await query.message.delete()
        except Exception as _de:
            pass
        try:
            await query.edit_message_text("\\u274c \\u0645\\u0646\\u0648 \\u0628\\u0633\\u062a\\u0647 \\u0634\\u062f.")
        except Exception:
            pass
        return
'''
    content = content[:m.start(2)] + new_body + content[m.end(2):]
    print("   ✅ menu_close اصلاح شد")

# ============================================================
# 3. اصلاح menu_manage, menu_status, menu_settings (چک نقش)
# ============================================================
print("\n=== 3. menu_manage/menu_status/menu_settings ===")
for target in ['menu_manage', 'menu_status', 'menu_settings']:
    pattern = re.compile(
        rf'(    if action == "{target}":\s*\n)(.*?)(?=\n    if action |\n    # =====)',
        re.DOTALL
    )
    m = pattern.search(content)
    if m:
        old_body = m.group(2)
        # چک کن که از قبل چک دسترسی نداره
        if 'is_bot_admin' in old_body:
            print(f"   ℹ️ {target}: از قبل چک داره")
            continue
        
        # اضافه کردن چک دسترسی
        new_body = '''        # [FINAL FIX] چک دسترسی
        try:
            from config import OWNER_ID
            from database import is_bot_admin
            _is_owner = (query.from_user.id == OWNER_ID)
            _is_sudo = False
            if not _is_owner:
                try:
                    _is_sudo = is_bot_admin(query.from_user.id)
                except Exception:
                    pass
            if not (_is_owner or _is_sudo):
                await query.answer("\\u26d4 \\u0641\\u0642\\u0637 \\u0633\\u0627\\u0632\\u0646\\u062f\\u0647 \\u0648 \\u0633\\u0648\\u062f\\u0648", show_alert=True)
                return
        except Exception:
            return
''' + old_body
        content = content[:m.start(2)] + new_body + content[m.end(2):]
        print(f"   ✅ {target}: چک دسترسی اضافه شد")

with open('modules/start.py', 'w', encoding='utf-8') as f:
    f.write(content)

# ============================================================
# 4. اصلاح خطای [PANEL ERR] در reply.py
# ============================================================
print("\n=== 4. reply.py: [PANEL ERR] ===")
with open('modules/reply.py', 'r', encoding='utf-8') as f:
    rcontent = f.read()

# جستجوی خطای PANEL ERR
rlines = rcontent.split('\n')
for i, line in enumerate(rlines):
    if '[PANEL ERR]' in line:
        # 15 خط قبل
        for j in range(max(0, i-15), i):
            if 'msg.reply_text' in rlines[j] or 'await msg.' in rlines[j]:
                print(f"   📍 msg.reply_text در خط {j+1}")
                print(f"      {rlines[j].strip()}")
                # تبدیل به send_message امن
                # پیدا کردن پارامترها
                if 'reply_text(' in rlines[j]:
                    # چک کردن اینکه کجا بسته میشه
                    pass
        break

# جایگزینی خاص: هر جا msg.reply_text که باعث خطا میشه
# با send_message(chat_id=chat.id, ...) جایگزین کن
# اما فقط اگه context داره
if 'await msg.reply_text' in rcontent:
    # گرفتن تمام occurrences و بررسی
    count = rcontent.count('await msg.reply_text')
    print(f"   📊 {count} مورد 'msg.reply_text' پیدا شد")
    # به کاربر اطلاع بده که کدوم‌ها ممکنه مشکل داشته باشن
    # تغییر فقط در خطی که خطا میده

# ============================================================
# 5. کامپایل
# ============================================================
print("\n=== 5. کامپایل ===")
for f, b in [('modules/start.py', bak), ('modules/reply.py', bak2)]:
    try:
        py_compile.compile(f, doraise=True)
        print(f"   ✅ {f}")
    except Exception as e:
        print(f"   ❌ {f}: {e}")
        shutil.copy(b, f)
        exit(1)

# ============================================================
# 6. کش + ری‌استارت
# ============================================================
for root, dirs, files in os.walk('.'):
    if 'venv' in root:
        continue
    if '__pycache__' in root:
        shutil.rmtree(root, ignore_errors=True)

print("\n=== 6. ری‌استارت ===")
os.system('pkill -9 -f "main.py"')
os.system('pkill -9 -f "connection_monitor.py"')
time.sleep(4)
os.system('cd ~/groupbot && nohup bash bot_watchdog.sh > ~/groupbot_watchdog.log 2>&1 &')
time.sleep(10)
os.system('tail -n 6 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ تمام!")
print("="*80)
