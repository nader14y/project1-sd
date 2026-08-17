"""یک سؤال بازی — می‌داند متنش چیست و کدام گزینه درست است."""

from config import LETTERS, POWER_UPS


class Question:
    """یک سؤال چهارگزینه‌ای، همراه با قدرت ویژه‌ی احتمالی‌اش."""

    def __init__(
        self,
        text: str,
        options: list[str],
        correct: str,
        power_up: str | None = None,
        category: str = "general",
    ):
        """یک سؤال می‌سازد و اعتبار داده‌هایش را همان لحظه بررسی می‌کند.

        Args:
            text: متن سؤال.
            options: دقیقاً ۴ گزینه، به ترتیب A تا D.
            correct: حرف گزینه‌ی درست ("A" تا "D").
            power_up: None یا یکی از کلیدهای POWER_UPS.
            category: دسته‌ی موضوعی سؤال.

        Raises:
            ValueError: اگر تعداد گزینه‌ها، حرف درست یا قدرت ویژه معتبر نباشد.
        """
        if not text.strip():
            raise ValueError("متن سؤال نمی‌تواند خالی باشد")
        if len(options) != 4:
            raise ValueError(f"هر سؤال باید دقیقاً ۴ گزینه داشته باشد: {text!r}")
        if correct not in LETTERS:
            raise ValueError(f"گزینه‌ی درست باید A تا D باشد، نه {correct!r}: {text!r}")
        if power_up is not None and power_up not in POWER_UPS:
            raise ValueError(f"قدرت ویژه‌ی ناشناس {power_up!r}: {text!r}")

        self.text = text
        self.options = options          # به ترتیب A, B, C, D
        self.correct = correct          # "A" | "B" | "C" | "D"
        self.power_up = power_up        # None | "double" | "steal" | "shield"
        self.category = category

    def is_correct(self, choice: str) -> bool:
        """آیا این انتخاب، جواب درست است؟ (به بزرگی/کوچکی حرف و فاصله حساس نیست)"""
        return choice.strip().upper() == self.correct

    @property
    def correct_option(self) -> str:
        """متن گزینه‌ی درست."""
        return self.options[LETTERS.index(self.correct)]

    def __repr__(self) -> str:
        return f"<Question {self.text[:28]!r} correct={self.correct} power_up={self.power_up}>"
