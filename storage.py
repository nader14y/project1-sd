import json
import random
import sys
from pathlib import Path

from engine import Question, ROUNDS


def app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent      # کنار فایل exe
    return Path(__file__).parent                # کنار فایل پایتون

QUESTIONS_PATH = app_dir() / "questions.json"
LEADERBOARD_PATH = app_dir() / "leaderboard.json"

class QuestionBank:
    def __init__(self, path=QUESTIONS_PATH) -> None:
        if not Path(path).exists():
            raise FileNotFoundError(f"فایل questions.json پیدا نشد: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as error:
            # خطای خام را به خطایی ترجمه می‌کنیم که *شماره‌ی خط* را بگوید
            raise ValueError(
                f"فایل questions.json خراب است (خط {error.lineno}): {error.msg}"
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
    def __init__(self, path=LEADERBOARD_PATH) -> None:
        self._path = Path(path)
        self._data: dict[str, dict[str, int]] = {}

        if self._path.exists():
            try:
                with open(self._path, encoding="utf-8") as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, OSError):
                # رده‌بندیِ خراب، دلیلِ خوبی برای مُردنِ بازی نیست: از نو شروع می‌کنیم
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