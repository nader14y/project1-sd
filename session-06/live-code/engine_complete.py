"""🧠 مغز بازی — قواعد و امتیازدهی.  ✅ وضعیت شروع جلسه‌ی ۶

⚠️ قانون معماری دوره: این فایل هیچ print و هیچ input ندارد. هرگز.
⚠️ و هیچ‌وقت خودش زمان را نمی‌خواند؛ زمان از بیرون به آن داده می‌شود.
   فعلاً بگویید «قانون است». جلسه‌ی ۷ می‌فهمند چرا — و آن لحظه، قله‌ی دوره است.

📌 اسم فایل سر کلاس: engine.py

🆕 تنها فرق این فایل با پایان جلسه‌ی ۴: ویژگی power_up (همان بخش کششی ⚡ دوبل).
   اگر تیمی جلسه‌ی ۴ دوبل را نزده، امروز ۳ دقیقه‌ای اضافه‌اش می‌کند — چون
   قالب questions.json این ستون را دارد.

⚠️ امروز هیچ چیز دیگری در این فایل عوض نمی‌شود. موتور فایل نمی‌خواند و
   فایل نمی‌نویسد — این کارِ دفتردار (storage.py) است.
🐍 نیاز: پایتون ۳٫۱۰ یا بالاتر (به خاطر  str | None  و  list[str] )

دو چیزی که در این فایل رعایت شده و سر کلاس نامشان را می‌بریم:

  ۱) نوع داده (type hint):  کنار هر ورودی و خروجی نوشته‌ایم چه *جنسی* است.
     پایتون اجبار نمی‌کند؛ این‌ها برای *آدم* است و برای ویرایشگر. VS Code از
     همین‌ها راهنمایی و هشدار می‌سازد.

  ۲) کپسوله‌سازی:  چیزهایی که با «_» شروع می‌شوند مالِ خود کلاس‌اند و از بیرون
     دست نمی‌خورند. از بیرون فقط می‌توان *پرسید* (property و متدهای _of)،
     نمی‌توان *عوض کرد*. یعنی کسی نمی‌تواند تقلب کند و امتیازش را ۱۰۰۰ کند.
"""

ROUNDS: int = 5          # هر مسابقه چند راند
TIME_LIMIT: int = 30     # مهلت هر جواب، به ثانیه
POINTS: int = 10         # امتیاز جواب درست
SPEED_BONUS: int = 3     # بونوس سریع‌ترین درست‌جواب


class Question:
    """یک سؤال چهارگزینه‌ای — ساخته شد، دیگر عوض نمی‌شود."""

    def __init__(self, text: str, options: list[str], correct: str,
                 power_up: str | None = None) -> None:
        if len(options) != 4:
            raise ValueError("هر سؤال باید دقیقاً ۴ گزینه داشته باشد")
        if correct not in ["A", "B", "C", "D"]:
            raise ValueError("جواب درست باید یکی از A، B، C یا D باشد")

        self._text: str = text
        self._options: list[str] = list(options)   # کپی می‌گیریم، نه خودِ لیستِ بیرون
        self._correct: str = correct
        self._power_up: str | None = power_up   # None یا "double" یا "steal"

    # ── فقط خواندنی: از بیرون می‌شود پرسید، نمی‌شود عوض کرد ──

    @property
    def text(self) -> str:
        return self._text

    @property
    def options(self) -> list[str]:
        return list(self._options)                 # کپی، تا کسی از بیرون گزینه‌ها را عوض نکند

    @property
    def correct(self) -> str:
        return self._correct

    @property
    def power_up(self) -> str | None:
        return self._power_up

    # ── کارها ──

    def is_correct(self, choice: str) -> bool:
        return choice.strip().upper() == self._correct

    def correct_text(self) -> str:
        """متن گزینه‌ی درست — برای نمایش «جواب درست: A) توکیو»"""
        return self._options["ABCD".index(self._correct)]


class RoundResult:
    """نتیجه‌ی یک بازیکن در یک راند.

    قبلاً این یک dict بود: {"status": ..., "points": ...}
    قاعده: هر dict که کلیدهایش همیشه ثابت است، در واقع یک کلاس است.
    """

    def __init__(self, status: str, points: int) -> None:
        self._status: str = status                 # "correct" یا "wrong" یا "too_late"
        self._points: int = points

    @property
    def status(self) -> str:
        return self._status

    @property
    def points(self) -> int:
        return self._points

    def add_bonus(self, amount: int) -> None:
        """امتیاز اضافه — تنها راهِ مجاز برای عوض‌کردن points."""
        self._points += amount

    def double(self) -> None:
        """⚡ امتیاز این راند دو برابر می‌شود."""
        self._points *= 2


class Match:
    """یک مسابقه‌ی دونفره‌ی ۵ راندی."""

    def __init__(self, player1: str, player2: str, questions: list[Question]) -> None:
        if player1 == player2:
            raise ValueError("نام دو بازیکن نمی‌تواند یکی باشد")
        if len(questions) < ROUNDS:
            raise ValueError(f"برای {ROUNDS} راند، حداقل {ROUNDS} سؤال لازم است")

        self._players: list[str] = [player1, player2]
        self._questions: list[Question] = list(questions)
        self._scores: dict[str, int] = {player1: 0, player2: 0}
        self._round: int = 0                                   # ۰ یعنی هنوز شروع نشده
        self._answers: dict[str, tuple[str, float]] = {}       # نام → (گزینه، ثانیه)

    # ── پنجره‌های خواندنی به درون مسابقه ──

    @property
    def players(self) -> list[str]:
        return list(self._players)

    @property
    def round(self) -> int:
        return self._round

    def score_of(self, player: str) -> int:
        return self._scores[player]

    def answer_of(self, player: str) -> tuple[str, float]:
        """(گزینه‌ای که زد، چند ثانیه طول کشید)"""
        return self._answers[player]

    # ── کارها ──

    def start_round(self) -> Question:
        self._round += 1
        self._answers = {}
        return self._questions[self._round - 1]

    def submit(self, player: str, choice: str, elapsed: float) -> None:
        """جواب یک بازیکن را ثبت می‌کند. elapsed = چند ثانیه طول کشید."""
        if player not in self._scores:
            raise ValueError(f"بازیکنی به نام {player} در این مسابقه نیست")
        self._answers[player] = (choice, elapsed)

    def is_over(self) -> bool:
        return self._round >= ROUNDS

    def winner(self) -> str | None:
        """برنده، یا None اگر مساوی شده باشد."""
        player1, player2 = self._players
        if self._scores[player1] == self._scores[player2]:
            return None
        if self._scores[player1] > self._scores[player2]:
            return player1
        return player2

    def resolve_round(self) -> dict[str, RoundResult]:
        question = self._questions[self._round - 1]
        results: dict[str, RoundResult] = {}
        correct_players: list[str] = []

        # ۱) درست بود، غلط بود، یا دیر؟
        for player in self._players:
            choice, elapsed = self._answers[player]

            if elapsed > TIME_LIMIT:
                results[player] = RoundResult("too_late", 0)
            elif question.is_correct(choice):
                results[player] = RoundResult("correct", POINTS)
                correct_players.append(player)
            else:
                results[player] = RoundResult("wrong", 0)

        # ۲) بونوس سرعت: بین درست‌جواب‌ها، سریع‌ترین
        if correct_players:
            fastest = correct_players[0]
            for player in correct_players:
                if self._answers[player][1] < self._answers[fastest][1]:
                    fastest = player
            results[fastest].add_bonus(SPEED_BONUS)

        # ۲٫۵) ⚡ سؤال دوبل: امتیاز درست‌جواب‌ها دو برابر
        if question.power_up == "double":
            for player in correct_players:
                results[player].double()

        # ۳) امتیازها را جمع کن  ← اینجا، *داخل* موتور، مجاز است
        for player in self._players:
            self._scores[player] += results[player].points

        return results


# ─────────────────────────────────────────────────────────────────────
# 🎯 تمرین خانه‌ی جلسه‌ی ۴ (سرقت) اگر انجام شده، همین‌جا کنار دوبل می‌نشیند:
#
#        if question.power_up == "steal":
#            for player in correct_players:
#                rival = self.rival_of(player)
#                self._scores[rival] = max(0, self._scores[rival] - STEAL_AMOUNT)
#
# 🛡️ قابلیت امضای تیم‌ها → از امروز یک تصمیمِ *داده‌ای* است، نه کدی:
#    هر تیم در questions.json خودش انتخاب می‌کند کدام قدرت ویژه، امضای اوست.
