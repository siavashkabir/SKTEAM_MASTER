import os, shutil, py_compile, time, re

print("="*80)
print("🔧 Consolidate Timer Menu + Add 2 New Buttons")
print("="*80)

ts = time.strftime("%H%M%S")
bak1 = f'modules/owner_set_group.py.bak_cons_{ts}'
bak2 = f'database.py.bak_cons_{ts}'

shutil.copy('modules/owner_set_group.py', bak1)
shutil.copy('database.py', bak2)
print(f"✅ بکاپ‌ها: {bak1} | {bak2}")

# ============ STEP 1: Add DB functions ============
print("\n=== STEP 1: افزودن توابع دیتابیس ===")
try:
    with open('database.py', 'r', encoding='utf-8') as f:
        db_content = f.read()
    
    if 'def get_chat_panel_warning' not in db_content:
        new_funcs = '''


# ===== PANEL WARNING & SUDO TIMER ACCESS (Auto-Added) =====
def get_chat_panel_warning(chat_id):
    """بررسی فعال بودن هشدار بسته شدن پنل"""
    try:
        v = get_setting(chat_id, "panel_warning_enabled", None)
        if v is None:
            return int(get_setting(0, "panel_warning_enabled", "0") or 0)
        return int(v)
    except Exception:
        return 0


def set_chat_panel_warning(chat_id, enabled):
    """تنظیم هشدار برای یک گروه"""
    try:
        set_setting(chat_id, "panel_warning_enabled", str(int(enabled)))
        return True
    except Exception:
        return False


def get_sudo_timer_access():
    """بررسی دسترسی سودو به تنظیمات تایمر"""
    try:
        return int(get_setting(0, "sudo_timer_access", "0") or 0)
    except Exception:
        return 0


def set_sudo_timer_access(enabled):
    """تنظیم دسترسی سودو (فقط سازنده)"""
    try:
        set_setting(0, "sudo_timer_access", str(int(enabled)))
        return True
    except Exception:
        return False
'''
        db_content = db_content.rstrip() + new_funcs + '\n'
        with open('database.py', 'w', encoding='utf-8') as f:
            f.write(db_content)
        print("✅ توابع جدید به database.py اضافه شدند.")
    else:
        print("⚠️ توابع از قبل وجود دارند.")
    
    py_compile.compile('database.py', doraise=True)
    print("✅ database.py کامپایل شد.")
except Exception as e:
    print(f"❌ خطا: {e}")
    shutil.copy(bak2, 'database.py')
    exit(1)

# ============ STEP 2: Process owner_set_group.py ============
print("\n=== STEP 2: بازسازی owner_set_group.py ===")
try:
    with open('modules/owner_set_group.py', 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.split('\n')
    
    # --- 2.1: Find build_menu and its button block ---
    menu_start = None
    for i, line in enumerate(lines):
        if line.startswith('def build_menu('):
            menu_start = i
            break
    if menu_start is None:
        print("❌ build_menu پیدا نشد!")
        raise Exception("build_menu not found")
    
    # Find return InlineKeyboardMarkup
    return_idx = None
    for j in range(menu_start, len(lines)):
        if 'return InlineKeyboardMarkup([' in lines[j]:
            return_idx = j
            break
    if return_idx is None:
        raise Exception("return InlineKeyboardMarkup not found")
    
    # Find closing ])
    close_idx = None
    for k in range(return_idx, len(lines)):
        if lines[k].strip() in (']])', '])'):
            close_idx = k
            break
    if close_idx is None:
        raise Exception("close ]) not found")
    
    print(f"📍 build_menu: خطوط {menu_start+1} تا {close_idx+1}")
    
    # --- 2.2: Find and remove timer buttons (lines containing specific callback_data) ---
    timer_actions = ['owner_set_cd:', 'owner_set_del:', 'owner_set_pt:', 'owner_set_ed:']
    removed_count = 0
    insert_at = None  # Where to put new timer_menu button
    
    new_button_lines = []
    for i in range(return_idx + 1, close_idx):
        line = lines[i]
        # Check if this is a timer button
        is_timer = any(act in line for act in timer_actions)
        # Find the first AI button for insertion
        if insert_at is None and 'owner_set_ai_on' in line:
            insert_at = i
            break
    
    if insert_at is None:
        # Fallback: insert before return
        insert_at = close_idx
    
    # Build new button line (matching indentation)
    # Determine indentation from insert_at line
    indent = ' ' * (len(lines[insert_at]) - len(lines[insert_at].lstrip()))
    new_timer_button = f'{indent}[InlineKeyboardButton("\u23f1 \u062a\u0646\u0637\u06cc\u0645\u0627\u062a \u062a\u0627\u06cc\u0645\u0631", callback_data=f"timer_menu:{{uid}}:{{chat_id}}")],'
    
    # Remove timer lines and insert new button
    new_lines = []
    for i, line in enumerate(lines):
        if return_idx < i < close_idx and any(act in line for act in timer_actions):
            removed_count += 1
            continue  # Skip timer buttons
        if i == insert_at:
            new_lines.append(new_timer_button)
        new_lines.append(line)
    lines = new_lines
    print(f"✅ {removed_count} دکمه تایمر حذف شد.")
    print(f"✅ دکمه واحد «⏱ تنظیمات تایمر» اضافه شد.")
    
    # --- 2.3: Add build_timer_menu function BEFORE build_menu ---
    menu_start_new = None
    for i, line in enumerate(lines):
        if line.startswith('def build_menu('):
            menu_start_new = i
            break
    
    timer_func = '''
def build_timer_menu(uid, chat_id):
    """منوی متمرکز تنظیمات تایمر - فقط سازنده و سودو"""
    cd = get_chat_cooldown(chat_id)
    pd = get_chat_panel_delete(chat_id)
    pt = get_chat_panel_timeout(chat_id)
    ed = get_chat_expire_delete(chat_id)
    try:
        from database import get_chat_panel_warning, get_sudo_timer_access
        warn = get_chat_panel_warning(chat_id)
        sudo = get_sudo_timer_access()
    except Exception:
        warn = 0
        sudo = 0
    warn_icon = "\u2705" if warn == 1 else "\u274c"
    sudo_icon = "\u2705" if sudo == 1 else "\u274c"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"\u23f0 Cooldown: {fmt_sec(cd)}", callback_data=f"owner_set_cd:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"\U0001f5d1 \u062d\u0630\u0641 \u067e\u0646\u0644: {fmt_sec(pd)}", callback_data=f"owner_set_del:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"\u23f3 \u0627\u0646\u0642\u0636\u0627\u06cc \u067e\u0646\u0644: {fmt_sec(pt)}", callback_data=f"owner_set_pt:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"\U0001f4ac \u062d\u0630\u0641 \u067e\u06cc\u0627\u0645 expire: {fmt_sec(ed)}", callback_data=f"owner_set_ed:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"\U0001f514 \u0647\u0634\u062f\u0627\u0631 \u0628\u0633\u062a\u0647 \u0634\u062f\u0646: {warn_icon}", callback_data=f"owner_set_warn:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"\U0001f464 \u062f\u0633\u062a\u0631\u0633\u06cc \u0633\u0648\u062f\u0648: {sudo_icon}", callback_data=f"owner_set_sudo:{uid}:{chat_id}")],
        [InlineKeyboardButton("\U0001f519 \u0628\u0627\u0632\u06af\u0634\u062a", callback_data=f"timer_back:{uid}:{chat_id}")],
    ])


'''
    lines.insert(menu_start_new, timer_func)
    print("✅ تابع build_timer_menu اضافه شد.")
    
    # --- 2.4: Add new handlers in owner_set_cb ---
    # Find anchor: `if action == "owner_set_pt":`
    anchor_idx = None
    for i, line in enumerate(lines):
        if 'action == "owner_set_pt"' in line:
            anchor_idx = i
            break
    
    if anchor_idx is None:
        raise Exception("anchor owner_set_pt not found")
    
    new_handlers = '''    if action == "timer_menu":
        try:
            await safe_edit(query, "\u23f1 \u062a\u0646\u0637\u06cc\u0645\u0627\u062a \u062a\u0627\u06cc\u0645\u0631\\n\\n\u062a\u0627\u06cc\u0645\u0631 \u0628\u0631 \u0627\u0633\u0627\u0633 \u0639\u062f\u0645 \u0641\u0639\u0627\u0644\u06cc\u062a \u0627\u0633\u062a.", reply_markup=build_timer_menu(uid, chat_id))
        except Exception as e:
            print("[TIMER MENU ERR] " + str(e))
        return

    if action == "timer_back":
        try:
            await safe_edit(query, "\u2699\ufe0f \u062a\u0646\u0637\u06cc\u0645\u0627\u062a \u06af\u0631\u0648\u0647", reply_markup=build_menu(uid, chat_id))
        except Exception as e:
            print("[TIMER BACK ERR] " + str(e))
        return

    if action == "owner_set_warn":
        try:
            from database import get_chat_panel_warning, set_chat_panel_warning
            cur = get_chat_panel_warning(chat_id)
            new = 0 if cur == 1 else 1
            set_chat_panel_warning(chat_id, new)
            try:
                await safe_edit(query, "\u23f1 \u062a\u0646\u0637\u06cc\u0645\u0627\u062a \u062a\u0627\u06cc\u0645\u0631", reply_markup=build_timer_menu(uid, chat_id))
            except Exception:
                pass
            await query.answer("\U0001f514 \u0647\u0634\u062f\u0627\u0631 " + ("\u0641\u0639\u0627\u0644" if new == 1 else "\u063a\u06cc\u0631\u0641\u0639\u0627\u0644"))
        except Exception as e:
            print("[WARN ERR] " + str(e))
        return

    if action == "owner_set_sudo":
        try:
            from config import OWNER_ID
            if user.id != OWNER_ID:
                await query.answer("\u26d4 \u0641\u0642\u0637 \u0633\u0627\u0632\u0646\u062f\u0647 \u062f\u0633\u062a\u0631\u0633\u06cc \u062f\u0627\u0631\u062f.", show_alert=True)
                return
            from database import get_sudo_timer_access, set_sudo_timer_access
            cur = get_sudo_timer_access()
            new = 0 if cur == 1 else 1
            set_sudo_timer_access(new)
            try:
                await safe_edit(query, "\u23f1 \u062a\u0646\u0637\u06cc\u0645\u0627\u062a \u062a\u0627\u06cc\u0645\u0631", reply_markup=build_timer_menu(uid, chat_id))
            except Exception:
                pass
            await query.answer("\U0001f464 \u062f\u0633\u062a\u0631\u0633\u06cc \u0633\u0648\u062f\u0648 " + ("\u0641\u0639\u0627\u0644" if new == 1 else "\u063a\u06cc\u0631\u0641\u0639\u0627\u0644"))
        except Exception as e:
            print("[SUDO ERR] " + str(e))
        return

'''
    lines.insert(anchor_idx, new_handlers)
    print("✅ ۴ هندلر جدید اضافه شدند.")
    
    with open('modules/owner_set_group.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    py_compile.compile('modules/owner_set_group.py', doraise=True)
    print("✅ owner_set_group.py کامپایل شد.")
    
except Exception as e:
    print(f"❌ خطا: {e}")
    import traceback
    traceback.print_exc()
    shutil.copy(bak1, 'modules/owner_set_group.py')
    print("⚠️ Auto-Rollback انجام شد.")
    exit(1)

# ============ STEP 3: Update handler pattern in start.py ============
print("\n=== STEP 3: به‌روزرسانی الگوی هندلر در start.py ===")
try:
    with open('modules/start.py', 'r', encoding='utf-8') as f:
        start_content = f.read()
    
    # Find pattern containing owner_set_cd
    m = re.search(r'pattern="([^"]*owner_set_cd[^"]*)"', start_content)
    if m and 'timer_menu' not in m.group(1):
        old_pat = m.group(1)
        new_pat = old_pat + '|timer_menu|timer_back|owner_set_warn|owner_set_sudo'
        start_content = start_content.replace(f'pattern="{old_pat}"', f'pattern="{new_pat}"')
        with open('modules/start.py', 'w', encoding='utf-8') as f:
            f.write(start_content)
        print("✅ الگوی هندلر به‌روزرسانی شد.")
    else:
        print("⚠️ الگو پیدا نشد یا از قبل به‌روز است.")
    
    py_compile.compile('modules/start.py', doraise=True)
    print("✅ start.py کامپایل شد.")
except Exception as e:
    print(f"❌ خطا: {e}")
    shutil.copy(bak1, 'modules/owner_set_group.py')
    exit(1)

# ============ STEP 4: Restart bot ============
print("\n=== STEP 4: ری‌استارت ربات ===")
os.system('pkill -9 -f "main.py"')
time.sleep(3)
os.system('cd ~/groupbot && bash -c "source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &"')
time.sleep(5)
print("✅ ربات ری‌استارت شد.")

os.system('tail -n 15 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ همه چیز با موفقیت انجام شد!")
print("="*80)
