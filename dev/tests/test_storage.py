import json

from storage import QuestionBank, ScoreBoard


SAMPLE = [
    {"text": f"سؤال {i}", "options": ["الف", "ب", "پ", "ت"],
     "correct": "B", "power_up": "double" if i == 1 else None, "category": "آزمایشی"}
    for i in range(1, 9)
]


def make_bank(tmp_path, items=None) -> QuestionBank:
    path = tmp_path / "questions.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items or SAMPLE, f, ensure_ascii=False, indent=2)
    return QuestionBank(str(path))

def test_a_new_scoreboard_is_empty(tmp_path):
    board = ScoreBoard(str(tmp_path / "leaderboard.json"))
    assert board.is_empty()
