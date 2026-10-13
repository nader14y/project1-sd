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

def test_bank_reads_every_question_from_the_file(tmp_path):
    bank = make_bank(tmp_path)
    assert bank.count() == 8


def test_bank_reads_the_power_up_too(tmp_path):
    bank = make_bank(tmp_path)
    assert any(q.power_up == "double" for q in bank.pick(8))


def test_picked_questions_are_never_repeated(tmp_path):
    bank = make_bank(tmp_path)
    picked = bank.pick(5)
    assert len({q.text for q in picked}) == 5


def test_picking_more_than_the_bank_has_is_refused(tmp_path):
    import pytest
    bank = make_bank(tmp_path)
    with pytest.raises(ValueError):
        bank.pick(99)

def test_a_new_scoreboard_is_empty(tmp_path):
    board = ScoreBoard(str(tmp_path / "leaderboard.json"))
    assert board.is_empty()


def test_the_leaderboard_survives_a_restart(tmp_path):
    path = str(tmp_path / "leaderboard.json")

    board = ScoreBoard(path)
    board.record("سارا", "علی", 30, "سارا", 39)

    again = ScoreBoard(path)                  # انگار برنامه بسته و دوباره باز شد
    assert not again.is_empty()
    assert dict(again.top(5))["سارا"] == {"wins": 1, "points": 39}
    assert dict(again.top(5))["علی"] == {"wins": 0, "points": 30}


def test_points_add_up_across_matches(tmp_path):
    path = str(tmp_path / "leaderboard.json")
    board = ScoreBoard(path)
    board.record("علی", "علی", 20, "رضا", 10)
    board.record("علی", "علی", 15, "رضا", 30)

    assert dict(board.top(5))["علی"] == {"wins": 2, "points": 35}


def test_a_draw_gives_points_but_no_win(tmp_path):
    board = ScoreBoard(str(tmp_path / "leaderboard.json"))
    board.record(None, "علی", 12, "رضا", 12)

    assert dict(board.top(5))["علی"] == {"wins": 0, "points": 12}
    assert dict(board.top(5))["رضا"] == {"wins": 0, "points": 12}


def test_top_sorts_by_wins_then_points(tmp_path):
    board = ScoreBoard(str(tmp_path / "leaderboard.json"))
    board.record("سارا", "سارا", 10, "علی", 90)      # سارا ۱ برد، علی امتیاز بیشتر
    board.record(None, "رها", 5, "علی", 5)

    assert [name for name, _ in board.top(5)] == ["سارا", "علی", "رها"]


def test_persian_names_stay_persian_in_the_file(tmp_path):
    path = tmp_path / "leaderboard.json"
    ScoreBoard(str(path)).record("سارا", "علی", 1, "سارا", 2)

    raw = path.read_text(encoding="utf-8")
    assert "سارا" in raw
    assert "\\u" not in raw
