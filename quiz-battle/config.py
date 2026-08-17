"""تنظیمات و ثابت‌های Quiz Battle.

قانون جلسه‌ی ۶: هیچ عدد جادویی‌ای در کد پخش نمی‌شود — همه اینجا، با اسم.
"""

import sys
from pathlib import Path

APP_NAME = "Quiz Battle"
APP_VERSION = "1.0.0"

# --- قواعد بازی (۵ قانون محصول) ---------------------------------------
ROUNDS = 5                 # هر مسابقه دقیقاً ۵ راند
TIME_LIMIT = 30            # مهلت هر جواب، به ثانیه
POINTS_CORRECT = 10        # امتیاز جواب درست
SPEED_BONUS = 3            # بونوس سریع‌ترین درست‌جواب
STEAL_AMOUNT = 5           # امتیازی که سرقت از حریف کم می‌کند
DOUBLE_MULTIPLIER = 2      # ضریب سؤال دوبل

LETTERS = "ABCD"

# نمایش قدرت‌های ویژه: کلید → (ایموجی، نام، توضیح)
POWER_UPS: dict[str, tuple[str, str, str]] = {
    "double": ("⚡", "دوبل", f"امتیاز این سؤال {DOUBLE_MULTIPLIER} برابر می‌شود!"),
    "steal": ("🎯", "سرقت", f"هر جواب درست، {STEAL_AMOUNT} امتیاز از حریف کم می‌کند!"),
    "shield": ("🛡️", "سپر", "جواب درست یک سپر می‌گیرد که جلوی سرقتِ بعدی را می‌گیرد."),
}

# «سپر» قابلیتِ امضای همین نسخه‌ی مرجع است؛ هر تیم قابلیت خودش را انتخاب می‌کند.
SIGNATURE_POWER_UP = "shield"


def app_dir() -> Path:
    """پوشه‌ای که برنامه واقعاً از آن اجرا می‌شود — چه از سورس، چه از فایل اجرایی."""
    if getattr(sys, "frozen", False):        # یعنی داخل بسته‌ی PyInstaller هستیم
        return Path(sys.executable).parent
    return Path(__file__).parent


QUESTIONS_PATH = app_dir() / "questions.json"
LEADERBOARD_PATH = app_dir() / "leaderboard.json"
LOG_PATH = app_dir() / "game.log"
