
"""📒 دفتردار بازی.  ✅ وضعیت مطلوب پایان جلسه‌ی ۱۰

🆕 امروز دو تصمیمِ **متفاوت** برای دو فایل گرفتیم:

    questions.json نباشد یا خراب باشد  →  فریاد می‌زنیم؛ بازی نمی‌تواند ادامه دهد
    leaderboard.json خراب باشد         →  از نو شروع می‌کنیم؛ بازی ادامه می‌دهد

معیارش یک سؤال است:  **«بدون این داده می‌شود بازی کرد؟»**
بدون سؤال، نه. بدون تاریخچه‌ی رده‌بندی، بله — حیف است، ولی می‌شود.

⚠️ و دقت کنید: دفتردار **فریاد می‌زند**، ولی پیامِ مهربان به کاربر نمی‌دهد.
   ترجمه‌ی فریاد به جمله‌ی آدمیزاد، کارِ دهان است.
"""

import json
import random
from pathlib import Path

from engine import Question, ROUNDS

QUESTIONS_PATH = "questions.json"
LEADERBOARD_PATH = "leaderboard.json"

class QuestionBank:
    def __init__(self, path: str = QUESTIONS_PATH) -> None:
        if not Path(path).exists():
            raise FileNotFoundError(f"فایل بانک سؤال پیدا نشد: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as error:
            # خطای خامِ پایتون را به خطایی ترجمه می‌کنیم که *شماره‌ی خط* را بگوید
            raise ValueError(
                f"فایل بانک سؤال خراب است (خط {error.lineno}): {error.msg}"
            ) from error

        if not isinstance(data, list) or not data:
            raise ValueError("بانک سؤال باید یک لیست غیرخالی باشد")

        self._questions: list[Question] = []
        for item in data:
            question = Question(
                text=item["text"],
                options=item["options"],
                correct=item["correct"],
                power_up=item.get("power_up"),
            )
            self._questions.append(question)

    def count(self) -> int:
        return len(self._questions)

    def pick(self, n: int = ROUNDS) -> list[Question]:
        if self.count() < n:
            raise ValueError(
                f"بانک سؤال {self.count()} سؤال دارد؛ برای یک مسابقه {n} سؤال لازم است"
            )
        return random.sample(self._questions, k=n)

class ScoreBoard:
    def __init__(self, path: str = LEADERBOARD_PATH) -> None:
        self._path = Path(path)
        self._data: dict[str, dict[str, int]] = {}

        if self._path.exists():
            try:
                with open(self._path, encoding="utf-8") as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, OSError):
                # 🆕 رده‌بندیِ خراب، دلیلِ خوبی برای مُردنِ بازی نیست: از نو شروع می‌کنیم.
                self._data = {}

    def is_empty(self) -> bool:
        return not self._data

    def record(self, winner, player1, score1, player2, score2) -> None:
        for name, points in [(player1, score1), (player2, score2)]:
            if name not in self._data:
                self._data[name] = {"wins": 0, "points": 0}
            self._data[name]["points"] += points

        if winner is not None:
            self._data[winner]["wins"] += 1

        self._save()

    def top(self, n: int = 5) -> list[tuple[str, dict[str, int]]]:
        def wins_then_points(item):
            return item[1]["wins"], item[1]["points"]

        return sorted(self._data.items(), key=wins_then_points, reverse=True)[:n]

    def _save(self) -> None:
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)