ROUNDS = 5          # هر مسابقه چند راند
TIME_LIMIT = 30     # مهلت هر جواب، به ثانیه
POINTS = 10         # امتیاز جواب درست
SPEED_BONUS = 3     # بونوس سریع‌ترین درست‌جواب


class Question:
    def __init__(self, text, options, correct):
        self.text = text
        self.options = options
        self.correct = correct

    def is_correct(self, choice):
        return str(choice).strip().upper() == self.correct

    def correct_text(self):
        return self.options["ABCD".index(self.correct)]


class Match:
    def __init__(self, player1, player2, questions):
        if player1 == player2:
            raise ValueError("Unique Name per Player!")

        self.players = [player1, player2]
        self.scores = {player1: 0, player2: 0}
        self.round = 0
        self.answers = {}

    def start_round(self):
        if self.round >= len(self.questions):
            return None

        self.round += 1
        self.answers = {}
        return self.questions[self.round - 1]

    def submit(self, player, choice, elapsed):
        if player not in self.players:
            raise ValueError(f"Unknown player: {player}")

        self.answers[player] = (choice, elapsed)

    def resolve_round(self):
        if self.round == 0:
            return

        question = self.questions[self.round - 1]

        for player in self.players:
            if player not in self.answers:
                continue

            choice, elapsed = self.answers[player]
            if elapsed > TIME_LIMIT:
                continue
            if question.is_correct(choice):
                self.scores[player] += POINTS

    def is_over(self):
        return self.round >= ROUNDS

    def winner(self):
        player1, player2 = self.players
        if self.scores[player1] == self.scores[player2]:
            return None

        if self.scores[player1] > self.scores[player2]:
            return player1
        return player2
