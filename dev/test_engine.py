import pytest

from engine import POINTS, TIME_LIMIT, Match, Question


def make_questions(n=2):
    return [Question("۲+۲ چند است؟", ["4", "5", "6", "7"], "A") for _ in range(n)]


def make_match(n=2):
    return Match("علی", "رضا", make_questions(n))


def play_round(match, choice1, elapsed1, choice2, elapsed2):
    match.start_round()
    match.submit("علی", choice1, elapsed1)
    match.submit("رضا", choice2, elapsed2)
    match.resolve_round()


def test_correct_answer_gives_points():
    match = make_match()
    play_round(match, "A", 5.0, "B", 8.0)
    assert match.scores["علی"] == POINTS
    assert match.scores["رضا"] == 0


def test_answer_is_case_and_space_insensitive():
    match = make_match()
    play_round(match, " a ", 5.0, "B", 6.0)
    assert match.scores["علی"] == POINTS


def test_late_answer_gets_nothing():
    match = make_match()
    play_round(match, "A", TIME_LIMIT + 1, "A", 5.0)
    assert match.scores["علی"] == 0
    assert match.scores["رضا"] == POINTS


def test_answer_exactly_at_the_limit_still_counts():
    match = make_match()
    play_round(match, "A", float(TIME_LIMIT), "B", 2.0)
    assert match.scores["علی"] == POINTS


def test_duplicate_player_names_are_rejected():
    with pytest.raises(ValueError):
        Match("علی", "علی", make_questions())


def test_unknown_player_cannot_submit():
    match = make_match()
    match.start_round()
    with pytest.raises(ValueError):
        match.submit("غریبه", "A", 1.0)


def test_match_ends_after_all_questions():
    match = make_match(n=2)
    play_round(match, "A", 1.0, "B", 2.0)
    play_round(match, "B", 1.0, "A", 2.0)
    assert match.is_over()
    assert match.start_round() is None


def test_winner_is_the_higher_score():
    match = make_match(n=1)
    play_round(match, "A", 1.0, "B", 2.0)
    assert match.winner() == "علی"


def test_tie_has_no_winner():
    match = make_match(n=1)
    play_round(match, "A", 1.0, "A", 2.0)
    assert match.winner() is None


def test_correct_text_returns_the_right_option():
    question = Question("پایتخت ژاپن کدام است؟", ["توکیو", "کیوتو", "اوساکا", "سئول"], "A")
    assert question.correct_text() == "توکیو"
