#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""تست جامع پنل سازنده — تحلیل + بررسی باگ + rollback خودکار"""
import sys, re, os, subprocess, py_compile, traceback
from datetime import datetime
from pathlib import Path

HOME = Path.home()
PROJECT = HOME / "groupbot"
MODULES = PROJECT / "modules"
BACKUPS = PROJECT / "backups"
REPORT = PROJECT / "CREATOR_PANEL_TEST.md"
TAG = datetime.now().strftime("%Y%m%d_%H%M%S")
BKP = BACKUPS / ("test_bak_" + TAG + ".tar.gz")

FILES = ["start.py","pv_main.py","owner_set_group.py",
         "system_management.py","force_join.py",
         "remote_groups.py","reply.py","owner_panel_trigger.py"]

# callback هایی که باید توی پنل سازنده پاسخ بدن
CREATOR_CBS = [
    "owner_section_menu","owner_section_back",
    "s_fj_menu","s_fj_set","s_fj_toggle","s_fj_del",
    "s_op_botadmins","s_op_ba_list","s_op_sudo_stats","s_op_group_stats",
    "s_ba_perm","s_ba_toggle_fj","s_ba_del","s_ba_del_confirm",
    "s_panel_group","s_panel_group_back","sudo_panel_back",
]

ERRORS = []
WARNINGS = []
INFO = []

def log(m): print(m, flush=True)
def add_error(m): ERRORS.append(m); log("❌ "+m)
def add_warn(m): WARNINGS.append(m); log("⚠️  "+m)
def add_ok(m): INFO.append("✅ "+m); log("✅ "+m)

def backup():
    BACKUPS.mkdir(exist_ok=True)
    r = subprocess.run(["tar","-czf",str(BKP),"-C",str(PROJECT),"modules"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        log("❌ بکاپ نشد: "+r.stderr); return False
    add_ok("بکاپ: "+str(BKP)); return True

def rollback():
    log("\n⚠️  rollback...")
    if not BKP.exists(): return
    subprocess.run(["tar","-xzf",str(BKP),"-C",str(PROJECT)],
                   capture_output=True, text=True)
    log("✅ برگشت از بکاپ")

# ─── PHASE 2: syntax ───
def phase_syntax():
    log("\n"+"="*50); log("PHASE 2: بررسی syntax"); log("="*50)
    for f in FILES:
        p = MODULES / f
        if not p.exists(): add_warn("نبود: "+f); continue
        try:
            py_compile.compile(str(p), doraise=True)
            add_ok("syntax OK: "+f)
        except py_compile.PyCompileError as e:
            add_error("syntax خطا در "+f+": "+str(e))

# ─── PHASE 3: پیدا کردن تمام callback ها و هندلرها ───
def phase_collect():
    log("\n"+"="*50); log("PHASE 3: جمع‌آوری callback و handler"); log("="*50)
    cbs = {}
    handlers = []
    all_text = ""
    for f in FILES:
        p = MODULES / f
        if not p.exists(): continue
        t = p.read_text(encoding="utf-8", errors="ignore")
        all_text += "\n# FILE: "+f+"\n"+t
        # هر callback_data=
        for m in re.finditer(r'callback_data\s*=\s*(?:f)?["\']([^"\']+)["\']', t):
            cbs.setdefault(m.group(1), []).append(f)
        # هر CallbackQueryHandler Pattern
        for m in re.finditer(r'CallbackQueryHandler\s*\(([^)]{0,400})\)', t, re.DOTALL):
            block = m.group(1)
            pm = re.search(r'(?:pattern\s*=\s*)?(?:r)?["\']([^"\']+)["\']', block)
            fn = re.search(r',\s*(\w+)\s*[,)]', block)
            if pm:
                handlers.append({"file":f, "pattern":pm.group(1),
                                 "func": fn.group(1) if fn else "?"})
    log("📊 "+str(len(cbs))+" callback یکتا، "+str(len(handlers))+" handler")
    return cbs, handlers, all_text

# ─── PHASE 4: بررسی پوشش callback ها ───
def phase_coverage(cbs, handlers):
    log("\n"+"="*50); log("PHASE 4: پوشش callback ها"); log("="*50)
    for cb in CREATOR_CBS:
        # callback تمیز برای تست
        clean = re.sub(r'\{[^}]+\}', '0', cb).strip(':')
        found = None
        for h in handlers:
            try:
                if re.search(h["pattern"], clean):
                    found = h; break
            except re.error:
                if h["pattern"] in clean:
                    found = h; break
        if found:
            add_ok(cb+" → "+found["func"]+" ("+found["file"]+")")
        else:
            add_error(cb+" → هیچ handler پیدا نشد!")
    # هندلرهای اضافی
    log("\n— هندلرهای پنل سازنده (از pattern های بالا):")
    for h in handlers:
        if any(k in h["pattern"] for k in ["owner_section","s_fj","s_ba","s_panel_group","s_op"]):
            log("  "+h["file"]+" → "+h["func"]+"   pattern="+h["pattern"][:80])

# ─── PHASE 5: بررسی دکمه‌های بازگشت ───
def phase_back(all_text):
    log("\n"+"="*50); log("PHASE 5: دکمه‌های بازگشت"); log("="*50)
    # برای هر back، پیدا کن داخل چه بلوکی از if/elif استفاده شده و چه منویی صدا زده
    for back in ["owner_section_back","s_panel_group_back","sudo_panel_back"]:
        idx = 0
        matches = 0
        # تمام جاهایی که این رشته چک شده
        for m in re.finditer(r'(==|==\s*)\s*["\']'+re.escape(back)+r'["\']', all_text):
            matches += 1
            start = m.start()
            window = all_text[start:start+600]
            # اولین تابع منو در این پنجره
            menu_match = re.search(r'reply_markup\s*=\s*(\w+)\s*\(', window)
            if menu_match:
                target = menu_match.group(1)
                if back == "owner_section_back" and target != "owner_section_menu":
                    add_error(back+" → "+target+" (باید owner_section_menu باشه!)")
                elif back == "owner_section_back" and target == "owner_section_menu":
                    add_ok(back+" → "+target)
                elif back == "s_panel_group_back":
                    add_ok(back+" → "+target+" (بررسی دستی لازم)")
                elif back == "sudo_panel_back":
                    add_ok(back+" → "+target)
            else:
                add_warn(back+" (مورد "+str(matches)+"): menu پیدا نشد در 600 کاراکتر بعدی")
        if matches == 0:
            add_error(back+" هیچ جا چک نشده!")

# ─── PHASE 6: بررسی باگ دقیق خط 6078 ───
def phase_line6078():
    log("\n"+"="*50); log("PHASE 6: بررسی خط 6078"); log("="*50)
    p = MODULES / "start.py"
    lines = p.read_text(encoding="utf-8").splitlines()
    if len(lines) < 6078:
        add_warn("start.py فقط "+str(len(lines))+" خط داره")
        return
    ctx = lines[6068:6088]
    log("محدوده 6068-6088:")
    for i, l in enumerate(ctx, start=6068):
        mark = " ← " if i == 6078 else "   "
        log(str(i)+mark+l.rstrip())
    line = lines[6077]
    if "owner_manage_menu" in line:
        add_error("خط 6078: owner_manage_menu — باید owner_section_menu باشه!")
    elif "owner_section_menu" in line:
        add_ok("خط 6078 درست: owner_section_menu")
    else:
        add_warn("خط 6078 حاوی owner_*_menu نیست")

# ─── PHASE 7: گزارش ───
def phase_report():
    log("\n"+"="*50); log("PHASE 7: گزارش"); log("="*50)
    L = ["# تست جامع پنل سازنده", "", "تاریخ: "+str(datetime.now()), ""]
    L += ["## ❌ خطاها ("+str(len(ERRORS))+")", ""] + ["- "+x for x in ERRORS] + [""]
    L += ["## ⚠️  هشدارها ("+str(len(WARNINGS))+")", ""] + ["- "+x for x in WARNINGS] + [""]
    L += ["## ✅ موفق‌ها ("+str(len(INFO))+")", ""] + ["- "+x for x in INFO] + [""]
    L += ["## نتیجه", "", ("❌ خطا دارد" if ERRORS else "✅ همه چیز OK")]
    REPORT.write_text("\n".join(L), encoding="utf-8")
    log("📄 "+str(REPORT))
    try:
        subprocess.run(["cp",str(REPORT),"/sdcard/Download/CREATOR_PANEL_TEST.md"], check=True)
        log("📱 /sdcard/Download/CREATOR_PANEL_TEST.md")
    except Exception as e:
        log("⚠️  کپی: "+str(e))

# ─── MAIN ───
def main():
    log("="*60); log("🔍 تست جامع پنل سازنده"); log("="*60)
    if not backup(): sys.exit(1)
    try:
        phase_syntax()
        cbs, handlers, all_text = phase_collect()
        phase_coverage(cbs, handlers)
        phase_back(all_text)
        phase_line6078()
        phase_report()
        log("\n"+"="*60)
        log("نتیجه: "+str(len(ERRORS))+" خطا، "+str(len(WARNINGS))+" هشدار")
        log("="*60)
        if ERRORS:
            log("\n⚠️  خطا وجود دارد — می‌خوای rollback بشه؟ (y/n)")
            # non-interactive: فعلاً بدون rollback خودکار تا تو تصمیم بگیری
            log("rollback دستی: tar -xzf "+str(BKP)+" -C "+str(PROJECT))
    except Exception as e:
        log("\n❌ خطای غیرمنتظره: "+str(e))
        traceback.print_exc()
        rollback()
        sys.exit(1)

if __name__ == "__main__": main()
