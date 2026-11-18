def sub_menu(chat_id):
    from bot import _sub_is_active, _sub_days
    import sqlite3
    from pathlib import Path
    _gdb = Path.home() / "groupbot" / "data" / "groupbot.db"
    NL = chr(10)

    def _exp(cid, st):
        try:
            conn = sqlite3.connect(str(_gdb), timeout=5)
            r = conn.execute("SELECT expire_date FROM subscriptions WHERE chat_id=? AND sub_type=?", (cid, st)).fetchone()
            conn.close()
            if r and r[0]:
                return r[0].split()[0]
        except Exception:
            pass
        return "—"

    def _line(st):
        active = _sub_is_active(chat_id, st)
        days = _sub_days(chat_id, st)
        exp = _exp(chat_id, st)
        if active:
            return "  وضعیت: ✅ فعال" + NL + "  تاریخ انقضا: " + exp + NL + "  روزهای مانده: " + str(days) + NL
        return "  وضعیت: ❌ غیرفعال" + NL + "  تاریخ انقضا: —" + NL + "  روزهای مانده: —" + NL

    text = (
        "💎 اشتراک Sk.Team Music" + NL
        + "━━━━━━━━━━━━━━━━━━" + NL + NL
        + "🎵 موزیک‌پلیر:" + NL
        + _line("music") + NL
        + "🎙 ریکورد ویس‌کال:" + NL
        + _line("vcall") + NL
        + "📞 برای تمدید با سازنده تماس بگیرید" + NL
        + "@Siavashska"
    )
    kb = [
        [b("🔄 تمدید", "set_sub_renew")],
        [b("📜 تاریخچه", "set_sub_history")],
        [b("🔙 بازگشت", CB["back"])],
        [b("❌ بستن", CB["close"])],
    ]
    return text, InlineKeyboardMarkup(kb)
