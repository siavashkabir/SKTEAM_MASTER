import os, shutil, py_compile, time, sqlite3

print("="*80)
print("🔧 افزودن تنظیمات گزارش به پنل مالک گروه")
print("="*80)

ts = time.strftime("%H%M%S")
bak_db = f'database.py.bak_repset_{ts}'
bak_osg = f'modules/owner_set_group.py.bak_repset_{ts}'
bak_rep = f'modules/reports.py.bak_repset_{ts}'
shutil.copy('database.py', bak_db)
shutil.copy('modules/owner_set_group.py', bak_osg)
shutil.copy('modules/reports.py', bak_rep)
print(f"✅ بکاپ‌ها ساخته شدند.")

# ==== 1. اضافه کردن توابع DB ====
print("\n=== 1. توابع DB ===")
try:
    with open('database.py', 'r', encoding='utf-8') as f:
        db_content = f.read()
    
    if 'def get_report_settings(' not in db_content:
        funcs = '''


# ========== REPORT SETTINGS (Auto-Added) ==========
REP_LIMIT_OPTS = [1, 2, 3, 5, 10, 20, 50, 100]
REP_CD_OPTS = [30, 60, 300, 900, 3600, 21600, 86400]


def get_report_settings(chat_id):
    """برمی‌گرداند (daily_limit, cooldown_seconds)"""
    try:
        dl = int(get_setting(chat_id, "report_daily_limit", "3") or 3)
    except Exception:
        dl = 3
    try:
        cd = int(get_setting(chat_id, "report_cooldown", "300") or 300)
    except Exception:
        cd = 300
    return dl, cd


def set_report_daily_limit(chat_id, value):
    try:
        set_setting(chat_id, "report_daily_limit", str(int(value)))
        return True
    except Exception:
        return False


def set_report_cooldown(chat_id, value):
    try:
        set_setting(chat_id, "report_cooldown", str(int(value)))
        return True
    except Exception:
        return False


def fmt_rep_cd(seconds):
    """نمایش خوانا برای cooldown"""
    try:
        s = int(seconds)
    except Exception:
        return str(seconds)
    if s < 60:
        return f"{s} ثانیه"
    if s < 3600:
        return f"{s // 60} دقیقه"
    if s < 86400:
        return f"{s // 3600} ساعت"
    return f"{s // 86400} روز"
'''
        db_content = db_content.rstrip() + funcs + '\n'
        with open('database.py', 'w', encoding='utf-8') as f:
            f.write(db_content)
        print("✅ توابع DB اضافه شدند.")
    else:
        print("⚠️ از قبل وجود دارند.")
    
    py_compile.compile('database.py', doraise=True)
except Exception as e:
    print(f"❌ خطا: {e}")
    shutil.copy(bak_db, 'database.py')
    exit(1)

# ==== 2. اضافه کردن دکمه‌ها و هندلرها به owner_set_group.py ====
print("\n=== 2. اضافه کردن دکمه‌ها به owner_set_group.py ===")
try:
    with open('modules/owner_set_group.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # --- 2.1: اضافه کردن دکمه‌های تنظیمات گزارش قبل از دکمه بازگشت ---
    back_btn_idx = None
    for i, line in enumerate(lines):
        if 'timer_back:' in line and 'InlineKeyboardButton' in line:
            back_btn_idx = i
            break
    
    if back_btn_idx is None:
        print("❌ دکمه بازگشت پیدا نشد!")
        shutil.copy(bak_osg, 'modules/owner_set_group.py')
        exit(1)
    
    print(f"📍 دکمه بازگشت در خط {back_btn_idx+1}")
    
    # indent
    indent = ' ' * (len(lines[back_btn_idx]) - len(lines[back_btn_idx].lstrip()))
    
    new_btns = [
        f'{indent}[InlineKeyboardButton(f"📊 سهمیه روزانه گزارش: {{get_report_settings(chat_id)[0]}}", callback_data=f"owner_rep_dl:{{uid}}:{{chat_id}}")],\n',
        f'{indent}[InlineKeyboardButton(f"⏱ فاصله بین گزارش‌ها: {{fmt_rep_cd(get_report_settings(chat_id)[1])}}", callback_data=f"owner_rep_cd:{{uid}}:{{chat_id}}")],\n',
    ]
    
    # چک نبودن از قبل
    already = any('owner_rep_dl:' in lines[k] for k in range(max(0, back_btn_idx-10), back_btn_idx+2))
    
    if not already:
        lines = lines[:back_btn_idx] + new_btns + lines[back_btn_idx:]
        print(f"✅ ۲ دکمه جدید اضافه شدند.")
    else:
        print("⚠️ دکمه‌ها از قبل هستند.")
    
    # --- 2.2: import توابع DB در بالای فایل ---
    # چک کردن ایمپورت
    has_import = any('get_report_settings' in lines[k] and 'import' in lines[k] for k in range(0, 30))
    
    if not has_import:
        # پیدا کردن آخرین خط import
        last_import = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                last_import = i
        
        import_line = 'from database import get_report_settings, set_report_daily_limit, set_report_cooldown, fmt_rep_cd, REP_LIMIT_OPTS, REP_CD_OPTS\n'
        lines.insert(last_import + 1, import_line)
        print("✅ ایمپورت توابع اضافه شد.")
    
    # --- 2.3: اضافه کردن هندلرها قبل از "if action == \"timer_back\":" ---
    # دوباره find کردن خط دکمه بازگشت (چون جابجا شد)
    back_btn_idx2 = None
    for i, line in enumerate(lines):
        if 'timer_back:' in line and 'InlineKeyboardButton' in line:
            back_btn_idx2 = i
            break
    
    # پیدا کردن هندلر timer_back (action)
    handler_anchor_idx = None
    for i, line in enumerate(lines):
        if 'if action == "timer_back"' in line or 'action == "timer_back"' in line:
            handler_anchor_idx = i
            break
    
    if handler_anchor_idx is None:
        print("⚠️ هندلر timer_back پیدا نشد. جستجو با الگو...")
        for i, line in enumerate(lines):
            if 'timer_back' in line and 'action' in line:
                handler_anchor_idx = i
                break
    
    if handler_anchor_idx is None:
        print("❌ هندلر timer_back پیدا نشد!")
        shutil.copy(bak_osg, 'modules/owner_set_group.py')
        exit(1)
    
    print(f"📍 هندلر timer_back در خط {handler_anchor_idx+1}")
    
    # indent هندلر
    handler_indent = len(lines[handler_anchor_idx]) - len(lines[handler_anchor_idx].lstrip())
    hi = ' ' * handler_indent
    hib = ' ' * (handler_indent + 4)
    
    new_handlers = f'''{hi}if action == "owner_rep_dl":
{hib}try:
{hib}    cur = get_report_settings(chat_id)[0]
{hib}    try:
{hib}        i = REP_LIMIT_OPTS.index(cur)
{hib}    except ValueError:
{hib}        i = 0
{hib}    new = REP_LIMIT_OPTS[(i + 1) % len(REP_LIMIT_OPTS)]
{hib}    set_report_daily_limit(chat_id, new)
{hib}    try:
{hib}        await _safe_edit(query, "⚙️ تنظیمات این گروه", reply_markup=_build_menu(uid, chat_id))
{hib}    except Exception:
{hib}        pass
{hib}    await query.answer(f"✅ سهمیه: {{new}} گزارش در روز")
{hib}except Exception as e:
{hib}    print("[REP_DL ERR] " + str(e))
{hib}return

{hi}if action == "owner_rep_cd":
{hib}try:
{hib}    cur = get_report_settings(chat_id)[1]
{hib}    try:
{hib}        i = REP_CD_OPTS.index(cur)
{hib}    except ValueError:
{hib}        i = 0
{hib}    new = REP_CD_OPTS[(i + 1) % len(REP_CD_OPTS)]
{hib}    set_report_cooldown(chat_id, new)
{hib}    try:
{hib}        await _safe_edit(query, "⚙️ تنظیمات این گروه", reply_markup=_build_menu(uid, chat_id))
{hib}    except Exception:
{hib}        pass
{hib}    await query.answer(f"✅ فاصله: {{fmt_rep_cd(new)}}")
{hib}except Exception as e:
{hib}    print("[REP_CD ERR] " + str(e))
{hib}return

'''
    
    # چک نبودن از قبل
    already_handler = any('owner_rep_dl' in lines[k] and 'action ==' in lines[k] for k in range(0, len(lines)))
    
    if not already_handler:
        lines.insert(handler_anchor_idx, new_handlers)
        print(f"✅ ۲ هندلر جدید اضافه شدند.")
    else:
        print("⚠️ هندلرها از قبل هستند.")
    
    with open('modules/owner_set_group.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    py_compile.compile('modules/owner_set_group.py', doraise=True)
    print("✅ کامپایل owner_set_group.py موفق.")
    
except Exception as e:
    print(f"❌ خطا: {e}")
    import traceback
    traceback.print_exc()
    shutil.copy(bak_osg, 'modules/owner_set_group.py')
    exit(1)

# ==== 3. تغییر reports.py برای خواندن از DB ====
print("\n=== 3. اصلاح reports.py ===")
try:
    with open('modules/reports.py', 'r', encoding='utf-8') as f:
        rep_content = f.read()
    
    # تغییر مقادیر ثابت به خواندن از DB
    old_cd = 'COOLDOWN_SECONDS = 300  # 5 دقیقه\nDAILY_LIMIT = 3'
    new_cd = '# (از دیتابیس خوانده می‌شود per-group)'
    
    if old_cd in rep_content:
        rep_content = rep_content.replace(old_cd, new_cd)
        print("✅ ثابت‌ها حذف شدند.")
    
    # تغییر import
    old_imp = 'from database import (\n    is_group_owner, is_bot_admin, add_report, get_pending_reports,\n    count_pending_reports, update_report_status, count_user_reports_today\n)'
    new_imp = 'from database import (\n    is_group_owner, is_bot_admin, add_report, get_pending_reports,\n    count_pending_reports, update_report_status, count_user_reports_today,\n    get_report_settings\n)'
    
    if old_imp in rep_content:
        rep_content = rep_content.replace(old_imp, new_imp)
        print("✅ import اصلاح شد.")
    
    # تغییر استفاده از COOLDOWN_SECONDS و DAILY_LIMIT
    old_block = '''    # cooldown
    key = (user.id, chat.id)
    now = time.time()
    last = _REPORT_COOLDOWN.get(key, 0)
    if now - last < COOLDOWN_SECONDS:
        try:
            warn = await context.bot.send_message(
                chat_id=user.id,
                text=f"⏳ لطفاً {int(COOLDOWN_SECONDS - (now - last))} ثانیه دیگر صبر کنید."
            )
            context.job_queue.run_once(_auto_del, 5, chat_id=user.id, data=warn.message_id,
                                        name=f"repcd_{warn.message_id}")
        except Exception:
            pass
        raise ApplicationHandlerStop
    
    # محدودیت روزانه
    today_count = count_user_reports_today(user.id, chat.id)
    if today_count >= DAILY_LIMIT:
        try:
            warn = await context.bot.send_message(
                chat_id=user.id,
                text=f"⛔ سهمیه گزارش روزانه شما ({DAILY_LIMIT} مورد) تمام شده است."
            )
            context.job_queue.run_once(_auto_del, 8, chat_id=user.id, data=warn.message_id,
                                        name=f"replim_{warn.message_id}")
        except Exception:
            pass
        raise ApplicationHandlerStop'''
    
    new_block = '''    # خواندن تنظیمات گروه از DB
    try:
        _daily_limit, _cd_seconds = get_report_settings(chat.id)
    except Exception:
        _daily_limit, _cd_seconds = 3, 300
    
    # cooldown
    key = (user.id, chat.id)
    now = time.time()
    last = _REPORT_COOLDOWN.get(key, 0)
    if now - last < _cd_seconds:
        try:
            _remain = int(_cd_seconds - (now - last))
            warn = await context.bot.send_message(
                chat_id=user.id,
                text=f"⏳ لطفاً {_remain} ثانیه دیگر صبر کنید."
            )
            context.job_queue.run_once(_auto_del, 5, chat_id=user.id, data=warn.message_id,
                                        name=f"repcd_{warn.message_id}")
        except Exception:
            pass
        raise ApplicationHandlerStop
    
    # محدودیت روزانه
    today_count = count_user_reports_today(user.id, chat.id)
    if today_count >= _daily_limit:
        try:
            warn = await context.bot.send_message(
                chat_id=user.id,
                text=f"⛔ سهمیه گزارش روزانه شما ({_daily_limit} مورد) تمام شده است."
            )
            context.job_queue.run_once(_auto_del, 8, chat_id=user.id, data=warn.message_id,
                                        name=f"replim_{warn.message_id}")
        except Exception:
            pass
        raise ApplicationHandlerStop'''
    
    if old_block in rep_content:
        rep_content = rep_content.replace(old_block, new_block)
        print("✅ منطق خواندن از DB اعمال شد.")
    else:
        print("⚠️ الگوی بلوک پیدا نشد. جستجو با regex...")
        import re
        # جایگزینی flexible
        rep_content = re.sub(
            r'COOLDOWN_SECONDS(?!\s*=)',
            '_cd_seconds',
            rep_content
        )
        rep_content = re.sub(
            r'DAILY_LIMIT(?!\s*=)',
            '_daily_limit',
            rep_content
        )
        # اضافه کردن خواندن از DB قبل از "key = (user.id"
        if 'get_report_settings(chat.id)' not in rep_content:
            rep_content = rep_content.replace(
                'key = (user.id, chat.id)',
                '''try:
        _daily_limit, _cd_seconds = get_report_settings(chat.id)
    except Exception:
        _daily_limit, _cd_seconds = 3, 300
    
    key = (user.id, chat.id)''',
                1
            )
        print("✅ با regex اعمال شد.")
    
    with open('modules/reports.py', 'w', encoding='utf-8') as f:
        f.write(rep_content)
    
    py_compile.compile('modules/reports.py', doraise=True)
    print("✅ کامپایل reports.py موفق.")
    
except Exception as e:
    print(f"❌ خطا: {e}")
    import traceback
    traceback.print_exc()
    shutil.copy(bak_rep, 'modules/reports.py')
    exit(1)

# ==== 4. ری‌استارت ====
print("\n=== 4. ری‌استارت ربات ===")
os.system('pkill -9 -f "main.py"')
time.sleep(3)
os.system('cd ~/groupbot && bash -c "source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &"')
time.sleep(8)
os.system('tail -n 12 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ تنظیمات گزارش اضافه شد!")
print("="*80)
print("""
📌 محل تنظیمات:
   منوی مالک گروه → تنظیمات این گروه → 
   
   • 📊 سهمیه روزانه گزارش (کلیک → تعویض مقدار)
   • ⏱ فاصله بین گزارش‌ها (کلیک → تعویض مقدار)

📌 گزینه‌ها:
   • سهمیه روزانه: 1 / 2 / 3 / 5 / 10 / 20 / 50 / 100
   • فاصله: 30 ثانیه / 1 دقیقه / 5 دقیقه / 15 دقیقه / 1 ساعت / 6 ساعت / 24 ساعت
""")
