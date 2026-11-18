#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""جستجوی مستقیم callback های پنل سازنده با context کامل"""
import re
from datetime import datetime
from pathlib import Path

PROJECT = Path.home() / "groupbot"
MODULES = PROJECT / "modules"
REPORT = PROJECT / "CREATOR_CB_GREP.md"

TARGETS = [
    "owner_section_menu","owner_section_back",
    "s_fj_menu","s_fj_set","s_fj_toggle","s_fj_del",
    "s_op_botadmins","s_op_ba_list","s_op_sudo_stats","s_op_group_stats",
    "s_ba_perm","s_ba_toggle_fj","s_ba_del","s_ba_del_confirm",
    "s_panel_group","s_panel_group_back","sudo_panel_back",
]

FILES = ["start.py","pv_main.py","owner_set_group.py",
         "system_management.py","force_join.py",
         "remote_groups.py","reply.py","owner_panel_trigger.py"]

out = ["# جستجوی دقیق callback های پنل سازنده","", "تاریخ: "+str(datetime.now()), ""]

def ctx(lines, i, n=6):
    a=max(0,i-n); b=min(len(lines),i+n+1)
    return "\n".join(f"{a+k+1:5d} | {lines[a+k].rstrip()}" for k in range(b-a))

# ─── بخش ۱: هر callback کجا تعریف شده ───
out += ["## بخش ۱: هر callback کجا تعریف و کجا handler شده",""]
for target in TARGETS:
    out.append("### `"+target+"`")
    out.append("")
    found_any = False
    for fn in FILES:
        p = MODULES / fn
        if not p.exists(): continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        lines = text.splitlines()
        # هر خطی که شامل target باشه
        hits = [i for i,l in enumerate(lines) if target in l and not l.strip().startswith("#")]
        if not hits: continue
        found_any = True
        out.append(f"**{fn}** — {len(hits)} تطابق:")
        out.append("```")
        for h in hits[:8]:
            out.append(ctx(lines, h, 3))
            out.append("---")
        out.append("```")
        out.append("")
    if not found_any:
        out.append("❌ **هیچ جا پیدا نشد!**")
        out.append("")

# ─── بخش ۲: هندلر اصلی callback کجاست ───
out += ["","## بخش ۲: هندلر اصلی callback (pattern های بزرگ)",""]
for fn in FILES:
    p = MODULES / fn
    if not p.exists(): continue
    text = p.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    for i, l in enumerate(lines):
        if "CallbackQueryHandler" in l or "callback_query_handler" in l.lower() or "callback_handler" in l:
            out.append(f"**{fn}:{i+1}**")
            out.append("```")
            out.append(ctx(lines, i, 5))
            out.append("```")
            out.append("")

# ─── بخش ۳: هندلری که owner_section_back رو می‌گیره ───
out += ["","## بخش ۳: هندلری که owner_section_back رو پردازش می‌کنه",""]
for fn in FILES:
    p = MODULES / fn
    if not p.exists(): continue
    text = p.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    for i, l in enumerate(lines):
        if "owner_section_back" in l:
            out.append(f"**{fn}:{i+1}**")
            out.append("```")
            out.append(ctx(lines, i, 15))
            out.append("```")
            out.append("")

# ─── بخش ۴: ۵۰ خط آخر start.py ───
out += ["","## بخش ۴: خطوط آخر start.py (برای پیدا کردن pattern اصلی)",""]
p = MODULES / "start.py"
if p.exists():
    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    start = max(0, len(lines)-80)
    out.append("```")
    out.append("\n".join(f"{start+i+1:5d} | {l.rstrip()}" for i, l in enumerate(lines[start:])))
    out.append("```")

REPORT.write_text("\n".join(out), encoding="utf-8")
print("✅ گزارش: "+str(REPORT))
print("📊 "+str(REPORT.stat().st_size)+" بایت")
import subprocess
try:
    subprocess.run(["cp",str(REPORT),"/sdcard/Download/CREATOR_CB_GREP.md"], check=True)
    print("📱 /sdcard/Download/CREATOR_CB_GREP.md")
except Exception as e:
    print("⚠️  "+str(e))
