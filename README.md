# Quiz Battle

A two-player Persian quiz game with web and terminal interfaces. No database is required.

## بازی آنلاین با GitHub Pages

[اجرای کوییز بتل در مرورگر](https://nader14y.github.io/project1-sd/)

نسخهٔ GitHub Pages بدون سرور پایتون اجرا می‌شود. Pyodide همان `engine.py`، `storage.py` و `web_game.py` را در مرورگر اجرا می‌کند؛ فایل موتور بازی تغییر نکرده است. در دریافت اولیه، دانلود محیط پایتون ممکن است کمی زمان ببرد و به دسترسی به `cdn.jsdelivr.net` نیاز دارد.

بازی همچنان نوبتی و روی یک دستگاه است. وضعیت بازی و جدول قهرمان‌ها در `localStorage` همین مرورگر ذخیره می‌شوند و با تازه‌سازی صفحه بازیابی می‌شوند. جدول امتیازها بین دستگاه‌ها مشترک نیست. زمان، پاسخ‌های صحیح و داده‌های امتیاز در اختیار مرورگرند و این نسخه تضمین جلوگیری از دست‌کاری امتیازها را ندارد. با پاک‌کردن داده‌های سایت، نتیجه‌ها هم پاک می‌شوند. اگر ذخیره‌سازی مرورگر در دسترس نباشد، هشدار نمایش داده می‌شود و بازی تا زمانی که صفحه باز است ادامه دارد.

هر push به `main`، تست‌ها و ساخت سایت را در GitHub Actions اجرا می‌کند و در صورت موفقیت روی Pages منتشر می‌کند. [راهنمای ساخت و انتشار Pages](docs/pages-deployment.fa.md) شامل تنظیمات، ساخت محلی و رفع خطاست.

## نسخهٔ وب با سرور Flask

رابط وب فارسی و راست‌به‌چپ است و روی موبایل و دسکتاپ اجرا می‌شود. دو بازیکن روی **یک دستگاه**، نوبتی به سؤال‌های یکسان پاسخ می‌دهند. فایل `engine.py` بدون تغییر باقی مانده و تمام محاسبات امتیاز توسط همان موتور انجام می‌شود.

برای شرح ورودی و خروجی همهٔ توابع، مسیرهای API، تنظیمات، مدیریت خطا و تابع `serve`، [مستندات فارسی توابع web.py](docs/web-functions.fa.md) را بخوانید.

### نصب و اجرا

پایتون ۳٫۱۰ یا جدیدتر لازم است.

```bash
python -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -r requirements-web.txt
python web.py
```

سپس [بازی را در مرورگر باز کنید](http://127.0.0.1:8000).

۱. نام دو بازیکن را وارد کنید؛ نام‌ها باید متفاوت باشند.
۲. بازیکن اول «آماده‌ام» را می‌زند؛ سؤال و زمان‌سنج ۳۰ ثانیه‌ای شروع می‌شوند.
۳. پس از پاسخ یا پایان زمان، دستگاه را به بازیکن دوم بدهید. زمان او فقط پس از زدن «آماده‌ام» شروع می‌شود.
۴. نتیجه و پاسخ درست پس از نوبت هر دو نفر نمایش داده می‌شوند.
۵. پس از پنج راند، برنده و جدول قهرمان‌ها نمایش داده می‌شوند. می‌توانید دوباره با همان افراد یا بازیکن‌های تازه بازی کنید.

### داده، زمان و مدیریت خطا

- سؤال‌ها از `questions.json` و جدول امتیازها از `leaderboard.json` خوانده می‌شوند. دیتابیس و حساب کاربری وجود ندارد.
- وضعیت بازی‌های فعال در حافظهٔ سرور است. تازه‌سازی صفحه بازی را ادامه می‌دهد، اما راه‌اندازی مجدد سرور بازی‌های فعال را پاک می‌کند. جدول امتیازها باقی می‌ماند.
- بازی پس از دو ساعت بی‌فعالیتی منقضی می‌شود؛ حداکثر ۵۱۲ بازی هم‌زمان در حافظه نگه داشته می‌شود.
- زمان پاسخ در سرور محاسبه می‌شود؛ زمان و امتیاز ارسالی مرورگر قابل اعتماد نیستند. بستن صفحه یا جابه‌جایی تب زمان را متوقف نمی‌کند. تأخیر شبکه هم بخشی از زمان پاسخ محسوب می‌شود.
- ارسال مجدد پاسخ یا درخواست راند بعد، امتیاز یا راند اضافه نمی‌کند. نتیجهٔ پاسخ نفر اول تا پایان نوبت نفر دوم مخفی می‌ماند.
- جدول امتیازها ابتدا در فایل موقت نوشته و سپس به‌صورت اتمی جایگزین می‌شود. خطای ذخیره، نتیجهٔ نهایی را از بین نمی‌برد؛ با تازه‌سازی صفحه یا دکمهٔ تلاش دوباره، ذخیره تکرار می‌شود.
- فایل جدول امتیازهای خراب با هشدار در لاگ کنار گذاشته می‌شود و جدول خالی بارگذاری می‌شود. برای حفظ سابقه، پیش از اولین ذخیرهٔ بعدی فایل خراب را بررسی یا پشتیبان‌گیری کنید.
- ورودی نامعتبر، سؤال‌های خراب، نبود فایل، پایان نشست، درخواست تکراری، خطای شبکه و خطای غیرمنتظره پیام مناسب دارند. جزئیات خطای داخلی به مرورگر ارسال نمی‌شود.
- نشست‌ها با کوکی امضاشده و `HttpOnly`/`SameSite` جدا می‌شوند. درخواست‌های تغییر وضعیت به توکن CSRF نیاز دارند. پاسخ سؤال‌ها و محتوای درخواست‌ها در لاگ ثبت نمی‌شوند.

### لاگ

نسخهٔ وب رویدادهای شروع بازی، شروع نوبت، ثبت پاسخ، نتیجهٔ راند، پایان بازی و درخواست‌های HTTP را در `quiz_web.log` ثبت می‌کند. هر درخواست شناسهٔ پیگیری دارد که در هدر `X-Request-ID` و خطاهای JSON نیز برمی‌گردد. هر فایل حداکثر ۱ مگابایت و تعداد نسخه‌های پشتیبان ۳ است. اگر فایل لاگ قابل نوشتن نباشد، لاگ در خروجی خطا نوشته می‌شود.

### تست‌ها

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

تست‌ها قوانین موتور، کل جریان پنج راند، دوبل و امتیاز سرعت، تساوی، محاسبهٔ زمان در سرور، پایان زمان، تازه‌سازی صفحه، جداسازی نشست‌ها، ورودی نامعتبر، CSRF، درخواست تکراری و هم‌زمان، خرابی فایل‌ها، ذخیرهٔ اتمی، بازیابی پس از خطای ذخیره و لاگ را بررسی می‌کنند. همهٔ فایل‌های دادهٔ تست در پوشه‌های موقت ایجاد می‌شوند.

### تنظیمات اجرا

نسخهٔ وب با Waitress و هشت thread اجرا می‌شود. چون وضعیت بازی در حافظه و جدول امتیاز در JSON نگهداری می‌شود، برنامه را با **یک process** اجرا کنید؛ اجرای چند worker/process یا اجرای هم‌زمان رابط ترمینال و وب روی یک `leaderboard.json` پشتیبانی نمی‌شود.

| متغیر محیطی | مقدار پیش‌فرض | کاربرد |
|---|---|---|
| `QUIZ_HOST` | `127.0.0.1` | برای دسترسی از دستگاه دیگر در شبکه، `0.0.0.0` قرار دهید |
| `QUIZ_PORT` | `8000` | پورت وب |
| `QUIZ_SECRET_KEY` | تصادفی در هر اجرا | در استقرار، یک رشتهٔ تصادفی بلند و ثابت تنظیم کنید |
| `QUIZ_HTTPS` | غیرفعال | پشت HTTPS مقدار `1` بگذارید تا کوکی فقط روی HTTPS ارسال شود |

این نسخه برای بازی نوبتی روی یک دستگاه است؛ اتاق آنلاین بین دو دستگاه ندارد. در استقرار عمومی، HTTPS را روی reverse proxy تنظیم کنید.

## Terminal version

Each match has 5 rounds. In each round, both players answer the same multiple-choice question (A–D).

- A correct answer gets **10 points**.
- The fastest correct answer gets **+3 bonus** points.
- An answer that takes more than **30 seconds** gets 0 points.
- On a `"double"` power-up question, correct answers get double points.

A leaderboard, ranked by wins and then by points, is saved to `leaderboard.json`.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Play

```bash
python game.py
```

## Test

```bash
pytest
```

## Build an executable

Build a standalone program that runs without Python. Run the script inside the venv, on the system you are building for (PyInstaller cannot build a Windows `.exe` on a Mac, or the reverse).

- **Windows:** double-click `build.bat`, or run it in a terminal.
- **Mac:** `./build.sh`

The program is created in `dist/` (`QuizBattle.exe` on Windows, `QuizBattle` on Mac). To share it, put `questions.json` in the same folder as the program. The program creates `leaderboard.json` next to itself, and writes `quiz_game.log` in the folder it is started from.

On a Mac, the first time you open the program, right-click it and choose **Open**, because it is not signed. A program built on an Apple Silicon Mac does not run on an Intel Mac.

## Files

| File | Purpose |
|------|---------|
| `game.py` | Terminal UI (menu, rounds, leaderboard) |
| `web.py` | Flask API, session validation, error handlers, Waitress entry point |
| `web_game.py` | Web match lifecycle, server timer, locking, expiry, duplicate protection |
| `templates/` / `static/` | Responsive Persian web interface, CSS and JavaScript |
| `engine.py` | Game rules: `Question`, `Match`, scoring |
| `storage.py` | `QuestionBank` (reads `questions.json`) and `ScoreBoard` (`leaderboard.json`) |
| `app_log.py` | Logging setup (writes to `quiz_game.log`) |
| `requirements-web.txt` / `requirements-dev.txt` | Minimal web dependencies / test dependencies |
| `questions.json` | Question bank |
| `tests/` | pytest tests for the engine and storage |
| `build.bat` / `build.sh` | Build the executable on Windows / Mac |

## Adding questions

Add an entry to `questions.json`:

```json
{
  "text": "Question text",
  "options": ["A", "B", "C", "D"],
  "correct": "A",
  "power_up": "double"
}
```

Each question needs exactly 4 options, and `correct` must be a letter from A to D. `power_up` is optional.
