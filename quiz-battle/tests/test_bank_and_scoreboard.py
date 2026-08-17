"""تست‌های بانک سؤال و رده‌بندی — با فایل موقت، بدون دست‌زدن به داده‌ی واقعی."""

import json

import pytest

from config import ROUNDS
from game.question_bank import QuestionBank
from storage.scoreboard import ScoreBoard

SAMPLE = [
    {"text": "سؤال ۱", "options": ["a", "b", "c", "d"], "correct": "A", "power_up": None},
    {"text": "سؤال ۲", "options": ["a", "b", "c", "d"], "correct": "B", "power_up": "double"},
    {"text": "سؤال ۳", "options": ["a", "b", "c", "d"], "correct": "C", "power_up": "steal"},
    {"text": "سؤال ۴", "options": ["a", "b", "c", "d"], "correct": "D", "power_up": "shield"},
    {"text": "سؤال ۵", "options": ["a", "b", "c", "d"], "correct": "A", "power_up": None},
    {"text": "سؤال ۶", "options": ["a", "b", "c", "d"], "correct": "B", "power_up": None},
]


def write_bank(tmp_path, data):
    path = tmp_path / "questions.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


# ─────────────────────────────────────────────────────────── بانک سؤال


def test_bank_loads_and_picks(tmp_path):
    bank = QuestionBank(write_bank(tmp_path, SAMPLE))
    assert len(bank) == len(SAMPLE)
    picked = bank.pick(ROUNDS)
    assert len(picked) == ROUNDS
    assert len({q.text for q in picked}) == ROUNDS      # بدون تکرار


def test_bank_reports_the_broken_question_number(tmp_path):
    broken = [dict(SAMPLE[0]), {"text": "خراب", "options": ["a"], "correct": "A"}]
    with pytest.raises(ValueError, match="شماره‌ی 2"):
        QuestionBank(write_bank(tmp_path, broken))


def test_missing_bank_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        QuestionBank(tmp_path / "nope.json")


def test_demo_set_is_deterministic_and_ordered(tmp_path):
    bank = QuestionBank(write_bank(tmp_path, SAMPLE))
    first, second = bank.demo_set(), bank.demo_set()
    assert [q.text for q in first] == [q.text for q in second]
    assert [q.power_up for q in first] == [None, "shield", "steal", "double", None]


# ─────────────────────────────────────────────────────────── رده‌بندی


def test_scoreboard_persists_between_runs(tmp_path):
    path = tmp_path / "leaderboard.json"
    ScoreBoard(path).record_result("علی", "علی", 40, "رضا", 25)

    reloaded = ScoreBoard(path)                          # مثل بستن و بازکردن بازی
    top = dict(reloaded.top())
    assert top["علی"]["wins"] == 1
    assert top["علی"]["points"] == 40
    assert top["رضا"]["wins"] == 0
    assert top["رضا"]["points"] == 25


def test_draw_is_recorded_for_both(tmp_path):
    board = ScoreBoard(tmp_path / "leaderboard.json")
    board.record_result(None, "علی", 30, "رضا", 30)
    top = dict(board.top())
    assert top["علی"]["draws"] == 1 and top["رضا"]["draws"] == 1
    assert top["علی"]["wins"] == 0 and top["رضا"]["wins"] == 0


def test_top_sorts_by_wins_then_points(tmp_path):
    board = ScoreBoard(tmp_path / "leaderboard.json")
    board.record_result("علی", "علی", 20, "رضا", 10)
    board.record_result("رضا", "رضا", 90, "مریم", 5)
    board.record_result("علی", "علی", 20, "مریم", 5)
    assert [name for name, _ in board.top()] == ["علی", "رضا", "مریم"]


def test_broken_leaderboard_does_not_kill_the_game(tmp_path):
    path = tmp_path / "leaderboard.json"
    path.write_text("}{ این JSON خراب است", encoding="utf-8")
    assert ScoreBoard(path).is_empty()
