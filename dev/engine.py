ROUNDS = 5          # هر مسابقه چند راند
TIME_LIMIT = 30     # مهلت هر جواب، به ثانیه
POINTS = 10         # امتیاز جواب درست
SPEED_BONUS = 3     # بونوس سریع‌ترین درست‌جواب

class Question:
    def __init__(self, text, options, correct):
        # TODO: سه ویژگی را روی self بگذار
        pass

    def is_correct(self, choice):
        """آیا این انتخاب درست است؟ (به بزرگی/کوچکی حرف و فاصله حساس نیست)"""
        # TODO: choice را تمیز کن و با self.correct مقایسه کن
        pass

    def correct_text(self):
        """متن گزینه‌ی درست — برای نمایش «جواب درست: A) توکیو»"""
        # TODO: از "ABCD".index(self.correct) استفاده کن
        pass


class Match:
    def __init__(self, player1, player2, questions):
        # TODO: اگر نام دو بازیکن یکی بود، خطا بده:
        #       raise ValueError("نام دو بازیکن نمی‌تواند یکی باشد")
        # TODO: players, questions, scores, round, answers را بساز
        pass

    def start_round(self):
        """راند بعدی را شروع می‌کند و سؤالش را برمی‌گرداند."""
        # TODO: یکی به round اضافه کن، answers را خالی کن،
        #       و سؤال این راند را برگردان
        pass

    def submit(self, player, choice, elapsed):
        """جواب یک بازیکن را ثبت می‌کند. elapsed = چند ثانیه طول کشید."""
        # TODO: در answers ذخیره کن
        pass

    def resolve_round(self):
        # TODO مرحله ۱: برای هر بازیکن مشخص کن درست بود، غلط بود، یا دیر
        # TODO مرحله ۲: بین درست‌جواب‌ها، سریع‌ترین را پیدا کن و بونوس بده
        # TODO مرحله ۳: امتیازها را به scores اضافه کن
        # TODO مرحله ۴: results را برگردان
        pass

    def is_over(self):
        """آیا هر ۵ راند بازی شده است؟"""
        # TODO
        pass

    def winner(self):
        """برنده، یا None اگر مساوی شده باشد."""
        # TODO
        pass
