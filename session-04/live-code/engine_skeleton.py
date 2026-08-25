"""مغز بازی — قواعد و امتیازدهی.

⚠️ قانون معماری دوره: این فایل هیچ print و هیچ input ندارد. هرگز.
⚠️ و هیچ‌وقت خودش زمان را نمی‌خواند؛ زمان از بیرون به آن داده می‌شود.

📌 این اسکلت را بچه‌ها یک‌بار کپی می‌کنند و بدنه‌ی متدها را با هم پر می‌کنیم.
   نوشتن `def submit(self, player: str, choice: str, elapsed: float) -> None:`
   هیچ چیزی یاد نمی‌دهد — نوشتن منطق داخلش، همه‌چیز را.

🐍 نیاز: پایتون ۳٫۱۰ یا بالاتر

دو چیز در این اسکلت هست که تازه است — سر کلاس نامشان را می‌بریم:

  ۱) نوع داده (type hint):  `player: str` یعنی «اسم بازیکن یک رشته است».
     `-> bool` یعنی «این متد درست/غلط برمی‌گرداند». پایتون اجبار نمی‌کند؛
     این‌ها برای *آدم* است و برای VS Code، که با همین‌ها راهنمایی می‌دهد.

  ۲) کپسوله‌سازی:  هر چیزی که با «_» شروع شود مالِ خودِ کلاس است و از بیرون
     دست نمی‌خورد. برای خواندنش، «پنجره»های خواندنی گذاشته‌ایم — آن‌ها را
     از قبل برایتان نوشته‌ایم، چون تشریفات است و چیزی یاد نمی‌دهد.
"""

ROUNDS: int = 5          # هر مسابقه چند راند
TIME_LIMIT: int = 30     # مهلت هر جواب، به ثانیه
POINTS: int = 10         # امتیاز جواب درست
SPEED_BONUS: int = 3     # بونوس سریع‌ترین درست‌جواب


class Question:
    """یک سؤال چهارگزینه‌ای — ساخته شد، دیگر عوض نمی‌شود.

    می‌داند: متن (str)، ۴ گزینه (list[str])، جواب درست (str)
    می‌کند: می‌گوید یک انتخاب درست است یا نه (bool)
    """

    def __init__(self, text: str, options: list[str], correct: str) -> None:
        # TODO ۱: اگر تعداد گزینه‌ها ۴ نبود، خطا بده:
        #         raise ValueError("هر سؤال باید دقیقاً ۴ گزینه داشته باشد")
        # TODO ۲: اگر correct یکی از "A" تا "D" نبود، خطا بده
        # TODO ۳: سه ویژگی را با «_» روی self بگذار:  _text، _options، _correct
        #         (برای _options یک کپی بگیر:  list(options) )
        pass

    # ── پنجره‌های خواندنی (آماده — دست نزنید) ──

    @property
    def text(self) -> str:
        return self._text

    @property
    def options(self) -> list[str]:
        return list(self._options)

    @property
    def correct(self) -> str:
        return self._correct

    # ── کارها ──

    def is_correct(self, choice: str) -> bool:
        """آیا این انتخاب درست است؟ (به بزرگی/کوچکی حرف و فاصله حساس نیست)"""
        # TODO: choice را تمیز کن و با self._correct مقایسه کن
        pass

    def correct_text(self) -> str:
        """متن گزینه‌ی درست — برای نمایش «جواب درست: A) توکیو»"""
        # TODO: از "ABCD".index(self._correct) استفاده کن
        pass


class RoundResult:
    """نتیجه‌ی یک بازیکن در یک راند.

    🎓 این می‌توانست یک dict باشد: {"status": ..., "points": ...}
       ولی هر dict که کلیدهایش همیشه ثابت است، در واقع یک کلاس است.
    """

    def __init__(self, status: str, points: int) -> None:
        # TODO: _status و _points را بساز
        pass

    @property
    def status(self) -> str:
        return self._status

    @property
    def points(self) -> int:
        return self._points

    def add_bonus(self, amount: int) -> None:
        """امتیاز اضافه — تنها راهِ مجاز برای عوض‌کردن points."""
        # TODO: amount را به self._points اضافه کن
        pass


class Match:
    """یک مسابقه‌ی دونفره‌ی ۵ راندی."""

    def __init__(self, player1: str, player2: str, questions: list[Question]) -> None:
        # TODO ۱: اگر نام دو بازیکن یکی بود، خطا بده:
        #         raise ValueError("نام دو بازیکن نمی‌تواند یکی باشد")
        # TODO ۲: اگر تعداد سؤال‌ها از ROUNDS کمتر بود، خطا بده
        # TODO ۳: این پنج ویژگی را بساز (همه با «_»):
        #         _players : list[str]                     → [player1, player2]
        #         _questions : list[Question]              → کپیِ questions
        #         _scores : dict[str, int]                 → هر دو، صفر
        #         _round : int                             → ۰ (هنوز شروع نشده)
        #         _answers : dict[str, tuple[str, float]]  → خالی
        pass

    # ── پنجره‌های خواندنی (آماده — دست نزنید) ──

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
        """راند بعدی را شروع می‌کند و سؤالش را برمی‌گرداند."""
        # TODO: یکی به _round اضافه کن، _answers را خالی کن،
        #       و سؤال این راند را برگردان
        pass

    def submit(self, player: str, choice: str, elapsed: float) -> None:
        """جواب یک بازیکن را ثبت می‌کند. elapsed = چند ثانیه طول کشید."""
        # TODO ۱: اگر این بازیکن در این مسابقه نیست، ValueError بده
        # TODO ۲: در _answers ذخیره کن
        pass

    def resolve_round(self) -> dict[str, RoundResult]:
        # TODO مرحله ۱: برای هر بازیکن یک RoundResult بساز
        #               ("too_late" / "correct" / "wrong")
        # TODO مرحله ۲: بین درست‌جواب‌ها سریع‌ترین را پیدا کن → add_bonus(SPEED_BONUS)
        # TODO مرحله ۳: امتیازها را به _scores اضافه کن
        # TODO مرحله ۴: results را برگردان
        pass

    def is_over(self) -> bool:
        """آیا هر ۵ راند بازی شده است؟"""
        # TODO
        pass

    def winner(self) -> str | None:
        """برنده، یا None اگر مساوی شده باشد."""
        # TODO
        pass
