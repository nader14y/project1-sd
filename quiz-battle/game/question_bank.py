"""بانک سؤال — سؤال‌ها را از فایل JSON می‌خواند و برای هر مسابقه انتخاب می‌کند."""

import json
import random
from pathlib import Path

from config import QUESTIONS_PATH, ROUNDS
from game.question import Question


class QuestionBank:
    """مجموعه‌ی سؤال‌های بازی."""

    def __init__(self, path: str | Path = QUESTIONS_PATH):
        """بانک را از فایل JSON می‌خواند و همان لحظه اعتبارسنجی می‌کند.

        Raises:
            FileNotFoundError: اگر فایل بانک سؤال پیدا نشود.
            ValueError: اگر فایل خراب باشد یا سؤالی قالب درست نداشته باشد.
        """
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"بانک سؤال پیدا نشد: {self.path}")

        try:
            with open(self.path, encoding="utf-8") as f:
                raw = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"فایل بانک سؤال خراب است ({self.path}): {e}") from e

        if not isinstance(raw, list) or not raw:
            raise ValueError("بانک سؤال باید یک لیست غیرخالی باشد")

        self._questions: list[Question] = []
        for i, item in enumerate(raw, start=1):
            try:
                self._questions.append(
                    Question(
                        text=item["text"],
                        options=item["options"],
                        correct=item["correct"],
                        power_up=item.get("power_up"),
                        category=item.get("category", "general"),
                    )
                )
            except (KeyError, TypeError, ValueError) as e:
                raise ValueError(f"سؤال شماره‌ی {i} در بانک ایراد دارد: {e}") from e

        if len(self._questions) < ROUNDS:
            raise ValueError(f"بانک سؤال باید حداقل {ROUNDS} سؤال داشته باشد")

    # ------------------------------------------------------------------ انتخاب

    def __len__(self) -> int:
        return len(self._questions)

    @property
    def categories(self) -> list[str]:
        """دسته‌های موجود در بانک."""
        return sorted({q.category for q in self._questions})

    def pick(self, n: int = ROUNDS, category: str | None = None) -> list[Question]:
        """n سؤال برای یک مسابقه انتخاب می‌کند.

        حدوداً یکی از هر سه سؤال قدرت ویژه دارد (قانون ۳ محصول).

        Raises:
            ValueError: اگر بانک به اندازه‌ی کافی سؤال نداشته باشد.
        """
        pool = self._questions
        if category:
            pool = [q for q in pool if q.category == category]
        if len(pool) < n:
            raise ValueError(f"بانک فقط {len(pool)} سؤال مناسب دارد، اما {n} تا لازم است")

        powered = [q for q in pool if q.power_up]
        plain = [q for q in pool if not q.power_up]

        want_powered = min(round(n / 3), len(powered))
        want_plain = n - want_powered
        if want_plain > len(plain):                 # بانک ساده کم داشت
            want_plain = len(plain)
            want_powered = n - want_plain

        chosen = random.sample(powered, want_powered) + random.sample(plain, want_plain)
        random.shuffle(chosen)
        return chosen

    def demo_set(self) -> list[Question]:
        """یک مسابقه‌ی از پیش‌چیده‌شده برای دموی کلاس.

        تصادفی‌بودن دشمن دموست: ترتیب طوری است که هر سه قدرت ویژه دیده شود
        (سپر قبل از سرقت می‌آید تا کار کردنش روی پرده معلوم شود).
        """
        wanted = [None, "shield", "steal", "double", None]
        used: set[int] = set()
        chosen: list[Question] = []

        for power_up in wanted:
            for idx, q in enumerate(self._questions):
                if idx not in used and q.power_up == power_up:
                    chosen.append(q)
                    used.add(idx)
                    break

        # اگر بانک قدرت ویژه‌ی لازم را نداشت، با سؤال‌های باقی‌مانده کامل می‌کنیم
        for idx, q in enumerate(self._questions):
            if len(chosen) >= ROUNDS:
                break
            if idx not in used:
                chosen.append(q)
                used.add(idx)

        return chosen[:ROUNDS]
