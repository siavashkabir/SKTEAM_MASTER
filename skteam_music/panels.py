"""6 truly-distinct skin panels - COMPLETE"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

CB = {
    "pause": "pl:pause", "resume": "pl:resume",
    "next": "pl:next", "prev": "pl:prev", "stop": "pl:stop",
    "vu": "pl:vu", "vd": "pl:vd",
    "mute": "pl:mute", "unmute": "pl:unmute",
    "rep": "pl:rep", "shuffle": "pl:shuf",
    "queue": "pl:queue", "eq": "pl:eq",
    "close": "pl:close", "back": "pl:back",
    "dl128": "pl:dl128", "dl320": "pl:dl320",
    "seek_b30": "pl:seek_b30", "seek_b60": "pl:seek_b60",
    "seek_f30": "pl:seek_f30", "seek_f60": "pl:seek_f60",
    "spd_dn": "pl:spd_dn", "spd_up": "pl:spd_up",
    "spd_reset": "pl:spd_reset",
}

def _bar(pct, n=12, fill="━", empty="─", dot="●"):
    pct = max(0, min(100, int(pct)))
    f = int(n * pct / 100)
    if f >= n: return fill * n
    return fill * f + dot + empty * (n - f - 1)

def _t(sec):
    try: sec = int(sec or 0)
    except: sec = 0
    m, s = divmod(sec, 60); h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

def _icon(p):
    if p.get("paused"): return "⏸"
    if p.get("playing"): return "▶️"
    return "⏹"

def _b(t, cb): return InlineKeyboardButton(t, callback_data=cb)

def _rep_label(r):
    return {"one": "🔂 One", "all": "🔁 All"}.get(r, "🔁 Off")

def _shuf_label(s):
    return "🔀 روشن" if s else "🔀 خاموش"

def _short(s, n=30):
    """کوتاه کردن متن طولانی"""
    s = str(s or "—")
    return s if len(s) <= n else s[:n-1] + "…"


# ─── 1. MINIMAL ───
def skin_minimal(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    text = f"{_icon(p)} {t}\n{_t(pos)} {_bar(pct,12)} {_t(dur)}"
    kb = [
        [_b("⏸" if not p.get("paused") else "▶️", CB["pause"] if not p.get("paused") else CB["resume"]),
         _b("⏮", CB["prev"]), _b("⏭", CB["next"]), _b("⏹", CB["stop"])],
        [_b("🔉", CB["vd"]), _b("🔊", CB["vu"]),
         _b("🔇" if not p.get("muted") else "🔈", CB["mute"] if not p.get("muted") else CB["unmute"])],
        [_b(_rep_label(p.get("repeat","off")), CB["rep"]),
         _b("🔀", CB["shuffle"]), _b("🎚", CB["eq"]), _b("❌", CB["close"])],
    ]
    return text, kb

# ─── 2. CLASSIC ───
def skin_classic(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    vol = p.get("volume", 100)
    spd = p.get("speed", 1.0)
    text = (
        "╔══════════════════════╗\n"
        f"║  {_icon(p)} NOW PLAYING{' '*11}║\n"
        "╠══════════════════════╣\n"
        f"║  {t[:19]:<19}║\n"
        f"║  {_bar(pct,17)}║\n"
        f"║  {_t(pos)} / {_t(dur):<13}║\n"
        f"║  🔊 {vol}% · ⚡{spd}x · {_rep_label(p.get('repeat','off'))[:9]:<9}║\n"
        "╚══════════════════════╝"
    )
    kb = [
        [_b("⏸ مکث" if not p.get("paused") else "▶️ ادامه", CB["pause"] if not p.get("paused") else CB["resume"]),
         _b("⏮ قبلی", CB["prev"]), _b("⏭ بعدی", CB["next"]), _b("⏹ توقف", CB["stop"])],
        [_b("🔉 کم", CB["vd"]), _b("🔊 زیاد", CB["vu"]),
         _b("🔇" if not p.get("muted") else "🔈", CB["mute"] if not p.get("muted") else CB["unmute"])],
        [_b("⚡ کندتر", CB["spd_dn"]), _b(f"⚡ {spd}x", CB["spd_reset"]), _b("⚡ تندتر", CB["spd_up"])],
        [_b("⏪ ۶۰", CB["seek_b60"]), _b("◀ ۳۰", CB["seek_b30"]),
         _b("▶ ۳۰", CB["seek_f30"]), _b("⏩ ۶۰", CB["seek_f60"])],
        [_b(_rep_label(p.get("repeat","off")), CB["rep"]),
         _b(_shuf_label(p.get("shuffle", False)), CB["shuffle"]),
         _b("📋 صف", CB["queue"]), _b("🎚 EQ", CB["eq"])],
        [_b("📥 دریافت فایل", CB["dl128"]), _b("❌ بستن", CB["close"])],
    ]
    return text, kb

# ─── 3. NEON ───
def skin_neon(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    vol = p.get("volume", 100)
    text = (
        "🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪\n"
        f"🟪  🎧 {_icon(p)} NOW PLAYING  🟪\n"
        "🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪\n"
        f"🟩 {t}\n"
        f"🟨 {_bar(pct,15,'🟨','⬜','🟧')} {pct}%\n"
        f"🟥 ⏱ {_t(pos)} / {_t(dur)}\n"
        f"🟦 🔊{vol}% · ⚡{p.get('speed',1)}x · {_rep_label(p.get('repeat','off'))}"
    )
    kb = [
        [_b("⏸", CB["pause"] if not p.get("paused") else CB["resume"]),
         _b("⏮", CB["prev"]), _b("⏭", CB["next"]), _b("⏹", CB["stop"]), _b("🎚", CB["eq"])],
        [_b("🔊", CB["vu"]), _b("🔉", CB["vd"]),
         _b("🔇" if not p.get("muted") else "🔈", CB["mute"] if not p.get("muted") else CB["unmute"]),
         _b(_rep_label(p.get("repeat","off")), CB["rep"]), _b("🔀", CB["shuffle"])],
        [_b("⏪۶۰", CB["seek_b60"]), _b("◀۳۰", CB["seek_b30"]),
         _b("▶۳۰", CB["seek_f30"]), _b("⏩۶۰", CB["seek_f60"]), _b("❌", CB["close"])],
    ]
    return text, kb

# ─── 4. DARK PRO ───
def skin_darkpro(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    text = (
        "▛▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▜\n"
        f"▌  🎵 {_icon(p)} NOW PLAYING  ▐\n"
        "▙▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▟\n"
        "┏━ Title ━━━━━━━━━━┓\n"
        f"┃ {t[:17]:<17} ┃\n"
        "┗━━━━━━━━━━━━━━━━━━━┛\n"
        "┏━ Progress ━━━━━━━━┓\n"
        f"┃ {_bar(pct,17,'█','░','▓')} ┃\n"
        f"┃ {_t(pos)} / {_t(dur):<11} ┃\n"
        "┗━━━━━━━━━━━━━━━━━━━┛"
    )
    kb = [
        [_b("⏸", CB["pause"] if not p.get("paused") else CB["resume"]),
         _b("⏮", CB["prev"]), _b("⏭", CB["next"]), _b("⏹", CB["stop"]),
         _b("🔊", CB["vu"]), _b("🎚", CB["eq"])],
        [_b("🔉", CB["vd"]),
         _b("🔇" if not p.get("muted") else "🔈", CB["mute"] if not p.get("muted") else CB["unmute"]),
         _b(_rep_label(p.get("repeat","off")), CB["rep"]), _b("📋", CB["queue"])],
        [_b("⏪۶۰", CB["seek_b60"]), _b("◀۳۰", CB["seek_b30"]),
         _b("▶۳۰", CB["seek_f30"]), _b("⏩۶۰", CB["seek_f60"])],
        [_b("📥", CB["dl128"]), _b("❌", CB["close"])],
    ]
    return text, kb

# ─── 5. RETRO ───
def skin_retro(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    n = 16; f = int(n * pct / 100)
    bar = "█" * f + "░" * (n - f)
    text = (
        "╭─────────────────╮\n"
        "│ ♫ Track ♫        │\n"
        "╰─────────────────╯\n"
        f"\n  ► {t}\n"
        f"  ► [{bar}] {pct}%\n"
        f"  ► {_t(pos)} ........... {_t(dur)}\n"
    )
    kb = [
        [_b("⏸", CB["pause"] if not p.get("paused") else CB["resume"]),
         _b("⏮", CB["prev"]), _b("⏭", CB["next"]), _b("⏹", CB["stop"]),
         _b("🔊", CB["vu"]), _b("🎚", CB["eq"])],
        [_b("🔉", CB["vd"]),
         _b("🔇" if not p.get("muted") else "🔈", CB["mute"] if not p.get("muted") else CB["unmute"]),
         _b(_rep_label(p.get("repeat","off")), CB["rep"]), _b("📋", CB["queue"])],
        [_b("⏪۶۰", CB["seek_b60"]), _b("◀۳۰", CB["seek_b30"]),
         _b("▶۳۰", CB["seek_f30"]), _b("⏩۶۰", CB["seek_f60"])],
        [_b("❌", CB["close"])],
    ]
    return text, kb

# ─── 6. SAMPLE (فارسی کامل) ───
def skin_sample(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    vol = p.get("volume", 100)
    spd = p.get("speed", 1.0)
    src = p.get("source", "SoundCloud")
    req = p.get("requested_by_name", "—")
    status_txt = "در حال پخش" if (p.get("playing") and not p.get("paused")) else \
                 "متوقف موقت" if p.get("paused") else "متوقف"
    icon = _icon(p)

    text = (
        f"{icon} وضعیت : {status_txt}\n"
        f"🌐 منبع : {src}\n"
        f"🔊 میزان صدا : {vol}%\n"
        f"⚡ سرعت : {spd}x\n"
        f"👤 درخواست کننده : {req}\n"
        f"\n⏱ {_t(pos)}  {_bar(pct,11)}  {_t(dur)}\n"
        f"🎵 {t}"
    )
    kb = [
        [_b("⏹ توقف", CB["stop"]),
         _b("⏸ مکث" if not p.get("paused") else "▶️ ادامه",
            CB["pause"] if not p.get("paused") else CB["resume"])],
        [_b("⏮ قبلی", CB["prev"]), _b("⏭ بعدی", CB["next"])],
        [_b("⏪ ۶۰", CB["seek_b60"]), _b("◀ ۳۰", CB["seek_b30"]),
         _b("▶ ۳۰", CB["seek_f30"]), _b("⏩ ۶۰", CB["seek_f60"])],
        [_b("🔉 کم", CB["vd"]), _b("🔊 زیاد", CB["vu"])],
        [_b("🔇 بی‌صدا" if not p.get("muted") else "🔈 باصدا",
            CB["mute"] if not p.get("muted") else CB["unmute"])],
        [_b("⚡ کندتر", CB["spd_dn"]), _b(f"⚡ {spd}x", CB["spd_reset"]), _b("⚡ تندتر", CB["spd_up"])],
        [_b(_rep_label(p.get("repeat","off")), CB["rep"]),
         _b(_shuf_label(p.get("shuffle", False)), CB["shuffle"]),
         _b("🎛 اکولایزر", CB["eq"])],
        [_b("📋 صف پخش", CB["queue"])],
        [_b("📥 دریافت ۱۲۸K", CB["dl128"]), _b("📥 دریافت ۳۲۰K", CB["dl320"])],
        [_b("🔴 بستن پنل", CB["close"])],
    ]
    return text, kb

# ─── dispatch ───


# ──────────── 8. COMPACT (فقط ۱ ردیف) ────────────
def skin_compact(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    icon = _icon(p)
    text = (
        f"{icon} **{t[:30]}**\n"
        f"`{_t(pos)}` {_bar(pct,10)} `{_t(dur)}`"
    )
    kb = [
        [_b("⏮", CB["prev"]), _b("⏯" if not p.get("paused") else "▶️",
            CB["pause"] if not p.get("paused") else CB["resume"]),
         _b("⏭", CB["next"]), _b("⏹", CB["stop"]),
         _b("🔉", CB["vd"]), _b("🔊", CB["vu"]),
         _b("🎚", CB["eq"]), _b("❌", CB["close"])],
    ]
    return text, kb


# ──────────── 9. PRO (حرفه‌ای با همه دکمه‌ها) ────────────
def skin_pro(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    vol = p.get("volume", 100)
    spd = p.get("speed", 1.0)
    req = p.get("requested_by_name", "—")
    icon = _icon(p)
    text = (
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"  🎧 SK.TEAM PRO PLAYER  {icon}\n"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"📀 **{t[:35]}**\n"
        f"👤 {req}\n"
        "▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️\n"
        f"⏱  {_t(pos)}  •  {_t(dur)}\n"
        f"📊 {_bar(pct,16,'█','░','▓')} {pct}%\n"
        f"🔊 {vol}%    ⚡ {spd}x\n"
        f"🔁 {p.get('repeat','off').upper()}    🔀 {'ON' if p.get('shuffle') else 'OFF'}\n"
        "▪️▪️▪️▪️▪️▪️▪️▪️▪️▪️"
    )
    kb = [
        [_b("⏮ قبلی", CB["prev"]),
         _b("⏯ پخش/مکث" if not p.get("paused") else "▶️ پخش",
            CB["pause"] if not p.get("paused") else CB["resume"]),
         _b("⏭ بعدی", CB["next"])],
        [_b("⏪ ۶۰", CB["seek_b60"]), _b("◀ ۳۰", CB["seek_b30"]),
         _b("⏹ توقف", CB["stop"]),
         _b("▶ ۳۰", CB["seek_f30"]), _b("⏩ ۶۰", CB["seek_f60"])],
        [_b("🔉 -", CB["vd"]), _b(f"🔊 {vol}%", CB["vu"]),
         _b("🔇" if not p.get("muted") else "🔈",
            CB["mute"] if not p.get("muted") else CB["unmute"]),
         _b("⚡ کند", CB["spd_dn"]), _b("⚡ تند", CB["spd_up"])],
        [_b("🎚 EQ", CB["eq"]), _b("📋 صف", CB["queue"]),
         _b(f"🔁 {p.get('repeat','off')}", CB["rep"]),
         _b("🔀", CB["shuffle"])],
        [_b("📥 دانلود", CB["dl128"]), _b("❌ بستن", CB["close"])],
    ]
    return text, kb


# ──────────── 10. NEON2 (نئون تیره) ────────────
def skin_neon2(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    vol = p.get("volume", 100)
    icon = _icon(p)
    text = (
        "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓\n"
        f"▓  ⚡ {icon} NOW PLAYING  ⚡  ▓\n"
        "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓\n"
        f"░ {t[:30]}\n"
        f"░ ▰{_bar(pct,16,'▰','▱','▰')}▰\n"
        f"░ ▸ {_t(pos)} ⟶ {_t(dur)}\n"
        f"░ ♫ vol {vol}%  ♫ spd {p.get('speed',1.0)}x"
    )
    kb = [
        [_b("⚡", CB["prev"]), _b("⏸" if not p.get("paused") else "▶️",
            CB["pause"] if not p.get("paused") else CB["resume"]),
         _b("⚡", CB["next"]), _b("▓", CB["stop"])],
        [_b("◄◄", CB["seek_b60"]), _b("◄", CB["seek_b30"]),
         _b("►", CB["seek_f30"]), _b("►►", CB["seek_f60"])],
        [_b("▼", CB["vd"]), _b(f"♫{vol}", CB["vu"]),
         _b("◯", CB["mute"] if not p.get("muted") else CB["unmute"]),
         _b("⚙", CB["eq"])],
        [_b("⏹ OFF", CB["close"])],
    ]
    return text, kb


# ──────────── 11. GLASS (شیشه‌ای، پر زرق و برق) ────────────
def skin_glass(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    vol = p.get("volume", 100)
    spd = p.get("speed", 1.0)
    req = p.get("requested_by_name", "—")
    icon = _icon(p)
    text = (
        "╭━━━━━━━━━━━━━━━━━━━━━╮\n"
        f"┃ ✨  SK.TEAM {icon}  ✨ ┃\n"
        "┣━━━━━━━━━━━━━━━━━━━━━┫\n"
        f"┃ 🎵 {t[:22]:<22}┃\n"
        f"┃ 👤 {req[:22]:<22}┃\n"
        "┣━━━━━━━━━━━━━━━━━━━━━┫\n"
        f"┃ ⏱ {_t(pos):<9} ⇒ {_t(dur):<9}┃\n"
        f"┃ {_bar(pct,20,'▰','▱','▰')}┃\n"
        f"┃ 💎 {pct}%  🔊 {vol}%  ⚡ {spd}x  ┃\n"
        "╰━━━━━━━━━━━━━━━━━━━━━╯"
    )
    kb = [
        [_b("◀ ۶۰s", CB["seek_b60"]), _b("⏮", CB["prev"]),
         _b("⏯" if not p.get("paused") else "▶️",
            CB["pause"] if not p.get("paused") else CB["resume"]),
         _b("⏭", CB["next"]), _b("۶۰s ▶", CB["seek_f60"])],
        [_b("🔊 −", CB["vd"]), _b("⏹", CB["stop"]),
         _b("🔊 +", CB["vu"]), _b("🔇", CB["mute"] if not p.get("muted") else CB["unmute"])],
        [_b("🎚 EQ", CB["eq"]), _b("📋 صف", CB["queue"]),
         _b(f"🔁", CB["rep"]), _b("🔀", CB["shuffle"])],
        [_b("📥 دریافت فایل", CB["dl128"]), _b("❌", CB["close"])],
    ]
    return text, kb


# ──────────── 12. DJ (حال دی‌جی) ────────────
def skin_dj(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    vol = p.get("volume", 100)
    spd = p.get("speed", 1.0)
    icon = _icon(p)
    text = (
        "🎧 🎶 🎵 🎼 🎤 🎹 🥁 🎺 🎷\n"
        f"     {icon}  DJ MODE ON  {icon}\n"
        "🎧 🎶 🎵 🎼 🎤 🎹 🥁 🎺 🎷\n"
        f"\n 🎵 **{t[:30]}**\n"
        f" ▰▰{_bar(pct,14,'▰','▱','▰')}▰▰\n"
        f" ⏱ {_t(pos)} / {_t(dur)}\n"
        f" 🔊 {vol}%  ⚡ {spd}x"
    )
    kb = [
        [_b("🎤", CB["vd"]), _b("🎧", CB["vu"]),
         _b("🔇" if not p.get("muted") else "🔊",
            CB["mute"] if not p.get("muted") else CB["unmute"]),
         _b("🎚 EQ", CB["eq"])],
        [_b("🔂 Rep", CB["rep"]), _b("🔀 Mix", CB["shuffle"]),
         _b("📋 List", CB["queue"])],
        [_b("⏪", CB["seek_b60"]), _b("⏮", CB["prev"]),
         _b("⏯" if not p.get("paused") else "▶️",
            CB["pause"] if not p.get("paused") else CB["resume"]),
         _b("⏭", CB["next"]), _b("⏩", CB["seek_f60"])],
        [_b("⚡ Slow", CB["spd_dn"]), _b("⏹ Stop", CB["stop"]), _b("⚡ Fast", CB["spd_up"])],
        [_b("📥 DL", CB["dl128"]), _b("❌", CB["close"])],
    ]
    return text, kb


# ──────────── 13. MONO (تک‌رنگ ساده) ────────────
def skin_mono(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    icon = _icon(p)
    text = (
        "┌───────────────────┐\n"
        f"│ {icon} PLAYING        │\n"
        "├───────────────────┤\n"
        f"│ {t[:17]:<17} │\n"
        f"│ [{_bar(pct,15,'=',' ','>')}] │\n"
        f"│ {_t(pos):>7} / {_t(dur):<7} │\n"
        "└───────────────────┘"
    )
    kb = [
        [_b("<<", CB["prev"]), _b("<>", CB["pause"] if not p.get("paused") else CB["resume"]),
         _b(">>", CB["next"]), _b("[]", CB["stop"])],
        [_b("-V", CB["vd"]), _b("V+", CB["vu"]), _b("M", CB["mute"] if not p.get("muted") else CB["unmute"])],
        [_b("EQ", CB["eq"]), _b("Q", CB["queue"]), _b("X", CB["close"])],
    ]
    return text, kb




# ═══════════════════════════════════════════════
# اسکین‌های خفن
# ═══════════════════════════════════════════════

# ──────────── 14. CYBERPUNK ────────────
def skin_cyber(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    vol = p.get("volume", 100); spd = p.get("speed", 1.0)
    req = p.get("requested_by_name", "—")
    icon = _icon(p)
    filled = int(pct * 20 / 100)
    bar = "▰" * filled + "▱" * (20 - filled)
    text = (
        "⚡⟪▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓⟫⚡\n"
        f"  🎮  S K . T E A M  {icon}\n"
        "⚡⟪▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓⟫⚡\n"
        f"⌬ **{t[:32]}**\n"
        f"⌬ 🎤 {req}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"▸ ▓{bar}▓ ◂\n"
        f"▸ ⏱ {_t(pos)} · {_t(dur)} · {pct}%\n"
        f"▸ 🔊 {vol}% ⚡ {spd}x 🔁 {p.get('repeat','off')}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━"
    )
    kb = [
        [_b("►►►", CB["seek_f60"]), _b("►►", CB["seek_f30"]),
         _b("║◄◄", CB["prev"]),
         _b("▶║" if not p.get("paused") else "▶▶",
            CB["pause"] if not p.get("paused") else CB["resume"]),
         _b("►►║", CB["next"]),
         _b("◄◄", CB["seek_b30"]), _b("◄◄◄", CB["seek_b60"])],
        [_b("▽vol", CB["vd"]), _b(f"▲{vol}", CB["vu"]),
         _b("⚡×" if not p.get("muted") else "⚡✓",
            CB["mute"] if not p.get("muted") else CB["unmute"]),
         _b("◄◄spd", CB["spd_dn"]), _b("spd►►", CB["spd_up"])],
        [_b("⌘EQ", CB["eq"]), _b("≡QUE", CB["queue"]),
         _b("∞REP", CB["rep"]), _b("⇄SHF", CB["shuffle"])],
        [_b("◆DL", CB["dl128"]), _b("⬛HALT", CB["stop"]), _b("✕", CB["close"])],
    ]
    return text, kb
# ──────────── 15. WAVE ────────────
def skin_wave(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    vol = p.get("volume", 100)
    icon = _icon(p)
    wave = "▁▂▃▄▅▆▇█▇▆▅▄▃▂▁▂▃▄▅▆▇█▇▆▅▄▃"
    text = (
        f"{icon} NOW PLAYING\n"
        f"⋆｡°✩ ──── ⋆｡°✩ ──── ⋆｡°✩\n"
        f"**{t[:35]}**\n"
        f"⋆｡°✩ ──── ⋆｡°✩ ──── ⋆｡°✩\n"
        f"       {wave}\n"
        f"◁━ {_t(pos)}  ●  {_t(dur)} ━▷\n"
        f"                   {pct}%\n"
        f"🔊 {vol}%"
    )
    kb = [
        [_b("⇤⇤≪", CB["seek_b60"]), _b("⇤≪", CB["seek_b30"]),
         _b("«◁", CB["prev"]),
         _b("◉" if not p.get("paused") else "◎",
            CB["pause"] if not p.get("paused") else CB["resume"]),
         _b("▷»", CB["next"]),
         _b("≫⇥", CB["seek_f30"]), _b("≫≫⇥", CB["seek_f60"])],
        [_b("▁▼", CB["vd"]), _b("▲▁", CB["vu"]),
         _b("◌" if not p.get("muted") else "◍",
            CB["mute"] if not p.get("muted") else CB["unmute"]),
         _b("⤺", CB["spd_dn"]), _b("⤻", CB["spd_up"])],
        [_b("∿ EQ", CB["eq"]), _b("☰ صف", CB["queue"]),
         _b("⟲", CB["rep"]), _b("⇆", CB["shuffle"]), _b("⏻", CB["stop"])],
        [_b("⤓ دریافت", CB["dl128"]), _b("✖", CB["close"])],
    ]
    return text, kb
# ──────────── 16. VINYL ────────────
def skin_vinyl(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    vol = p.get("volume", 100)
    req = p.get("requested_by_name", "—")
    icon = _icon(p)
    rot = pos % 4
    discs = ["◐", "◓", "◑", "◒"]
    disc = discs[rot]
    text = (
        f"╔══════════════════════════╗\n"
        f"║    💿 {disc}  RECORD PLAYER  ║\n"
        f"╠══════════════════════════╣\n"
        f"║ 🎵 {t[:20]:<20} ║\n"
        f"║ 🎤 {req[:20]:<20} ║\n"
        f"╠══════════════════════════╣\n"
        f"║  ●{_bar(pct,20,'─','─','●')}●  ║\n"
        f"║  ◀ {_t(pos):>7} · {_t(dur):<7} ▶  ║\n"
        f"║  🔊 vol {vol}%   {icon}            ║\n"
        f"╚══════════════════════════╝"
    )
    kb = [
        [_b("⏮⏮◄◄", CB["prev"]), _b("◄◄◄", CB["seek_b60"]),
         _b("◄◄", CB["seek_b30"]),
         _b("❚❚" if not p.get("paused") else "▶",
            CB["pause"] if not p.get("paused") else CB["resume"]),
         _b("►►", CB["seek_f30"]),
         _b("►►►", CB["seek_f60"]), _b("►►⏭⏭", CB["next"])],
        [_b("♫−", CB["vd"]), _b("♫+", CB["vu"]),
         _b("𝄽" if not p.get("muted") else "♬",
            CB["mute"] if not p.get("muted") else CB["unmute"]),
         _b("⏏ ⏹", CB["stop"])],
        [_b("♯ EQ", CB["eq"]), _b("♭ صف", CB["queue"]),
         _b("𝄉", CB["rep"]), _b("𝄊", CB["shuffle"]),
         _b("✕", CB["close"])],
    ]
    return text, kb
# ──────────── 17. CRYSTAL ────────────
def skin_crystal(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    vol = p.get("volume", 100)
    req = p.get("requested_by_name", "—")
    icon = _icon(p)
    text = (
        "   ╱╲ ╱╲ ╱╲ ╱╲ ╱╲ ╱╲\n"
        "  ╱💎╲╱💎╲╱💎╲╱💎╲╱💎╲\n"
        "  ╲ ╱╲ ╱╲ ╱╲ ╱╲ ╱╲ ╱\n"
        f"  ◆ {icon} DIAMOND PLAYER ◆\n"
        "  ╲ ╱╲ ╱╲ ╱╲ ╱╲ ╱╲ ╱\n"
        f"  ╔═ 🎵 {t[:22]:<22}═╗\n"
        f"  ║  ✦ {req[:24]:<24} ✦ ║\n"
        f"  ╠═══{_bar(pct,18,'◆','◇','◆')}═══╣\n"
        f"  ║  ⏱ {_t(pos):<8} · {_t(dur):<8} ║\n"
        f"  ║  💎 {pct}%  🔊 {vol}% ║\n"
        "  ╚════════════════════════╝"
    )
    kb = [
        [_b("✧⏮✦", CB["prev"]),
         _b("❖⟪۶۰", CB["seek_b60"]), _b("❖⟪۳۰", CB["seek_b30"]),
         _b("✦❚❚" if not p.get("paused") else "✦▶",
            CB["pause"] if not p.get("paused") else CB["resume"]),
         _b("۳۰⟫❖", CB["seek_f30"]), _b("۶۰⟫❖", CB["seek_f60"]),
         _b("✦⏭✧", CB["next"])],
        [_b("◇vol−", CB["vd"]), _b("vol+◆", CB["vu"]),
         _b("◈" if not p.get("muted") else "✧",
            CB["mute"] if not p.get("muted") else CB["unmute"]),
         _b("⟡EQ", CB["eq"]), _b("⊞صف", CB["queue"])],
        [_b("✦💎دریافت فایل", CB["dl128"]),
         _b("✧توقف✦", CB["stop"]),
         _b("✕", CB["close"])],
    ]
    return text, kb
# ──────────── 18. FIRE ────────────
def skin_fire(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    vol = p.get("volume", 100)
    req = p.get("requested_by_name", "—")
    icon = _icon(p)
    text = (
        "🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥\n"
        f"  🔥 **SK.TEAM FIRE** 🔥\n"
        "🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥\n"
        f"🍖 *{t[:32]}*\n"
        f"👤 {req}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔴{_bar(pct,20,'█','░','🔴')}🔴\n"
        f"⚡ {_t(pos)} / {_t(dur)} / {pct}%\n"
        f"🔊 {vol}%  {icon}\n"
        f"━━━━━━━━━━━━━━━━━━━━━"
    )
    kb = [
        [_b("💥⏮🔥", CB["prev"]),
         _b("🔥۶۰◀", CB["seek_b60"]), _b("🔥۳۰◀", CB["seek_b30"]),
         _b("💥❚❚" if not p.get("paused") else "💥▶",
            CB["pause"] if not p.get("paused") else CB["resume"]),
         _b("▶۳۰🔥", CB["seek_f30"]), _b("▶۶۰🔥", CB["seek_f60"]),
         _b("🔥⏭💥", CB["next"])],
        [_b("🔻vol", CB["vd"]), _b("vol🔺", CB["vu"]),
         _b("💨" if not p.get("muted") else "🔊",
            CB["mute"] if not p.get("muted") else CB["unmute"]),
         _b("🌡EQ", CB["eq"]), _b("🪵صف", CB["queue"])],
        [_b("⚡تند", CB["spd_up"]), _b("🐢کند", CB["spd_dn"]),
         _b("♻️", CB["rep"]), _b("🔀", CB["shuffle"])],
        [_b("💾🔥دریافت", CB["dl128"]),
         _b("🧯خاموش", CB["stop"]),
         _b("❌", CB["close"])],
    ]
    return text, kb
# ──────────── 19. SPACE ────────────
def skin_space(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    vol = p.get("volume", 100)
    req = p.get("requested_by_name", "—")
    icon = _icon(p)
    text = (
        "🌌 ✦ ✧ ★ ✧ ✦ ★ ✧ ✦ 🌌\n"
        "  🛰  SPACE MUSIC STATION\n"
        "🌌 ✦ ✧ ★ ✧ ✦ ★ ✧ ✦ 🌌\n"
        f"☄ **{t[:30]}**\n"
        f"👨‍🚀 {req}\n"
        "┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n"
        f"🚀 {_bar(pct,18,'▰','▱','🌠')} 🛸\n"
        f"⏱ {_t(pos)} → {_t(dur)} ({pct}%)\n"
        f"🔊 {vol}% · {icon}\n"
        "┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈"
    )
    kb = [
        [_b("☄⟪⏮", CB["prev"]),
         _b("🌠⟪۶۰", CB["seek_b60"]), _b("🌠⟪۳۰", CB["seek_b30"]),
         _b("🛸❚❚" if not p.get("paused") else "🛸▶",
            CB["pause"] if not p.get("paused") else CB["resume"]),
         _b("۳۰⟫🌠", CB["seek_f30"]), _b("۶۰⟫🌠", CB["seek_f60"]),
         _b("⏭⟫☄", CB["next"])],
        [_b("🪐vol−", CB["vd"]), _b("vol+🪐", CB["vu"]),
         _b("🌑" if not p.get("muted") else "🌟",
            CB["mute"] if not p.get("muted") else CB["unmute"]),
         _b("⚛EQ", CB["eq"]), _b("📡صف", CB["queue"])],
        [_b("⏪کند", CB["spd_dn"]), _b("⚡تند", CB["spd_up"]),
         _b("🔄Loop", CB["rep"]), _b("✨Shuf", CB["shuffle"])],
        [_b("🌌دریافت", CB["dl128"]),
         _b("💫ایست", CB["stop"]),
         _b("☄خروج", CB["close"])],
    ]
    return text, kb
# ──────────── 20. CINEMA (سینما) ────────────
def skin_cinema(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    vol = p.get("volume", 100)
    req = p.get("requested_by_name", "—")
    icon = _icon(p)
    filled = int(pct * 20 / 100)
    bar = "▰" * filled + "▱" * (20 - filled)
    text = (
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃ 🎬  C I N E M A  4 K  🎬 ┃\n"
        "┣━━━━━━━━━━━━━━━━━━━━━━━━━┫\n"
        "┃ ▓▒░ FILM NO. 2026-1011 ░▒▓┃\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
        f"\n           🎥  {icon}\n"
        f"\n  ★ **{t[:30]}**\n"
        f"\n  🎬 کارگردان: {req}\n"
        f"\n┌──────── PROGRESS ────────┐\n"
        f"│ {bar} │\n"
        f"│  🎞 {_t(pos)}  ·  📽 {_t(dur)} │\n"
        f"└──────────────────────────┘\n"
        f"\n  🔊 {vol}%  ·  ⏱ {pct}%\n"
    )
    kb = [
        [_b("🎞⏮", CB["prev"]),
         _b("◄◄ ۶۰s", CB["seek_b60"]), _b("◄ ۳۰s", CB["seek_b30"]),
         _b("⏸" if not p.get("paused") else "▶️",
            CB["pause"] if not p.get("paused") else CB["resume"]),
         _b("۳۰s ►", CB["seek_f30"]), _b("۶۰s ►►", CB["seek_f60"]),
         _b("⏭🎞", CB["next"])],
        [_b("🔈−", CB["vd"]), _b("+🔊", CB["vu"]),
         _b("🎙" if not p.get("muted") else "🎤",
            CB["mute"] if not p.get("muted") else CB["unmute"]),
         _b("🎚 EQ", CB["eq"]), _b("🎬 صحنه", CB["queue"])],
        [_b("⚡ 2x", CB["spd_up"]), _b("🐢 0.5x", CB["spd_dn"]),
         _b("🔁 Scene", CB["rep"]), _b("🎲 Random", CB["shuffle"])],
        [_b("📥 دانلود فیلم", CB["dl128"]),
         _b("⏹ END", CB["stop"]),
         _b("🚪 EXIT", CB["close"])],
    ]
    return text, kb
# ──────────── 21. RADIO (رادیو قدیمی) ────────────
def skin_radio(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    vol = p.get("volume", 100)
    icon = _icon(p)
    freq = 88.0 + (pct * 20 / 100)
    dial_pos = int(pct * 30 / 100)
    dial = " " * dial_pos + "▲" + " " * (30 - dial_pos)
    text = (
        "╔══════════════════════════════╗\n"
        "║  📻 SK.TEAM FM RADIO 2026   ║\n"
        "╠══════════════════════════════╣\n"
        "║ FM: 88  92  96  100 104 108 ║\n"
        f"║ {dial} ║\n"
        f"║  ▼ {freq:.1f} MHz              ║\n"
        "╠══════════════════════════════╣\n"
        f"║ ♫ NOW: {t[:22]:<22}║\n"
        f"║ 🔊 VOL: {vol:>3}%  ⏱ {_t(pos):>6}  ║\n"
        f"║ {icon} SIGNAL: ▮▮▮▮▮▮▮▯▯▯  ║\n"
        "╚══════════════════════════════╝"
    )
    kb = [
        [_b("◄◄◄ kHz", CB["seek_b60"]), _b("◄◄ kHz", CB["seek_b30"]),
         _b("⏮ FM", CB["prev"]),
         _b("⏸" if not p.get("paused") else "▶️",
            CB["pause"] if not p.get("paused") else CB["resume"]),
         _b("FM ⏭", CB["next"]),
         _b("kHz ►►", CB["seek_f30"]), _b("kHz ►►►", CB["seek_f60"])],
        [_b("vol−🔉", CB["vd"]), _b("🔊+vol", CB["vu"]),
         _b("🔇", CB["mute"] if not p.get("muted") else CB["unmute"]),
         _b("🎛 تیونر", CB["eq"]), _b("📻 موج", CB["queue"])],
        [_b("⏻ خاموش", CB["stop"]),
         _b("🎁 پکیج", CB["dl128"]),
         _b("🔌 قطع", CB["close"])],
    ]
    return text, kb
# ──────────── 22. HACKER (هکر/ماتریکس) ────────────
def skin_hacker(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    vol = p.get("volume", 100)
    req = p.get("requested_by_name", "—")
    icon = _icon(p)
    binary = "".join(["1" if (i * pos) % 3 else "0" for i in range(32)])
    filled = int(pct * 20 / 100)
    bar = "█" * filled + "░" * (20 - filled)
    text = (
        "┌─[ ROOT@SKTEAM ]─[ ~/music ]──┐\n"
        f"│ {binary[:30]} │\n"
        "└───────────────────────────────┘\n"
        f"$ cat /now_playing\n"
        f"  ├─ title: **{t[:32]}**\n"
        f"  ├─ user : {req}\n"
        f"  ├─ state: {icon}\n"
        f"  └─ vol  : {vol}%\n"
        f"\n$ progress --watch\n"
        f"  [{bar}] {pct}%\n"
        f"  {_t(pos)}/{_t(dur)}  PID:{pos % 9999:04d}\n"
        f"\n$ _█"
    )
    kb = [
        [_b("<<<60", CB["seek_b60"]), _b("<30", CB["seek_b30"]),
         _b("[/\\]", CB["prev"]),
         _b("[||]" if not p.get("paused") else "[>]",
            CB["pause"] if not p.get("paused") else CB["resume"]),
         _b("[\\/]", CB["next"]),
         _b("[30>]", CB["seek_f30"]), _b("[60>>>]", CB["seek_f60"])],
        [_b("[sudo vol-]", CB["vd"]), _b("[sudo vol+]", CB["vu"]),
         _b("[sudo mute]", CB["mute"] if not p.get("muted") else CB["unmute"]),
         _b("[tune -eq]", CB["eq"]), _b("[sudo ls queue]", CB["queue"])],
        [_b("[speed 0.5]", CB["spd_dn"]), _b("[speed 2.0]", CB["spd_up"]),
         _b("[loop]", CB["rep"]), _b("[rand]", CB["shuffle"])],
        [_b("[wget audio]", CB["dl128"]),
         _b("[sudo kill]", CB["stop"]),
         _b("[exit --force]", CB["close"])],
    ]
    return text, kb
# ──────────── 23. CONCERT (کنسرت/صحنه) ────────────
def skin_concert(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    vol = p.get("volume", 100)
    req = p.get("requested_by_name", "—")
    icon = _icon(p)
    spot_pos = int(pct * 30 / 100) if pct < 100 else 30
    spot = " " * spot_pos + "★" + " " * (30 - spot_pos)
    crowd = "🧑‍🤝‍🧑👨‍👩‍👧🧑‍🤝‍🧑👨‍👩‍👧🧑‍🤝‍🧑👨‍👩‍👧"
    filled = int(pct * 20 / 100)
    bar = "◉" * filled + "○" * (20 - filled)
    text = (
        "╔══════════════════════════════════╗\n"
        "║  🎤  LIVE  CONCERT  STAGE  2026  ║\n"
        "╠══════════════════════════════════╣\n"
        f"║  {spot[:32]:<32}║\n"
        "║       ╔═════════════╗           ║\n"
        f"║       ║  {icon}  {icon}  {icon}   ║           ║\n"
        "║       ║  ON STAGE  ║           ║\n"
        "║       ╚═════════════╝           ║\n"
        f"║  {crowd[:33]:<33}║\n"
        "╠══════════════════════════════════╣\n"
        f"║ 🎵 {t[:30]:<30}║\n"
        f"║ 🎤 {req[:30]:<30}║\n"
        f"║ {bar} ║\n"
        f"║ ⏱ {_t(pos):<5} · {_t(dur):<5} · vol {vol}% ║\n"
        "╚══════════════════════════════════╝"
    )
    kb = [
        [_b("🎸⏮", CB["prev"]),
         _b("🎺۶۰◀", CB["seek_b60"]), _b("🎺۳۰◀", CB["seek_b30"]),
         _b("🎤❚❚" if not p.get("paused") else "🎤▶",
            CB["pause"] if not p.get("paused") else CB["resume"]),
         _b("▶۳۰🎹", CB["seek_f30"]), _b("▶۶۰🎹", CB["seek_f60"]),
         _b("⏭🎸", CB["next"])],
        [_b("🥁−", CB["vd"]), _b("+🥁", CB["vu"]),
         _b("🎷" if not p.get("muted") else "🎺",
            CB["mute"] if not p.get("muted") else CB["unmute"]),
         _b("⚡🎙", CB["spd_up"]), _b("🐢🎙", CB["spd_dn"])],
        [_b("🎼 EQ", CB["eq"]), _b("📋 Setlist", CB["queue"]),
         _b("🔁 Encore", CB["rep"]), _b("🎲 Shuffle", CB["shuffle"])],
        [_b("🎁 Merch", CB["dl128"]),
         _b("🎬 Final", CB["stop"]),
         _b("🚪 Leave", CB["close"])],
    ]
    return text, kb
# ──────────── 24. CASSETTE (کاست) ────────────
def skin_cassette(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    vol = p.get("volume", 100)
    req = p.get("requested_by_name", "—")
    icon = _icon(p)
    rot = pos % 4
    reels = ["◐", "◓", "◑", "◒"]
    reel = reels[rot]
    filled = int(pct * 22 / 100)
    bar = "▓" * filled + "░" * (22 - filled)
    text = (
        "╭──────────────────────────────────╮\n"
        "│  ⏮ ●  💿 SK.TEAM TAPE  ● ⏭   │\n"
        "├──────────────────────────────────┤\n"
        "│                                  │\n"
        f"│     {reel}═══════○═══════{reel}    │\n"
        "│       ╔════════════════╗         │\n"
        f"│       ║  {icon}  {t[:10]:<10}║         │\n"
        "│       ╚════════════════╝         │\n"
        "│                                  │\n"
        "├──────────────────────────────────┤\n"
        f"│  [ {bar} ]  {pct}%  │\n"
        f"│  ▸⏱ {_t(pos)}      ⏸ {_t(dur)}  🔊 {vol}% │\n"
        f"│  🎧 {req[:25]:<25} │\n"
        "╰──────────────────────────────────╯"
    )
    kb = [
        [_b("⏮◄◄◄", CB["prev"]),
         _b("◄◄◄", CB["seek_b60"]), _b("◄◄", CB["seek_b30"]),
         _b("❚❚" if not p.get("paused") else "▶",
            CB["pause"] if not p.get("paused") else CB["resume"]),
         _b("►►", CB["seek_f30"]), _b("►►►", CB["seek_f60"]),
         _b("►►►⏭", CB["next"])],
        [_b("◁vol", CB["vd"]), _b("vol▷", CB["vu"]),
         _b("▢" if not p.get("muted") else "▣",
            CB["mute"] if not p.get("muted") else CB["unmute"]),
         _b("⚙ EQ", CB["eq"]), _b("▤ صف", CB["queue"])],
        [_b("⏏️ EJECT", CB["stop"]),
         _b("📼 دریافت", CB["dl128"]),
         _b("❌", CB["close"])],
    ]
    return text, kb
# ──────────── 25. MINIMAL+ (مینیمال حرفه‌ای) ────────────
def skin_minplus(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    vol = p.get("volume", 100); spd = p.get("speed", 1.0)
    req = p.get("requested_by_name", "—")
    icon = _icon(p)
    n = 24
    filled = int(pct * n / 100)
    bar = "▬" * filled + "▭" * (n - filled)
    text = (
        f"\n"
        f"  {icon}  **{t[:32]}**\n"
        f"  ────────────────────────────────\n"
        f"  👤 {req}\n"
        f"  🕐 {_t(pos)}    🔊 {vol}%    ⚡ {spd}x\n"
        f"\n"
        f"  {bar}\n"
        f"  ▲{pct:>3}%                            ▲100%\n"
        f"  {_t(pos):<10}{_t(dur):>26}\n"
    )
    kb = [
        [_b("⇤⇤", CB["seek_b60"]), _b("⇤", CB["seek_b30"]),
         _b("❮❮", CB["prev"]),
         _b("❚❚" if not p.get("paused") else "▶",
            CB["pause"] if not p.get("paused") else CB["resume"]),
         _b("❯❯", CB["next"]),
         _b("⇥", CB["seek_f30"]), _b("⇥⇥", CB["seek_f60"])],
        [_b("◂vol", CB["vd"]), _b("vol▸", CB["vu"]),
         _b("▫" if not p.get("muted") else "▪",
            CB["mute"] if not p.get("muted") else CB["unmute"]),
         _b("◂⚡", CB["spd_dn"]), _b("⚡▸", CB["spd_up"])],
        [_b("◉ EQ", CB["eq"]), _b("▤ صف", CB["queue"]),
         _b("↻ Rep", CB["rep"]), _b("⇄ Shuf", CB["shuffle"])],
        [_b("↓ دریافت", CB["dl128"]), _b("◼ STOP", CB["stop"]), _b("✕", CB["close"])],
    ]
    return text, kb
# ═══════════════════════════════════════════════
# اسکین‌های انگلیسی
# ═══════════════════════════════════════════════

def skin_en_full(p):
    """English Full"""
    t = _short(p.get("title", "—"), 40)
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    vol = p.get("volume", 100)
    spd = p.get("speed", 1.0)
    src = p.get("source", "SoundCloud")
    req = _short(p.get("requested_by_name", "—"), 25)
    icon = _icon(p)
    rep = p.get("repeat", "off")
    rep_lbl = {"off": "Off", "one": "One", "all": "All"}.get(rep, "Off")
    shuf = "On" if p.get("shuffle") else "Off"
    text = (
        f"{icon} NOW PLAYING\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎵 Title: {t}\n"
        f"👤 Requested by: {req}\n"
        f"🌐 Source: {src}\n"
        f"🔊 Volume: {vol}%\n"
        f"⚡ Speed: {spd}x\n"
        f"🔁 Repeat: {rep_lbl}  🔀 Shuffle: {shuf}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⏱ {_t(pos)}  {_bar(pct, 14)}  {_t(dur)}\n"
        f"📊 Progress: {pct}%"
    )
    kb = [
        [_b("⏮ Prev", CB["prev"]),
         _b("⏯ Pause" if not p.get("paused") else "▶️ Play",
            CB["pause"] if not p.get("paused") else CB["resume"]),
         _b("⏭ Next", CB["next"]),
         _b("⏹ Stop", CB["stop"])],
        [_b("⏪ 60s", CB["seek_b60"]), _b("◀ 30s", CB["seek_b30"]),
         _b("▶ 30s", CB["seek_f30"]), _b("⏩ 60s", CB["seek_f60"])],
        [_b("🔉 Vol-", CB["vd"]), _b(f"🔊 {vol}%", CB["vu"]),
         _b("🔇 Mute" if not p.get("muted") else "🔈 Unmute",
            CB["mute"] if not p.get("muted") else CB["unmute"])],
        [_b("⚡ Slow", CB["spd_dn"]), _b(f"⚡ {spd}x", CB["spd_reset"]),
         _b("⚡ Fast", CB["spd_up"])],
        [_b(f"🔁 {rep_lbl}", CB["rep"]),
         _b("🔀 Shuffle", CB["shuffle"]),
         _b("🎚 EQ", CB["eq"]),
         _b("📋 Queue", CB["queue"])],
        [_b("📥 Download", CB["dl128"]),
         _b("❌ Close", CB["close"])],
    ]
    return text, kb


def skin_en_short(p):
    """English Short"""
    t = _short(p.get("title", "—"), 40)
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    vol = p.get("volume", 100)
    spd = p.get("speed", 1.0)
    icon = _icon(p)
    filled = int(pct * 18 / 100)
    bar = "━" * filled + "●" + "─" * max(0, 17 - filled)
    text = (
        f"{icon} {t}\n"
        f"{_t(pos)} {bar} {_t(dur)}\n"
        f"🔊{vol}% · ⚡{spd}x"
    )
    kb = [
        [_b("⏮", CB["prev"]),
         _b("⏯", CB["pause"] if not p.get("paused") else CB["resume"]),
         _b("⏭", CB["next"]),
         _b("⏹", CB["stop"])],
        [_b("↺60", CB["seek_b60"]), _b("↺30", CB["seek_b30"]),
         _b("↻30", CB["seek_f30"]), _b("↻60", CB["seek_f60"])],
        [_b("🔉", CB["vd"]), _b("🔊", CB["vu"]),
         _b("🔇" if not p.get("muted") else "🔈",
            CB["mute"] if not p.get("muted") else CB["unmute"]),
         _b("🔀", CB["shuffle"])],
        [_b("⚡-", CB["spd_dn"]), _b("⚡+", CB["spd_up"]),
         _b("🔁", CB["rep"]), _b("Q", CB["queue"])],
        [_b("🎚", CB["eq"]), _b("DL", CB["dl128"]), _b("✕", CB["close"])],
    ]
    return text, kb





# ──────────── AURORA ────────────
def skin_aurora(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    vol = p.get("volume", 100)
    f = int(pct * 14 / 100)
    bar = "🟩" * f + "⬛" * (14 - f)
    text = (
        "🌌━━━━━━━━━━━━━━━━━━🌌\n"
        f"✨ **AURORA** {_icon(p)}\n"
        "🌌━━━━━━━━━━━━━━━━━━🌌\n"
        f"🎵 **{t[:32]}**\n{bar}\n"
        f"⏱ {_t(pos)} / {_t(dur)} • {pct}%\n"
        f"🔊 {vol}% • {_rep_label(p.get('repeat','off'))}\n"
        "🌌━━━━━━━━━━━━━━━━━━🌌"
    )
    kb = [
        [_b("⏮", CB["prev"]), _b("⏸" if not p.get("paused") else "▶️", CB["pause"] if not p.get("paused") else CB["resume"]), _b("⏭", CB["next"]), _b("⏹", CB["stop"])],
        [_b("🔉", CB["vd"]), _b("🔊", CB["vu"]), _b("🔇" if not p.get("muted") else "🔈", CB["mute"] if not p.get("muted") else CB["unmute"])],
        [_b(_rep_label(p.get("repeat","off")), CB["rep"]), _b("🔀", CB["shuffle"]), _b("❌", CB["close"])],
    ]
    return text, kb


# ──────────── MATRIX ────────────
def skin_matrix(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    f = int(pct * 15 / 100)
    bar = "▰" * f + "▱" * (15 - f)
    text = (
        "🟢 01001101 01000001 01010100\n"
        f"▓▓ **MATRIX** {_icon(p)} ▓▓\n"
        "🟢 01010010 01001001 01011000\n"
        f"💊 `{t[:30]}`\n`{bar}`\n"
        f"⏱ `{_t(pos)}` / `{_t(dur)}` • {pct}%\n"
        f"⚡ `{p.get('speed', 1.0)}x` • 🔊 `{p.get('volume', 100)}%`"
    )
    kb = [
        [_b("⏮", CB["prev"]), _b("⏸" if not p.get("paused") else "▶️", CB["pause"] if not p.get("paused") else CB["resume"]), _b("⏭", CB["next"]), _b("⏹", CB["stop"])],
        [_b("🔉", CB["vd"]), _b("🔊", CB["vu"]), _b("🔇" if not p.get("muted") else "🔈", CB["mute"] if not p.get("muted") else CB["unmute"])],
        [_b(_rep_label(p.get("repeat","off")), CB["rep"]), _b("🔀", CB["shuffle"]), _b("❌", CB["close"])],
    ]
    return text, kb


# ──────────── SUNSET ────────────
def skin_sunset(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    f = int(pct * 13 / 100)
    bar = "🟧" * f + "🟪" * (13 - f)
    text = (
        "🌇━━━━━━━━━━━━━━━━━🌇\n"
        f"🌅 **SUNSET** {_icon(p)} 🌇\n"
        "🌇━━━━━━━━━━━━━━━━━🌇\n"
        f"🎶 **{t[:32]}**\n{bar}\n"
        f"🌞 {_t(pos)} ──── 🌙 {_t(dur)}\n"
        f"📊 {pct}% • 🔊 {p.get('volume', 100)}%"
    )
    kb = [
        [_b("⏮", CB["prev"]), _b("⏸" if not p.get("paused") else "▶️", CB["pause"] if not p.get("paused") else CB["resume"]), _b("⏭", CB["next"]), _b("⏹", CB["stop"])],
        [_b("🔉", CB["vd"]), _b("🔊", CB["vu"]), _b("🔇" if not p.get("muted") else "🔈", CB["mute"] if not p.get("muted") else CB["unmute"])],
        [_b(_rep_label(p.get("repeat","off")), CB["rep"]), _b("🔀", CB["shuffle"]), _b("❌", CB["close"])],
    ]
    return text, kb


# ──────────── OCEAN ────────────
def skin_ocean(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    f = int(pct * 16 / 100)
    bar = "🌊" * f + "💧" * (16 - f)
    text = (
        "🌊━━━━━━━━━━━━━━━━━━🌊\n"
        f"🐚 **OCEAN** {_icon(p)} 🐚\n"
        "🌊━━━━━━━━━━━━━━━━━━🌊\n"
        f"🎵 **{t[:32]}**\n{bar}\n"
        f"⚓ {_t(pos)} / {_t(dur)} ({pct}%)\n"
        f"🧭 vol {p.get('volume',100)}% • spd {p.get('speed',1.0)}x"
    )
    kb = [
        [_b("⏮", CB["prev"]), _b("⏸" if not p.get("paused") else "▶️", CB["pause"] if not p.get("paused") else CB["resume"]), _b("⏭", CB["next"]), _b("⏹", CB["stop"])],
        [_b("🔉", CB["vd"]), _b("🔊", CB["vu"]), _b("🔇" if not p.get("muted") else "🔈", CB["mute"] if not p.get("muted") else CB["unmute"])],
        [_b(_rep_label(p.get("repeat","off")), CB["rep"]), _b("🔀", CB["shuffle"]), _b("❌", CB["close"])],
    ]
    return text, kb


# ──────────── GALAXY ────────────
def skin_galaxy(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    f = int(pct * 12 / 100)
    bar = "🪐" * f + "⭐" * (12 - f)
    text = (
        "🌠━━━━━━━━━━━━━━━━━🌠\n"
        f"🛸 **GALAXY** {_icon(p)} 🛸\n"
        "🌠━━━━━━━━━━━━━━━━━🌠\n"
        f"🚀 **{t[:32]}**\n{bar}\n"
        f"⏱ {_t(pos)} / {_t(dur)} ({pct}%)\n"
        f"🔊 {p.get('volume',100)}% • ⚡ {p.get('speed',1.0)}x"
    )
    kb = [
        [_b("⏮", CB["prev"]), _b("⏸" if not p.get("paused") else "▶️", CB["pause"] if not p.get("paused") else CB["resume"]), _b("⏭", CB["next"]), _b("⏹", CB["stop"])],
        [_b("🔉", CB["vd"]), _b("🔊", CB["vu"]), _b("🔇" if not p.get("muted") else "🔈", CB["mute"] if not p.get("muted") else CB["unmute"])],
        [_b(_rep_label(p.get("repeat","off")), CB["rep"]), _b("🔀", CB["shuffle"]), _b("❌", CB["close"])],
    ]
    return text, kb



SKINS = [
    "cassette", "cinema", "classic", "compact",
    "concert", "crystal", "cyber", "darkpro",
    "dj", "en_full", "en_short", "fire",
    "glass", "hacker", "minimal", "minplus",
    "mono", "neon", "neon2", "orange",
    "pro", "radio", "retro", "sample",
    "space", "vinyl", "wave",
    "aurora", "matrix", "sunset", "ocean", "galaxy",
]
SKIN_LABELS = {
    "cassette": "📼 کاست",
    "cinema": "🎬 سینما",
    "classic": "🟢 Classic",
    "compact": "⚡ فشرده",
    "concert": "🎤 کنسرت",
    "crystal": "💎 کریستال",
    "cyber": "⚡ سایبرپانک",
    "darkpro": "⚫ Dark Pro",
    "dj": "🎧 دی‌جی",
    "en_full": "🇬🇧 English Full",
    "en_short": "🇬🇧 English Short",
    "fire": "🔥 آتشین",
    "glass": "✨ شیشه‌ای",
    "hacker": "💻 هکر",
    "minimal": "🔵 Minimal",
    "minplus": "◾ مینیمال حرفه‌ای",
    "mono": "⬛ مونو",
    "neon": "🟣 Neon",
    "neon2": "🌌 نئون ۲",
    "orange": "🟧 نارنجی",
    "pro": "🎧 حرفه‌ای",
    "radio": "📻 رادیو",
    "retro": "🟤 Retro",
    "sample": "🇮🇷 نمونه فارسی",
    "space": "🌌 فضایی",
    "vinyl": "💿 صفحه گرام",
    "wave": "🌊 موج صوتی",
    "aurora": "🌌 شفق",
    "matrix": "🟢 ماتریکس",
    "sunset": "🌇 غروب",
    "ocean": "🌊 اقیانوس",
    "galaxy": "🛸 کهکشان",
}



# ──────────── 7. ORANGE ────────────
def skin_orange(p):
    t = p.get("title", "—")
    pos = p.get("position", 0); dur = p.get("duration", 1) or 1
    pct = int(100 * pos / dur) if dur else 0
    vol = p.get("volume", 100)
    spd = p.get("speed", 1.0)
    req = p.get("requested_by_name", "—")
    icon = _icon(p)
    # نوار پیشرفت نارنجی
    n = 16
    filled = int(pct * n / 100)
    bar = "🟧" * filled + "⬜" * (n - filled)
    text = (
        "🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧\n"
        f"🟧   {icon}  SK.TEAM  ORANGE  🟧\n"
        "🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧\n"
        f"🟠 🎵 **{t[:30]}**\n"
        f"🟠 🎤 {req}\n"
        "🟠━━━━━━━━━━━━━━━━━━━\n"
        f"  {bar}\n"
        f"  🔸 {pct}%  ·  {_t(pos)} / {_t(dur)}\n"
        f"  🔸 🔊 {vol}%  ·  ⚡ {spd}x\n"
        "🟠━━━━━━━━━━━━━━━━━━━\n"
        "🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧"
    )
    kb = [
        # ردیف ۱: کنترل اصلی
        [_b("🟠⏪", CB["seek_b60"]),
         _b("🟠⏮", CB["prev"]),
         _b("🟠⏸" if not p.get("paused") else "🟠▶",
            CB["pause"] if not p.get("paused") else CB["resume"]),
         _b("🟠⏭", CB["next"]),
         _b("🟠⏩", CB["seek_f60"])],
        # ردیف ۲: کنترل پیشرفته
        [_b("🔸◀️◀️", CB["seek_b30"]),
         _b("🔥⏪", CB["seek_b60"]),
         _b("🟠⏹", CB["stop"]),
         _b("🔥⏩", CB["seek_f60"]),
         _b("🔸▶️▶️", CB["seek_f30"])],
        # ردیف ۳: صدا و سرعت
        [_b("🟠🔉", CB["vd"]),
         _b(f"🔥{vol}%", CB["vu"]),
         _b("🟠🔇" if not p.get("muted") else "🟠🔊",
            CB["mute"] if not p.get("muted") else CB["unmute"]),
         _b("🟠🐢", CB["spd_dn"]),
         _b("🟠🐇", CB["spd_up"])],
        # ردیف ۴: تنظیمات
        [_b("🔶 EQ", CB["eq"]),
         _b("🔸 صف", CB["queue"]),
         _b("🔥 ریپیت", CB["rep"]),
         _b("🔶 شافل", CB["shuffle"])],
        # ردیف ۵: اضافی
        [_b("🔥 دانلود فایل", CB["dl128"]),
         _b("🟠 دریافت ۳۲۰", CB["dl320"])],
        # ردیف ۶: بستن
        [_b("🔴 بستن پنل", CB["close"])],
    ]
    return text, kb

def render(skin, data):
    fn = {
        "cassette": skin_cassette,
        "cinema": skin_cinema,
        "classic": skin_classic,
        "compact": skin_compact,
        "concert": skin_concert,
        "crystal": skin_crystal,
        "cyber": skin_cyber,
        "darkpro": skin_darkpro,
        "dj": skin_dj,
        "en_full": skin_en_full,
        "en_short": skin_en_short,
        "fire": skin_fire,
        "glass": skin_glass,
        "hacker": skin_hacker,
        "minimal": skin_minimal,
        "minplus": skin_minplus,
        "mono": skin_mono,
        "neon": skin_neon,
        "neon2": skin_neon2,
        "orange": skin_orange,
        "pro": skin_pro,
        "radio": skin_radio,
        "retro": skin_retro,
        "sample": skin_sample,
        "space": skin_space,
        "vinyl": skin_vinyl,
        "wave": skin_wave,
        "aurora": skin_aurora,
        "matrix": skin_matrix,
        "sunset": skin_sunset,
        "ocean": skin_ocean,
        "galaxy": skin_galaxy,
    }.get(skin, skin_sample)
    text, rows = fn(data)
    return text, InlineKeyboardMarkup(rows)
