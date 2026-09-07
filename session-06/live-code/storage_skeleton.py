"""📒 دفتردار بازی — رفت‌وآمد با فایل‌ها.

پروژه از امروز سه شغل دارد، و هر شغل یک فایل:

    engine.py    🧠 مغز       → قواعد، امتیاز، برنده        (نه print، نه input، نه فایل)
    game.py      👄 دهان      → نمایش، ورودی، رنگ، کرنومتر
    storage.py   📒 دفتردار   → خواندن و نوشتنِ فایل‌ها      ← تازه، امروز

⚠️ اینجا هیچ قاعده‌ای از بازی نیست، و هیچ رنگ و پیامی هم نیست.
   دفتردار فقط می‌رود سر قفسه، می‌آورد؛ و در دفتر می‌نویسد.

📌 این اسکلت را یک‌بار کپی کنید، اسمش را storage.py بگذارید، و بدنه‌ها را با هم پر کنیم.
🐍 نیاز: پایتون ۳٫۱۰ یا بالاتر
"""

import json
import random
from pathlib import Path

from engine import Question, ROUNDS

QUESTIONS_PATH = "questions.json"        # محتوای محصول → داخل git
LEADERBOARD_PATH = "leaderboard.json"    # داده‌ی بازیکن‌ها → داخل .gitignore


class QuestionBank:
    """بانک سؤال — از فایل خوانده می‌شود، نه از دلِ کد.

    می‌داند: لیستی از Questionها
    می‌کند: چندتا سؤال تصادفی به بازی می‌دهد
    """

    def __init__(self, path: str = QUESTIONS_PATH) -> None:
        # TODO ۱: فایل را با encoding="utf-8" باز کن و با json.load بخوان
        #         with open(path, encoding="utf-8") as f:
        #             raw = json.load(f)
        #
        # TODO ۲: self._questions را بساز و برای هر item در raw،
        #         یک Question بساز و به لیست اضافه کن.
        #         کلیدها: item["text"] · item["options"] · item["correct"]
        #         و برای قدرت ویژه:  item.get("power_up")
        #         (get یعنی «اگر این کلید نبود، None بده» — خطا نده)
        pass

    def count(self) -> int:
        # TODO: چند سؤال در بانک است؟
        pass

    def pick(self, n: int = ROUNDS) -> list[Question]:
        """n سؤال تصادفی و بدون تکرار — پس هر مسابقه فرق می‌کند."""
        # TODO ۱: اگر بانک کمتر از n سؤال دارد، ValueError بده
        #         (متن خطا: چند سؤال داریم و چند لازم است)
        # TODO ۲: return random.sample(self._questions, n)
        pass


class ScoreBoard:
    """رده‌بندی کل — تنها داده‌ای که بین اجراها می‌ماند."""

    def __init__(self, path: str = LEADERBOARD_PATH) -> None:
        self._path = Path(path)
        self._data: dict[str, dict[str, int]] = {}

        # TODO: اگر فایل *وجود دارد* (self._path.exists())، بخوانش و در _data بریز.
        #       اولین اجرای بازی، این فایل هنوز ساخته نشده — و این خطا نیست.
        pass

    def is_empty(self) -> bool:
        return not self._data

    def record(self, winner: str | None,
               player1: str, score1: int,
               player2: str, score2: int) -> None:
        """نتیجه‌ی یک مسابقه را ثبت و همان لحظه ذخیره می‌کند."""
        # TODO ۱: برای هر دو بازیکن:
        #         اگر اسمش در _data نبود، جای خالی بساز: {"wins": 0, "points": 0}
        #         بعد امتیاز این مسابقه را به points اضافه کن
        # TODO ۲: اگر winner برابر None نبود، یکی به wins برنده اضافه کن
        # TODO ۳: self._save() را صدا بزن  ← بدون این، هیچ‌چیز روی دیسک نمی‌رود
        pass

    # ── آماده (دست نزنید) ──

    def top(self, n: int = 5) -> list[tuple[str, dict[str, int]]]:
        """n نفر برتر: اول بیشترین برد، بعد بیشترین امتیاز."""
        return sorted(
            self._data.items(),
            key=lambda item: (item[1]["wins"], item[1]["points"]),
            reverse=True,
        )[:n]

    # ── کارِ اصلیِ امروز ──

    def _save(self) -> None:
        """دفتر را روی دیسک می‌نویسد.

        ⚠️ سه چیز در این تابع مهم است و هر سه را با هم می‌نویسیم:
              "w"                 → حالت نوشتن
              encoding="utf-8"    → وگرنه روی ویندوز فارسی خراب می‌شود
              ensure_ascii=False  → وگرنه اسم‌ها می‌شوند \\u0639\\u0644\\u06cc
              indent=2            → وگرنه همه‌ی فایل یک خط می‌شود
        """
        # TODO: فایل را در حالت "w" باز کن و با json.dump داده را بنویس
        pass
