from pathlib import Path
# ========================================
# تنظیمات ربات مدیریت گروه اسکای تیم
# ========================================

# --- اطلاعات ربات ---

# لیست فحش‌ها
try:
    from bad_words import BAD_WORDS
except ImportError:
    BAD_WORDS = []
import os as _os
try:
    from dotenv import load_dotenv as _ld
    _ld(_os.path.expanduser("~/.env"))
except Exception:
    pass
BOT_TOKEN = _os.environ.get("MANAGER_BOT_TOKEN", "")
if not BOT_TOKEN:
    raise RuntimeError("MANAGER_BOT_TOKEN is not set (put it in ~/.env)")
BOT_USERNAME = "@sk_team_mediaplayerbot"

# --- مالک ربات ---
OWNER_ID = 7955185125
OWNER_USERNAME = "@Siavashska"

# --- برند تیم ---
TEAM_NAME = "اسکای تیم"
TEAM_FULL_NAME = "Sky Team"
TEAM_EMOJI = "🛹"
TEAM_SLOGAN = "به گروه {group_name} خوش آمدید!"
SUPPORT_USERNAME = "@Siavashska"

# --- دیتابیس ---
DATABASE_PATH = str(Path(__file__).resolve().parent / "data" / "groupbot.db")
RESTART_FLAG_FILE = "data/restart_flag.txt"

# --- پیام خوش آمدگویی پیش فرض ---
DEFAULT_WELCOME = (
    "🎉 {mention} عزیز،\n"
    "به گروه **{group_name}** خوش آمدی! 🌟\n\n"
    "📌 لطفاً قوانین گروه رو مطالعه کن."
)
DEFAULT_RULES = "📜 قوانین گروه:\n1. احترام به همه\n2. ممنوعیت تبلیغات\n3. ممنوعیت فحاشی"

# --- کلمات ممنوعه ---
# BAD_WORDS از فایل bad_words.py import می‌شه

# --- حالت‌ها ---
WELCOME_ENABLED = True
ANTISPAM_ENABLED = True
ANTI_LINK_ENABLED = True

# --- تنظیمات NSFW (Sightengine) ---
SIGHTENGINE_USER = _os.environ.get("SIGHTENGINE_USER", "")
SIGHTENGINE_SECRET = _os.environ.get("SIGHTENGINE_SECRET", "")


# ========================================================
# تنظیمات ربات موزیک پلیر (برای دریافت آمار کال)
# ========================================================
# این API_KEY رو توی ربات موزیک پلیر هم بذار (باید یکسان باشه)
MUSIC_BOT_API_KEY = _os.environ.get("MUSIC_BOT_API_KEY", "")

# آیدی عددی ربات موزیک پلیر (اگه ربات تلگرامه)
MUSIC_BOT_ID = 0  # بعداً پر کن

# توکن ربات موزیک پلیر (اختیاری - برای ارتباط مستقیم)
MUSIC_BOT_TOKEN = ""  # بعداً پر کن

# ========================================================

# ═══════════════════════════════════════════════════
# Music Player API (Lovable)
# ═══════════════════════════════════════════════════
MUSIC_API_BASE = "https://project--b8962080-6b65-4712-a6ea-051e02bdecb9.lovable.app/api/public/mgmt"
MUSIC_MGMT_KEY = _os.environ.get("MUSIC_MGMT_KEY", "")
MUSIC_PLAYER_KEY = _os.environ.get("MUSIC_PLAYER_KEY", "")
