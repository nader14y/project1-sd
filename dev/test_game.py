import pytest

from engine import POINTS, Question
from game import play_match


def make_questions(n=2):
    return [Question("۲+۲ چند است؟", ["4", "5", "6", "7"], "A") for _ in range(n)]


def test_play_match_awards_points_and_picks_a_winner(monkeypatch):
    answers = iter(["A", "", "B", "A", "", "B"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers))
    monkeypatch.setattr("game.time.perf_counter", lambda: 0.0)

    match = play_match("علی", "رضا", make_questions(2))

    assert match.is_over()
    assert match.scores["علی"] == POINTS * 2
    assert match.scores["رضا"] == 0
    assert match.winner() == "علی"


def test_play_match_rejects_same_names():
    with pytest.raises(ValueError):
        play_match("علی", "علی", make_questions(1))
