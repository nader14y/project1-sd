"""موتور Quiz Battle — قواعد بازی، امتیازدهی و قدرت‌های ویژه.

⚠️ قانون معماری دوره (جلسه‌ی ۴): این فایل هیچ print و input ندارد. هرگز.
   زمان هم هیچ‌وقت از داخل خوانده نمی‌شود؛ همیشه از بیرون تزریق می‌شود.
   همین دو تصمیم است که تست‌نویسی جلسه‌ی ۷ را ممکن می‌کند.
"""

from config import (
    DOUBLE_MULTIPLIER,
    POINTS_CORRECT,
    ROUNDS,
    SPEED_BONUS,
    STEAL_AMOUNT,
    TIME_LIMIT,
)
from game.question import Question


class Match:
    """یک مسابقه‌ی ۵ راندی بین دو بازیکن.

    می‌داند: بازیکن‌ها، راند جاری، امتیازها، سپرها و جواب‌های راند.
    می‌کند: راند را شروع می‌کند، جواب می‌گیرد، و راند را با قواعد بازی حل می‌کند.
    """

    def __init__(self, player1: str, player2: str, questions: list[Question]):
        """یک مسابقه‌ی تازه می‌سازد.

        Raises:
            ValueError: نام خالی، نام‌های یکسان، یا سؤال کم‌تر از تعداد راندها.
        """
        player1, player2 = player1.strip(), player2.strip()
        if not player1 or not player2:
            raise ValueError("نام بازیکن نمی‌تواند خالی باشد")
        if player1 == player2:
            raise ValueError("نام دو بازیکن نمی‌تواند یکی باشد")
        if len(questions) < ROUNDS:
            raise ValueError(f"برای یک مسابقه حداقل {ROUNDS} سؤال لازم است")

        self.players = [player1, player2]
        self.questions = questions
        self.scores: dict[str, int] = {player1: 0, player2: 0}
        self.shields: dict[str, int] = {player1: 0, player2: 0}
        self.round = 0                                      # ۰ یعنی هنوز شروع نشده
        self.history: list[dict] = []                       # نتیجه‌ی همه‌ی راندها
        self._answers: dict[str, tuple[str, float]] = {}    # بازیکن → (گزینه، ثانیه)

    # ------------------------------------------------------------------ راند

    def start_round(self) -> Question:
        """راند بعدی را شروع می‌کند و سؤالش را برمی‌گرداند.

        Raises:
            ValueError: اگر مسابقه تمام شده باشد.
        """
        if self.is_over():
            raise ValueError("مسابقه تمام شده است")
        self.round += 1
        self._answers = {}
        return self.current_question

    @property
    def current_question(self) -> Question:
        """سؤال راند جاری."""
        if self.round == 0:
            raise ValueError("هنوز هیچ راندی شروع نشده است")
        return self.questions[self.round - 1]

    def submit(self, player: str, choice: str, elapsed: float) -> None:
        """جواب یک بازیکن به سؤال جاری را ثبت می‌کند.

        Args:
            player: نام بازیکن (باید عضو مسابقه باشد).
            choice: گزینه‌ی انتخابی ("A" تا "D").
            elapsed: مدت پاسخ‌گویی به ثانیه — برای مهلت و بونوس سرعت.

        Raises:
            ValueError: اگر بازیکن عضو مسابقه نباشد یا قبلاً جواب داده باشد.
        """
        if player not in self.players:
            raise ValueError("این بازیکن عضو مسابقه نیست")
        if player in self._answers:
            raise ValueError("این بازیکن قبلاً جواب داده است")
        self._answers[player] = (choice, elapsed)

    @property
    def waiting_for(self) -> list[str]:
        """بازیکن‌هایی که هنوز جواب نداده‌اند."""
        return [p for p in self.players if p not in self._answers]

    # ---------------------------------------------------------------- امتیاز

    def resolve_round(self) -> dict:
        """راند را حل می‌کند: امتیازدهی، بونوس سرعت و اعمال قدرت ویژه.

        Returns:
            یک dict وضعیت — نه جمله‌ی فارسی و نه چاپ. جمله‌سازی و رنگ،
            کار لایه‌ی نمایش است.

        Raises:
            ValueError: اگر هنوز هر دو بازیکن جواب نداده باشند.
        """
        if self.waiting_for:
            raise ValueError("هنوز هر دو بازیکن جواب نداده‌اند")

        question = self.current_question
        results: dict[str, dict] = {}
        correct_players: list[str] = []

        # ۱) درست، غلط، یا دیرهنگام؟
        for player in self.players:
            choice, elapsed = self._answers[player]
            row = {
                "choice": choice.strip().upper(),
                "elapsed": elapsed,
                "points": 0,
                "speed_bonus": 0,
                "doubled": False,
                "stole": 0,
                "lost_to_steal": 0,
                "shield_used": False,
                "shield_gained": False,
            }
            if elapsed > TIME_LIMIT:
                row["status"] = "too_late"
            elif question.is_correct(choice):
                row["status"] = "correct"
                row["points"] = POINTS_CORRECT
                correct_players.append(player)
            else:
                row["status"] = "wrong"
            results[player] = row

        # ۲) بونوس سرعت: بین درست‌جواب‌ها، سریع‌ترین
        if correct_players:
            fastest = min(correct_players, key=lambda p: self._answers[p][1])
            results[fastest]["speed_bonus"] = SPEED_BONUS
            results[fastest]["points"] += SPEED_BONUS

        # ۳) ⚡ دوبل: کل امتیاز راند (شامل بونوس سرعت) دو برابر می‌شود
        if question.power_up == "double":
            for player in correct_players:
                results[player]["points"] *= DOUBLE_MULTIPLIER
                results[player]["doubled"] = True

        for player in correct_players:
            self.scores[player] += results[player]["points"]

        # ۴) 🎯 سرقت: هم‌زمان حساب می‌شود تا ترتیب بازیکن‌ها اثری نگذارد
        if question.power_up == "steal" and correct_players:
            losses: dict[str, int] = {}
            for player in correct_players:
                rival = self.rival_of(player)
                if self.shields[rival] > 0:
                    self.shields[rival] -= 1
                    results[rival]["shield_used"] = True
                    continue
                losses[rival] = losses.get(rival, 0) + STEAL_AMOUNT
                results[player]["stole"] += STEAL_AMOUNT
            for rival, amount in losses.items():
                taken = min(amount, self.scores[rival])   # هرگز زیر صفر
                self.scores[rival] -= taken
                results[rival]["lost_to_steal"] = taken

        # ۵) 🛡️ سپر (قابلیت امضای این نسخه): درست‌جواب یک سپر می‌گیرد
        if question.power_up == "shield":
            for player in correct_players:
                self.shields[player] += 1
                results[player]["shield_gained"] = True

        summary = {
            "round": self.round,
            "question": question,
            "results": results,
            "scores": dict(self.scores),
            "shields": dict(self.shields),
        }
        self.history.append(summary)
        return summary

    # ----------------------------------------------------------------- پایان

    def rival_of(self, player: str) -> str:
        """حریفِ این بازیکن."""
        return self.players[1] if player == self.players[0] else self.players[0]

    def is_over(self) -> bool:
        """آیا هر ۵ راند بازی شده است؟"""
        return self.round >= ROUNDS

    def winner(self) -> str | None:
        """برنده، یا None اگر مساوی شده باشد."""
        p1, p2 = self.players
        if self.scores[p1] == self.scores[p2]:
            return None
        return p1 if self.scores[p1] > self.scores[p2] else p2

    def standings(self) -> list[tuple[str, int]]:
        """بازیکن‌ها به ترتیب امتیاز، از بیشترین به کمترین."""
        return sorted(self.scores.items(), key=lambda kv: kv[1], reverse=True)
