import json
import copy
import logging
import os
import random
import sys
import tempfile
from pathlib import Path

from engine import Question, ROUNDS

logger = logging.getLogger("quiz.web.storage")


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
            if not isinstance(item, dict):
                raise ValueError("هر سؤال باید یک شیء JSON باشد")
            if not isinstance(item.get("text"), str) or not item["text"].strip():
                raise ValueError("متن سؤال نباید خالی باشد")
            options = item.get("options")
            if not isinstance(options, list) or any(
                not isinstance(option, str) or not option.strip() for option in options
            ):
                raise ValueError("گزینه‌ها باید فهرستی از متن‌های غیرخالی باشند")
            if item.get("power_up") not in (None, "double"):
                raise ValueError("نوع امتیاز ویژه معتبر نیست")
            if "correct" not in item:
                raise ValueError("پاسخ درست سؤال مشخص نشده است")
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
                if not isinstance(self._data, dict) or any(
                    not isinstance(name, str) or not isinstance(stat, dict)
                    or any(type(stat.get(key)) is not int or stat[key] < 0 for key in ("wins", "points"))
                    for name, stat in self._data.items()
                ):
                    raise ValueError("Invalid leaderboard schema")
            except (ValueError, OSError):
                # رده‌بندیِ خراب، دلیلِ خوبی برای مُردنِ بازی نیست: از نو شروع می‌کنیم
                logger.warning("Could not read leaderboard; starting empty", exc_info=True)
                self._data = {}

    def is_empty(self) -> bool:
        return not self._data

    def record(self, winner, player1, score1, player2, score2) -> None:
        previous = copy.deepcopy(self._data)
        for name, points in [(player1, score1), (player2, score2)]:
            if name not in self._data:
                self._data[name] = {"wins": 0, "points": 0}
            self._data[name]["points"] += points

        if winner is not None:
            self._data[winner]["wins"] += 1

        try:
            self._save()
        except OSError:
            self._data = previous
            raise

    def top(self, n: int = 5) -> list[tuple[str, dict[str, int]]]:
        def wins_then_points(item):
            return item[1]["wins"], item[1]["points"]

        return sorted(self._data.items(), key=wins_then_points, reverse=True)[:n]

    def _save(self) -> None:
        # Same-directory atomic replacement preserves the previous file on failure.
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self._path.parent,
                                             prefix=".leaderboard-", suffix=".tmp", delete=False) as f:
                temporary = Path(f.name)
                json.dump(self._data, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temporary, self._path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
