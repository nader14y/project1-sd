ROUNDS = 5          # هر مسابقه چند راند
TIME_LIMIT = 30     # مهلت هر جواب، به ثانیه
POINTS = 10         # امتیاز جواب درست
SPEED_BONUS = 3     # بونوس سریع‌ترین درست‌جواب


class Question:
    def __init__(self, text, options, correct, power_up=None):
        if len(options) != 4:
            raise ValueError("هر سؤال باید دقیقاً ۴ گزینه داشته باشد.")

        correct = str(correct).strip().upper()
        if correct not in ("A", "B", "C", "D"):
            raise ValueError(f"جواب درست باید A تا D باشد، نه {correct!r}")

        self.text = text
        self.options = options
        self.correct = correct
        self.power_up = power_up

    def is_correct(self, choice):
        return str(choice).strip().upper() == self.correct

    def correct_text(self):
        return self.options["ABCD".index(self.correct)]


class RoundResult:
    def __init__(self, status, points):
        self.status = status        # "correct" یا "wrong" یا "too_late"
        self.points = points


class Match:
    def __init__(self, player1, player2, questions):
        if player1 == player2:
            raise ValueError("Unique Name per Player!")

        if len(questions) < ROUNDS:
            raise ValueError(f"هر مسابقه به {ROUNDS} سؤال نیاز دارد.")

        self.players = [player1, player2]
        self.questions = questions
        self.scores = {player1: 0, player2: 0}
        self.round = 0
        self.answers = {}

    def start_round(self):
        if self.round >= len(self.questions):
            return None

        self.round += 1
        self.answers = {}
        return self.questions[self.round - 1]

    def score_of(self, player):
        return self.scores[player]

    def submit(self, player, choice, elapsed):
        if player not in self.players:
            raise ValueError(f"Unknown player: {player}")

        self.answers[player] = (choice, elapsed)

    def resolve_round(self):
        if self.round == 0:
            return {}

        question = self.questions[self.round - 1]
        results = {}
        correct_players = []

        # ۱) درست بود، غلط بود، یا دیر؟
        for player in self.players:
            if player not in self.answers:
                continue

            choice, elapsed = self.answers[player]
            if elapsed > TIME_LIMIT:
                results[player] = RoundResult("too_late", 0)
            elif question.is_correct(choice):
                results[player] = RoundResult("correct", POINTS)
                correct_players.append(player)
            else:
                results[player] = RoundResult("wrong", 0)

        # ۲) بونوس سرعت: بین درست‌جواب‌ها، سریع‌ترین
        if correct_players:
            fastest = min(correct_players, key=lambda p: self.answers[p][1])
            results[fastest].points += SPEED_BONUS

        # ۳) سؤال دوبل: امتیاز درست‌جواب‌ها دو برابر
        if question.power_up == "double":
            for player in correct_players:
                results[player].points *= 2

        # ۴) امتیازها را جمع کن
        for player, result in results.items():
            self.scores[player] += result.points

        return results

    def is_over(self):
        return self.round >= len(self.questions)

    def winner(self):
        player1, player2 = self.players
        if self.scores[player1] == self.scores[player2]:
            return None

        if self.scores[player1] > self.scores[player2]:
            return player1
        return player2