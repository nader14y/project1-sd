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
        return choice.strip().upper() == self.correct
        
    def correct_text(self):
        return self.options["ABCD".index(self.correct)]

class Match:
    def __init__(self, player1, player2, questions):
        if player1 == player2:
            raise ValueError("Unique Name per Player!")
        
        self.palyers = [player1, player2]
        self.questions = questions
        self.scores = {player1:0 , player2:0}
        self.round = 0
        self.answers = {}

    def start_round(self):
        self.round += 1
        self.answers = {}
        return self.questions[self.round - 1]

    def submit(self, player, choice, elapsed):
        self.answers[player] = (choice, elapsed)

    def resolve_round(self):
        question = self.questions[self.round - 1]
        
        for player in self.palyers:
            choice, elapsed = self.answers[player]
            if elapsed > 30:
                self.scores[player] += 0    
            elif question.is_correct(choice):
                self.scores[player] += 10

    def is_over(self):
        return self.round > 5

    def winner(self):
        player1, player2 = self.palyers
        if self.scores[player1] == self.scores[player2]:
            return None
        
        if self.scores[player1] > self.scores[player2]:
            return player1
        else:
            return player2
