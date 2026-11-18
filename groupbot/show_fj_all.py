#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from pathlib import Path

print("="*70)
print("🔍 نمایش کامل همه بخش‌های FJ")
print("="*70)

MODULES = Path("modules")

# ═══ ۱. force_join.py کامل
print("\n" + "═"*70)
print("📄 فایل ۱: modules/force_join.py (کل)")
print("═"*70)
p = MODULES / "force_join.py"
if p.exists():
    for i, l in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        print(f"{i:4d} | {l}")

# ═══ ۲. fj_set در start.py
print("\n" + "═"*70)
print("📄 فایل ۲: fj_set در start.py")
print("═"*70)
p = MODULES / "start.py"
lines = p.read_text(encoding="utf-8").splitlines()
for i, l in enumerate(lines):
    if 'if action == "fj_set"' in l:
        print(f"\n📍 خط {i+1}")
        print("─"*60)
        for k in range(i, min(i+35, len(lines))):
            print(f"{k+1:5d} | {lines[k]}")
            if k > i+3 and lines[k].startswith('    if action') and 'fj_set' not in lines[k]:
                break

# ═══ ۳. FJ_WAIT در همه فایل‌ها
print("\n" + "═"*70)
print("📄 فایل ۳: FJ_WAIT در همه ماژول‌ها")
print("═"*70)
for f in sorted(MODULES.glob("*.py")):
    if ".bak" in f.name: continue
    try:
        text = f.read_text(encoding="utf-8", errors="ignore")
    except: continue
    for i, line in enumerate(text.splitlines()):
        if "FJ_WAIT" in line:
            print(f"📄 {f.name}:{i+1}  |  {line.strip()[:110]}")

# ═══ ۴. همه جاهایی که fj_link ذخیره/خوانده می‌شه
print("\n" + "═"*70)
print("📄 فایل ۴: fj_link در همه ماژول‌ها")
print("═"*70)
for f in sorted(MODULES.glob("*.py")):
    if ".bak" in f.name: continue
    try:
        text = f.read_text(encoding="utf-8", errors="ignore")
    except: continue
    for i, line in enumerate(text.splitlines()):
        if "fj_link" in line:
            print(f"📄 {f.name}:{i+1}  |  {line.strip()[:110]}")

# ═══ ۵. توابع مرتبط با force_join در database.py
print("\n" + "═"*70)
print("📄 فایل ۵: توابع force_join در database.py")
print("═"*70)
p = Path("database.py")
if p.exists():
    lines = p.read_text(encoding="utf-8").splitlines()
    for i, l in enumerate(lines):
        if "def " in l and ("force_join" in l.lower() or "fj_" in l.lower()):
            print(f"📍 {i+1}: {l.strip()}")
            # نمایش ۲۰ خط اول تابع
            for k in range(i, min(i+20, len(lines))):
                if k > i and lines[k].strip().startswith("def "):
                    break
                print(f"   {k+1:5d} | {lines[k]}")

# ═══ ۶. همه handler های force_join
print("\n" + "═"*70)
print("📄 فایل ۶: همه handler ها در force_join.py")
print("═"*70)
p = MODULES / "force_join.py"
if p.exists():
    lines = p.read_text(encoding="utf-8").splitlines()
    for i, l in enumerate(lines):
        if "add_handler" in l or "def register" in l or "async def" in l:
            print(f"{i+1:5d} | {l.strip()[:110]}")

print("\n" + "═"*70)
print("✅ پایان")
print("═"*70)
