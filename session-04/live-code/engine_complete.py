"""مغز بازی — قواعد و امتیازدهی.  ✅ وضعیت مطلوب پایان جلسه‌ی ۴

⚠️ قانون معماری دوره: این فایل هیچ print و هیچ input ندارد. هرگز.
⚠️ و هیچ‌وقت خودش زمان را نمی‌خواند؛ زمان از بیرون به آن داده می‌شود.
   فعلاً بگویید «قانون است». جلسه‌ی ۷ می‌فهمند چرا — و آن لحظه، قله‌ی دوره است.

📌 اسم فایل سر کلاس: engine.py
"""

ROUNDS = 5          # هر مسابقه چند راند
TIME_LIMIT = 30     # مهلت هر جواب، به ثانیه
POINTS = 10         # امتیاز جواب درست
SPEED_BONUS = 3     # بونوس سریع‌ترین درست‌جواب


class Question:
    """یک سؤال چهارگزینه‌ای."""

    def __init__(self, text, options, correct):
        self.text = text
        self.options = options      # ۴ گزینه، به ترتیب A تا D
        self.correct = correct      # "A" یا "B" یا "C" یا "D"

    def is_correct(self, choice):
        return choice.strip().upper() == self.correct

    def correct_text(self):
        """متن گزینه‌ی درست — برای نمایش «جواب درست: A) توکیو»"""
        return self.options["ABCD".index(self.correct)]


class Match:
    """یک مسابقه‌ی ۵ راندی بین دو بازیکن."""

    def __init__(self, player1, player2, questions):
        if player1 == player2:
            raise ValueError("نام دو بازیکن نمی‌تواند یکی باشد")

        self.players = [player1, player2]
        self.questions = questions
        self.scores = {player1: 0, player2: 0}
        self.round = 0              # ۰ یعنی هنوز شروع نشده
        self.answers = {}           # نام بازیکن → (گزینه، ثانیه)

    def start_round(self):
        self.round += 1
        self.answers = {}
        return self.questions[self.round - 1]

    def submit(self, player, choice, elapsed):
        """جواب یک بازیکن را ثبت می‌کند. elapsed = چند ثانیه طول کشید."""
        self.answers[player] = (choice, elapsed)

    def resolve_round(self):
        """راند را حل می‌کند: امتیازدهی + بونوس سرعت.

        ⚠️ اینجا هیچ print نمی‌کنیم — فقط نتیجه را برمی‌گردانیم.
           جمله‌سازی و رنگ، کار فایل game.py است.
        """
        question = self.questions[self.round - 1]
        results = {}
        correct_players = []

        # ۱) درست بود، غلط بود، یا دیر؟
        for player in self.players:
            choice, elapsed = self.answers[player]

            if elapsed > TIME_LIMIT:
                results[player] = {"status": "too_late", "points": 0}
            elif question.is_correct(choice):
                results[player] = {"status": "correct", "points": POINTS}
                correct_players.append(player)
            else:
                results[player] = {"status": "wrong", "points": 0}

        # ۲) بونوس سرعت: بین درست‌جواب‌ها، سریع‌ترین
        if correct_players:
            fastest = correct_players[0]
            for player in correct_players:
                if self.answers[player][1] < self.answers[fastest][1]:
                    fastest = player
            results[fastest]["points"] += SPEED_BONUS

        # ۳) امتیازها را جمع کن
        for player in self.players:
            self.scores[player] += results[player]["points"]

        return results

    def is_over(self):
        return self.round >= ROUNDS

    def winner(self):
        """برنده، یا None اگر مساوی شده باشد."""
        player1, player2 = self.players
        if self.scores[player1] == self.scores[player2]:
            return None
        if self.scores[player1] > self.scores[player2]:
            return player1
        return player2


# ─────────────────────────────────────────────────────────────────────
# 🎁 بخش کششی (دقیقه‌ی ۸۰ تا ۸۵، اگر وقت بود) — ⚡ سؤال دوبل
#
# ۱) به Question یک ویژگی چهارم بدهید:
#        def __init__(self, text, options, correct, power_up=None):
#            ...
#            self.power_up = power_up        # None یا "double"
#
# ۲) در resolve_round، بین مرحله‌ی ۲ و ۳ این را اضافه کنید:
#        if question.power_up == "double":
#            for player in correct_players:
#                results[player]["points"] *= 2
#
# ۳) در game.py به یکی از سؤال‌ها power_up بدهید:
#        Question("...", [...], "C", "double")
#
# همین. سه تغییر کوچک، و بچه‌ها می‌بینند که موتورِ تمیز، اضافه‌کردن قابلیت را آسان می‌کند.
#
# 🎯 سرقت → تمرین خانه.  🛡️ قابلیت امضای تیم → جلسه‌ی ۶.
#
# 💡 مسیر پیشرفته برای تیم‌های سریع: حلقه‌ی پیدا کردن سریع‌ترین را
#    با یک خط بنویسند:  fastest = min(correct_players, key=lambda p: self.answers[p][1])
