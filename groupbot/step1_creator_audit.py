import os, re, glob

print("="*80)
print("🎯 قدم ۱: بررسی دقیق ۸ دکمه معیوب پنل سازنده")
print("="*80)

# ============================================================
# 1. جمع‌آوری کالبک‌های پنل سازنده
# ============================================================
CREATOR_MENUS = [
    'sudo_panel_menu',
    'owner_section_menu',
    'owner_manage_menu',
    'group_owner_panel_menu',
]

with open('modules/start.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# کالبک‌های موجود در پنل سازنده
creator_callbacks = {}  # cb -> (menu_func, line_num, label)

for menu_func in CREATOR_MENUS:
    start = None
    for i, line in enumerate(lines):
        if line.startswith(f'def {menu_func}('):
            start = i
            break
    if start is None:
        continue
    
    end = len(lines)
    for j in range(start+1, len(lines)):
        if lines[j].startswith('def ') or lines[j].startswith('async def '):
            end = j
            break
    
    for i in range(start, end):
        line = lines[i]
        if 'InlineKeyboardButton' not in line:
            continue
        
        m = re.search(r'callback_data=["\']([^"\']+)["\']', line)
        cb = None
        if m:
            cb = m.group(1)
        else:
            m = re.search(r'callback_data=f["\']([^"\']+)["\']', line)
            if m:
                cb = m.group(1)
        
        if not cb:
            continue
        
        m2 = re.search(r'InlineKeyboardButton\(["\']([^"\']+)["\']', line)
        label = m2.group(1)[:50] if m2 else '?'
        
        cb_norm = cb.split(':')[0] if ':' in cb else cb
        creator_callbacks[cb_norm] = (menu_func, i+1, label)

print(f"\n📊 دکمه‌های پنل سازنده: {len(creator_callbacks)}")

# ============================================================
# 2. جمع‌آوری همه handlerها
# ============================================================
handlers = set()
for mfile in ['modules/start.py'] + glob.glob('modules/*.py'):
    if '.bak' in mfile or 'crash' in mfile or not os.path.exists(mfile):
        continue
    with open(mfile, 'r', encoding='utf-8') as f:
        content = f.read()
    for m in re.finditer(r'action\s*==\s*["\']([^"\']+)["\']', content):
        handlers.add(m.group(1))
    for m in re.finditer(r'action\.startswith\(["\']([^"\']+)["\']', content):
        handlers.add(m.group(1))

print(f"📊 handlerهای موجود: {len(handlers)}")

# ============================================================
# 3. جمع‌آوری patternها
# ============================================================
patterns = []
for i, line in enumerate(lines):
    if 'add_handler' in line and 'pattern=' in line:
        m = re.search(r'pattern=["\']([^"\']+)["\']', line)
        if m:
            pat = m.group(1)
            parts = pat.replace('^(', '').replace(')$', '').split('|')
            patterns.append((i+1, parts))

print(f"📊 patternها: {len(patterns)}")

# ============================================================
# 4. تحلیل هر دکمه
# ============================================================
print("\n" + "="*80)
print("🔍 تحلیل دقیق هر دکمه (کدوم مرحله شکست می‌خوره)")
print("="*80)

all_pattern_parts = set()
for _, parts in patterns:
    all_pattern_parts.update(parts)

problems = []
working = []

for cb, (menu_func, line_num, label) in sorted(creator_callbacks.items()):
    # چک ۱: در pattern هست؟
    in_pattern = cb in all_pattern_parts
    
    # چک ۲: handler داره؟
    has_handler = cb in handlers
    
    # چک ۳: برای startswith
    has_startswith = any(cb.startswith(s) for s in handlers if s.endswith('_'))
    
    status = "✅"
    issue = []
    
    if not in_pattern and not has_startswith:
        status = "❌"
        issue.append("pattern نداره")
    
    if not has_handler and not has_startswith:
        status = "❌"
        issue.append("handler نداره")
    
    if in_pattern and has_handler:
        working.append((cb, menu_func, line_num, label))
        print(f"\n✅ {cb}")
        print(f"   دکمه: {label}")
        print(f"   در {menu_func} خط {line_num}")
    else:
        problems.append((cb, menu_func, line_num, label, issue))
        print(f"\n{status} {cb}")
        print(f"   دکمه: {label}")
        print(f"   در {menu_func} خط {line_num}")
        print(f"   مشکل: {' و '.join(issue)}")
        print(f"   در pattern: {'✅' if in_pattern else '❌'}")
        print(f"   handler داره: {'✅' if has_handler else '❌'}")

# ============================================================
# 5. خلاصه نهایی
# ============================================================
print("\n" + "="*80)
print("📊 خلاصه نهایی")
print("="*80)
print(f"""
✅ کار می‌کنن: {len(working)}
❌ مشکل دارن: {len(problems)}
""")

if problems:
    print("\n🚨 لیست دقیق دکمه‌های معیوب:")
    for cb, menu_func, line_num, label, issues in problems:
        print(f"\n   ❌ {cb}")
        print(f"      دکمه: {label}")
        print(f"      در: {menu_func} خط {line_num}")
        print(f"      مشکل: {' و '.join(issues)}")
