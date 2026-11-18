import os, re, glob

print("="*80)
print("🔍 ردیابی کامل شاخه‌های بخش سازنده")
print("="*80)

# ============================================================
# 1. استخراج همه توابع منو (def ...menu...)
# ============================================================
with open('modules/start.py', 'r', encoding='utf-8') as f:
    start_lines = f.readlines()

# تابع‌های منو در start.py + ماژول‌ها
menu_funcs = {}  # func_name -> (file, start_line, end_line, buttons)

def extract_buttons(lines, start, end):
    """استخراج دکمه‌ها با callback_data از یک تابع"""
    buttons = []
    for i in range(start, end):
        line = lines[i]
        if 'InlineKeyboardButton' not in line:
            continue
        # label
        m1 = re.search(r'InlineKeyboardButton\(["\']([^"\']+)["\']', line)
        label = m1.group(1)[:50] if m1 else '?'
        # callback
        cb = None
        m2 = re.search(r'callback_data=["\']([^"\']+)["\']', line)
        if m2:
            cb = m2.group(1)
        else:
            m3 = re.search(r'callback_data=f["\']([^"\']+)["\']', line)
            if m3:
                cb = m3.group(1)
        if cb:
            # نرمال‌سازی
            cb_norm = cb.split(':')[0] if ':' in cb else cb
            buttons.append((label, cb_norm, i+1))
    return buttons

def find_menu_funcs(lines, source):
    """پیدا کردن همه توابع منو"""
    result = {}
    for i, line in enumerate(lines):
        m = re.match(r'^def (\w*(?:menu|panel|_kb)\w*)\s*\(', line)
        if m:
            fname = m.group(1)
            # پایان تابع
            end = len(lines)
            for j in range(i+1, len(lines)):
                if lines[j].startswith('def ') or lines[j].startswith('async def '):
                    end = j
                    break
            buttons = extract_buttons(lines, i, end)
            result[fname] = (source, i+1, end, buttons)
    return result

# از start.py
menu_funcs.update(find_menu_funcs(start_lines, 'modules/start.py'))

# از ماژول‌ها
for mfile in glob.glob('modules/*.py'):
    if '.bak' in mfile or 'crash' in mfile:
        continue
    with open(mfile, 'r', encoding='utf-8') as f:
        mlines = f.readlines()
    menu_funcs.update(find_menu_funcs(mlines, mfile))

print(f"📊 {len(menu_funcs)} تابع منو پیدا شد")

# ============================================================
# 2. استخراج همه handlerها (if action == "X":)
# ============================================================
handlers = {}  # action -> (file, line, reply_markup_func)

def find_handlers(lines, source):
    result = {}
    for i, line in enumerate(lines):
        # action ==
        m = re.match(r'\s*if action == ["\']([^"\']+)["\']', line)
        if not m:
            continue
        action = m.group(1)
        # پیدا کردن انتهای handler
        end = len(lines)
        for j in range(i+1, len(lines)):
            if re.match(r'\s*if action', lines[j]) or lines[j].startswith('def ') or lines[j].startswith('async def '):
                end = j
                break
            if 'raise ApplicationHandlerStop' in lines[j]:
                end = j+1
                break
        
        # استخراج reply_markup
        reply_markup = None
        for k in range(i, end):
            # reply_markup=func_name(...)
            m2 = re.search(r'reply_markup=(\w+)\(', lines[k])
            if m2:
                reply_markup = m2.group(1)
            # InlineKeyboardMarkup(...) مستقیم
            elif 'InlineKeyboardMarkup' in lines[k]:
                reply_markup = 'InlineKeyboardMarkup'
        
        result[action] = (source, i+1, end, reply_markup)
    return result

handlers.update(find_handlers(start_lines, 'modules/start.py'))
for mfile in glob.glob('modules/*.py'):
    if '.bak' in mfile or 'crash' in mfile:
        continue
    with open(mfile, 'r', encoding='utf-8') as f:
        mlines = f.readlines()
    handlers.update(find_handlers(mlines, mfile))

print(f"📊 {len(handlers)} handler پیدا شد")

# ============================================================
# 3. تابع برای ردیابی: از یک منو، دکمه‌ها و مقصدشون
# ============================================================
def trace_menu(menu_name, depth=0, visited=None, max_depth=3):
    """ردیابی یک منو و شاخه‌هاش"""
    if visited is None:
        visited = set()
    
    if menu_name in visited or depth > max_depth:
        return
    
    visited.add(menu_name)
    
    if menu_name not in menu_funcs:
        return
    
    source, start, end, buttons = menu_funcs[menu_name]
    indent = '  ' * depth
    
    # پیدا کردن دکمه بازگشت
    back_btn = None
    for label, cb, ln in buttons:
        if 'بازگشت' in label or 'back' in cb.lower() or 'back' in label.lower():
            back_btn = (label, cb, ln)
            break
    
    # اگه دکمه بازگشت داره، ببین کجا می‌ره
    if back_btn:
        label, cb, ln = back_btn
        if cb in handlers:
            h_source, h_line, h_end, h_markup = handlers[cb]
            dest = h_markup if h_markup else '?'
            print(f"{indent}   🔙 بازگشت ({cb}) → {dest} [{h_source}:{h_line}]")
    
    # ردیابی دکمه‌های زیرمنو
    for label, cb, ln in buttons:
        if label == back_btn[0] if back_btn else False:
            continue
        if 'بستن' in label or 'close' in cb.lower():
            continue
        
        if cb in handlers:
            h_source, h_line, h_end, h_markup = handlers[cb]
            dest = h_markup if h_markup else '?'
            print(f"{indent}   └─ {label} ({cb}) → {dest}")

# ============================================================
# 4. شروع از منوی اصلی سازنده
# ============================================================
print("\n" + "="*80)
print("🎯 ردیابی از منوی اصلی سازنده (sudo_panel_menu)")
print("="*80)

if 'sudo_panel_menu' in menu_funcs:
    source, start, end, buttons = menu_funcs['sudo_panel_menu']
    print(f"\n📍 sudo_panel_menu [{source}:{start}]")
    print(f"   {len(buttons)} دکمه:\n")
    
    for label, cb, ln in buttons:
        # مقصد
        if cb in handlers:
            h_source, h_line, h_end, h_markup = handlers[cb]
            dest = h_markup if h_markup else '?'
            
            # اگه یه منوی دیگه‌ست، ردیابی
            if dest in menu_funcs:
                # از این منو، دکمه بازگشت کجا می‌ره؟
                _, _, _, dest_buttons = menu_funcs[dest]
                back_cb = None
                for dl, dcb, dln in dest_buttons:
                    if 'بازگشت' in dl or 'back' in dcb.lower():
                        back_cb = dcb
                        break
                
                if back_cb and back_cb in handlers:
                    _, _, _, back_markup = handlers[back_cb]
                    back_dest = back_markup if back_markup else '?'
                    print(f"   🔘 {label}")
                    print(f"      └─ opens: {dest}")
                    print(f"         🔙 بازگشتش → {back_dest}")
                else:
                    print(f"   🔘 {label}")
                    print(f"      └─ opens: {dest}")
                    print(f"         ⚠️ بازگشت نداره!")
            else:
                print(f"   🔘 {label}")
                print(f"      └─ {dest} (handler: {h_source}:{h_line})")
        else:
            print(f"   🔘 {label} ({cb})")
            print(f"      ❌ handler نداره!")

# ============================================================
# 5. بررسی بخش سازنده (owner_section_menu)
# ============================================================
print("\n" + "="*80)
print("🔧 بخش سازنده (owner_section_menu)")
print("="*80)

if 'owner_section_menu' in menu_funcs:
    source, start, end, buttons = menu_funcs['owner_section_menu']
    print(f"\n📍 owner_section_menu [{source}:{start}]")
    print(f"   {len(buttons)} دکمه:\n")
    
    for label, cb, ln in buttons:
        if cb in handlers:
            h_source, h_line, h_end, h_markup = handlers[cb]
            dest = h_markup if h_markup else '?'
            
            if dest in menu_funcs:
                _, _, _, dest_buttons = menu_funcs[dest]
                back_cb = None
                for dl, dcb, dln in dest_buttons:
                    if 'بازگشت' in dl or 'back' in dcb.lower():
                        back_cb = dcb
                        break
                
                if back_cb and back_cb in handlers:
                    _, _, _, back_markup = handlers[back_cb]
                    back_dest = back_markup if back_markup else '?'
                    print(f"   🔘 {label}")
                    print(f"      └─ opens: {dest}")
                    print(f"         🔙 بازگشتش → {back_dest}")
                else:
                    print(f"   🔘 {label}")
                    print(f"      └─ opens: {dest}")
                    print(f"         ⚠️ بازگشت نداره!")
            else:
                print(f"   🔘 {label} → {dest}")
        else:
            print(f"   🔘 {label} ({cb}) → ❌ handler نداره!")

print("\n" + "="*80)
print("✅ تحلیل کامل شد (فقط گزارش - هیچ تغییری اعمال نشد)")
print("="*80)
