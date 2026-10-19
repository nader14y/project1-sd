import json
import random
from pathlib import Path

from engine import Question, ROUNDS

QUESTIONS_PATH = "questions.json"        # محتوای محصول → داخل git
LEADERBOARD_PATH = "leaderboard.json"    # داده‌ی بازیکن‌ها → داخل .gitignore


class QuestionBank:
    """بانک سؤال — از فایل خوانده می‌شود، نه از دلِ کد."""

    def __init__(self, path: str = QUESTIONS_PATH) -> None:
        with open(path, encoding="utf-8") as f:      # ← encoding را جا نیندازید
            raw = json.load(f)

        self._questions: list[Question] = []
        for item in raw:
            self._questions.append(
                Question(
                    item["text"],
                    item["options"],
                    item["correct"],
                    item.get("power_up"),            # get یعنی «اگر نبود، None»
                )
            )

    def count(self) -> int:
        return len(self._questions)

    def pick(self, n: int = ROUNDS) -> list[Question]:
        """n سؤال تصادفی و بدون تکرار — پس هر مسابقه فرق می‌کند."""
        if self.count() < n:
            raise ValueError(
                f"بانک سؤال {self.count()} سؤال دارد؛ برای یک مسابقه {n} سؤال لازم است"
            )
        return random.sample(self._questions, n)


class ScoreBoard:
    """رده‌بندی کل — تنها داده‌ای که بین اجراها می‌ماند."""

    def __init__(self, path: str = LEADERBOARD_PATH) -> None:
        self._path = Path(path)
        self._data: dict[str, dict[str, int]] = {}

        if self._path.exists():                      # اولین بار که بازی اجرا می‌شود، وجود ندارد
            with open(self._path, encoding="utf-8") as f:
                self._data = json.load(f)

    def is_empty(self) -> bool:
        return not self._data

    def record(self, winner: str | None,
               player1: str, score1: int,
               player2: str, score2: int) -> None:
        """نتیجه‌ی یک مسابقه را ثبت و همان لحظه ذخیره می‌کند."""
        for name, points in [(player1, score1), (player2, score2)]:
            if name not in self._data:
                self._data[name] = {"wins": 0, "points": 0}
            self._data[name]["points"] += points

        if winner is not None:
            self._data[winner]["wins"] += 1

        self._save()

    def top(self, n: int = 5) -> list[tuple[str, dict[str, int]]]:
        """n نفر برتر: اول بیشترین برد، بعد بیشترین امتیاز.

        🌱 این یک خط، «مرتب‌سازی با کلیدِ دوتایی» است. امروز فقط استفاده‌اش
           می‌کنیم؛ بازکردنش مسیر پیشرفته است.
        """
        return sorted(
            self._data.items(),
            key=lambda item: (item[1]["wins"], item[1]["points"]),
            reverse=True,
        )[:n]

    def _save(self) -> None:
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)
            #                        ^^^^^^^^^^^^^^^^^^  ^^^^^^^^
            #                        فارسی، نه ع     خوانا، و diff تمیز


# ─────────────────────────────────────────────────────────────────────
# 🌱 آیا حس می‌کنید storage.py دو شغل دارد؟ (سؤال‌ها، و رده‌بندی)
#    درست حس می‌کنید. ولی هنوز **درد** ندارد. روزی که داشت، دو فایلش می‌کنیم.
#    قاعده‌ی جلسه‌ی ۴: فایل تازه، جوابِ یک دردِ واقعی است — نه احتیاطِ از پیش.
#
# 💡 مسیر پیشرفته:
#    ۱) اعتبارسنجی هنگام خواندن: سؤال بدون ۴ گزینه → خطای واضح با *شماره‌ی* سؤال
#    ۲) draws و played را هم به رده‌بندی اضافه کنید
#    ۳) ScoreBoard با sqlite3 — و دقت کنید هیچ فایل دیگری عوض نمی‌شود
