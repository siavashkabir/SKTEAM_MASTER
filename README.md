# SK.TEAM Master

مجموعهٔ ربات‌های تلگرام (Python) + پنل وب (Cloudflare Worker) با دیتابیس ابری **Turso** و **Supabase**.

| پوشه | توضیح |
|---|---|
| `groupbot/` | ربات مدیریت گروه + `userbot_service.py` (Termux) |
| `skteam_music/` | ربات موزیک (Termux) |
| `sk_media/` | Media server (Termux) |
| `melody-player/` | پلیر ویس‌چت (Proot Ubuntu) |
| `webpanel/` | پنل وب (Cloudflare Worker + فرانت‌اند ثابت) |

## دیتابیس (Turso)
تمام فایل‌ها به‌جای `sqlite3` از ماژول `turso_db.py` (سازگار با API ‏sqlite3، مبتنی بر `libsql-client`) استفاده می‌کنند.
- اگر `TURSO_DATABASE_URL` تنظیم باشد → اتصال به Turso.
- اگر تنظیم نباشد یا `libsql-client` نصب نباشد → خطا لاگ می‌شود و به sqlite لوکال برمی‌گردد (ربات از کار نمی‌افتد).
- برای هر فایل دیتابیس می‌توان دیتابیس جدا داد: `TURSO_URL_<NAME>` / `TURSO_TOKEN_<NAME>` (مثلاً `TURSO_URL_SETTINGS` برای `settings.db`، `TURSO_URL_GROUPBOT` برای `groupbot.db`).
- هر دستور روی سرور auto-commit است (`commit()` بی‌اثر است). تأخیر شبکه دارد؛ دیتابیس را نزدیک سرور بسازید.

انتقال دادهٔ فعلی: `turso db shell <name> < dump.sql` (با `sqlite3 groupbot.db .dump > dump.sql`).

## متغیرهای محیطی
در `~/.env` (فایل `.env` هرگز کامیت نمی‌شود):

```env
# ربات‌ها
MANAGER_BOT_TOKEN=...        # groupbot (اجباری)
MUSIC_BOT_TOKEN=...          # skteam_music (اجباری)
MUSIC_BOT_API_KEY=...        # یکسان در groupbot، skteam_music و melody-player/.env
MUSIC_MGMT_KEY=...
MUSIC_PLAYER_KEY=...
SIGHTENGINE_USER=...
SIGHTENGINE_SECRET=...

# Turso
TURSO_DATABASE_URL=libsql://<db>-<org>.turso.io
TURSO_AUTH_TOKEN=...         # turso db tokens create <db>
```

`melody-player/.env`: `PANEL_API_BASE`, `PLAYER_API_KEY`, `TG_API_ID`, `TG_API_HASH`, `TG_SESSION_STRING`, `MUSIC_BOT_API_KEY`.

پنل وب (Cloudflare):

| نام | نوع | توضیح |
|---|---|---|
| `TURSO_DATABASE_URL` | var در `wrangler.toml` | آدرس libsql |
| `SUPABASE_URL` | var در `wrangler.toml` | `https://<project>.supabase.co` |
| `TURSO_AUTH_TOKEN` | secret | توکن Turso |
| `SUPABASE_SERVICE_KEY` | secret | کلید service_role از Supabase → Settings → API |
| `ADMIN_TOKEN` | secret | رمز ورود پنل (رشتهٔ تصادفی بلند) |
| `CLOUDFLARE_API_TOKEN` / `CLOUDFLARE_ACCOUNT_ID` | محیط CI/دیپلوی | برای `wrangler deploy` غیرتعاملی |

## اجرا در Termux
```bash
pkg update && pkg install -y python git clang rust libffi openssl libjpeg-turbo freetype proot-distro
git clone -b copilot-fixes https://github.com/siavashkabir/SKTEAM_MASTER ~/SKTEAM_MASTER
cd ~/SKTEAM_MASTER && cp -r groupbot skteam_music sk_media ~/ && cp start_all.sh ~/
nano ~/.env                       # متغیرهای بالا
cd ~/groupbot && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt && deactivate
cd ~/skteam_music && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt && deactivate
bash ~/start_all.sh
```
`sk_media/server.py` با venv ‏groupbot اجرا می‌شود؛ `pip install -r ~/sk_media/requirements.txt` را در همان venv بزنید.

## اجرا در Proot (پلیر)
```bash
proot-distro install ubuntu
proot-distro login ubuntu
apt update && apt install -y python3 python3-venv ffmpeg git
cd /root/melody-player && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt
nano .env      # متغیرهای melody-player بالا
```
از Termux با `start_all.sh` (مرحلهٔ ۵) اجرا می‌شود؛ `MUSIC_BOT_API_KEY` باید در `melody-player/.env` باشد.

## پنل وب
```bash
cd webpanel && npm install
# مقادیر YOUR-* را در wrangler.toml عوض کنید
npx wrangler login
npx wrangler secret put ADMIN_TOKEN
npx wrangler secret put TURSO_AUTH_TOKEN
npx wrangler secret put SUPABASE_SERVICE_KEY
npm run deploy
```
بررسی: `curl https://<worker>.workers.dev/api/health` ← `{"ok":true,"turso":"ok","supabase":"ok"}`.
مسیرهای API (به‌جز health نیاز به `Authorization: Bearer $ADMIN_TOKEN`): `/api/turso/tables`, `/api/turso/table/<name>`, `/api/supabase/<table>`.

## ⚠️ امنیت
توکن‌ها و کلیدهایی که قبلاً در کد/تاریخچهٔ git بودند (توکن دو ربات، Sightengine، کلیدهای Music API، `.env.BACKUP`، `telethon_session.txt`، `cookies_yt.txt`) لو رفته‌اند: **حتماً همه را عوض (revoke) کنید.** این فایل‌ها از ردیابی git خارج و در `.gitignore` قرار گرفتند.
