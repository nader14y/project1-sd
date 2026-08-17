"""تست‌های موتور بازی — هر ۵ قانون محصول، به‌علاوه‌ی قابلیت امضا (سپر).

نکته‌ی طلایی جلسه‌ی ۷: هیچ‌کدام از این تست‌ها یک ثانیه هم صبر نمی‌کنند،
چون زمان به موتور تزریق می‌شود و موتور خودش هرگز time.time() صدا نمی‌زند.
"""

import pytest

from config import ROUNDS, TIME_LIMIT
from game.match import Match
from game.question import Question


def make_questions(power_up=None, n=ROUNDS):
    return [Question("۲+۲ چند است؟", ["4", "5", "6", "7"], "A", power_up) for _ in range(n)]


def make_match(power_up=None):
    return Match("علی", "رضا", make_questions(power_up))


def play_round(match, choice1, elapsed1, choice2, elapsed2):
    match.start_round()
    match.submit("علی", choice1, elapsed1)
    match.submit("رضا", choice2, elapsed2)
    return match.resolve_round()


# ─────────────────────────────────────────── قانون ۲: امتیاز و بونوس سرعت


def test_correct_answer_gives_points():
    m = make_match()
    play_round(m, "A", 5.0, "B", 8.0)
    assert m.scores["علی"] == 13      # ۱۰ + ۳ بونوس سرعت (تنها درست‌جواب)
    assert m.scores["رضا"] == 0


def test_speed_bonus_goes_to_faster_player():
    m = make_match()
    play_round(m, "A", 12.0, "A", 4.0)   # رضا سریع‌تر بود
    assert m.scores["رضا"] == 13
    assert m.scores["علی"] == 10


def test_no_speed_bonus_when_nobody_is_correct():
    m = make_match()
    summary = play_round(m, "B", 3.0, "C", 4.0)
    assert m.scores == {"علی": 0, "رضا": 0}
    assert all(row["speed_bonus"] == 0 for row in summary["results"].values())


def test_answer_is_case_and_space_insensitive():
    m = make_match()
    play_round(m, " a ", 5.0, "B", 6.0)
    assert m.scores["علی"] == 13


# ───────────────────────────────────────────────────── قانون ۴: مهلت زمانی


def test_late_answer_gets_nothing():
    m = make_match()
    summary = play_round(m, "A", TIME_LIMIT + 1, "A", 5.0)
    assert summary["results"]["علی"]["status"] == "too_late"
    assert m.scores["علی"] == 0
    assert m.scores["رضا"] == 13       # تنها درست‌جوابِ به‌موقع


def test_answer_exactly_at_the_limit_still_counts():
    m = make_match()
    summary = play_round(m, "A", float(TIME_LIMIT), "B", 2.0)
    assert summary["results"]["علی"]["status"] == "correct"


# ─────────────────────────────────────────────── قانون ۳: قدرت‌های ویژه


def test_double_multiplies_the_whole_round_score():
    m = make_match(power_up="double")
    play_round(m, "A", 5.0, "B", 6.0)
    assert m.scores["علی"] == 26       # (۱۰ + ۳) × ۲ — تصمیم مستندشده‌ی این نسخه


def test_steal_takes_points_from_the_rival():
    m = make_match()
    play_round(m, "A", 5.0, "B", 6.0)          # علی: ۱۳
    m.questions[1] = Question("۳+۳؟", ["6", "7", "8", "9"], "A", "steal")
    play_round(m, "B", 4.0, "A", 5.0)          # حالا رضا درست جواب می‌دهد
    assert m.scores["رضا"] == 13
    assert m.scores["علی"] == 8                # ۱۳ − ۵


def test_steal_never_pushes_score_below_zero():
    m = make_match(power_up="steal")
    play_round(m, "B", 4.0, "A", 5.0)          # رضا درست، علی صفر امتیاز دارد
    assert m.scores["علی"] == 0                # نه ‎−۵


def test_both_correct_on_steal_means_both_steal():
    """تصمیم محصولیِ این نسخه — و دقیقاً همان بحثی که کلاس باید بکند."""
    m = make_match(power_up="steal")
    summary = play_round(m, "A", 4.0, "A", 9.0)
    assert summary["results"]["علی"]["stole"] == 5
    assert summary["results"]["رضا"]["stole"] == 5


# ───────────────────────────────────── قابلیت امضای این نسخه: 🛡️ سپر


def test_shield_question_gives_a_shield_to_correct_players():
    m = make_match(power_up="shield")
    play_round(m, "A", 5.0, "B", 6.0)
    assert m.shields["علی"] == 1
    assert m.shields["رضا"] == 0


def test_shield_blocks_the_next_steal():
    m = make_match(power_up="shield")
    play_round(m, "A", 5.0, "B", 6.0)          # علی: ۱۳ امتیاز + ۱ سپر
    m.questions[1] = Question("۳+۳؟", ["6", "7", "8", "9"], "A", "steal")
    summary = play_round(m, "B", 4.0, "A", 5.0)
    assert summary["results"]["علی"]["shield_used"] is True
    assert m.scores["علی"] == 13               # سپر جلوی سرقت را گرفت
    assert m.shields["علی"] == 0               # و مصرف شد


# ───────────────────────────────────── قانون ۵: پایان مسابقه و برنده


def test_winner_and_draw():
    m = make_match()
    for _ in range(ROUNDS):
        play_round(m, "A", 5.0, "B", 6.0)
    assert m.is_over()
    assert m.winner() == "علی"

    draw = make_match()
    for _ in range(ROUNDS):
        play_round(draw, "B", 5.0, "C", 6.0)   # هر دو غلط، هر راند
    assert draw.winner() is None


def test_cannot_start_a_round_after_the_match_is_over():
    m = make_match()
    for _ in range(ROUNDS):
        play_round(m, "A", 5.0, "B", 6.0)
    with pytest.raises(ValueError):
        m.start_round()


# ───────────────────────────────────────────── ورودی‌های بد (جلسه‌ی ۱۰)


def test_two_players_cannot_share_a_name():
    with pytest.raises(ValueError):
        Match("علی", "علی", make_questions())


def test_empty_player_name_is_rejected():
    with pytest.raises(ValueError):
        Match("علی", "   ", make_questions())


def test_match_needs_enough_questions():
    with pytest.raises(ValueError):
        Match("علی", "رضا", make_questions(n=ROUNDS - 1))


def test_unknown_player_cannot_submit():
    m = make_match()
    m.start_round()
    with pytest.raises(ValueError):
        m.submit("مهدی", "A", 5.0)


def test_a_player_cannot_answer_twice():
    m = make_match()
    m.start_round()
    m.submit("علی", "A", 5.0)
    with pytest.raises(ValueError):
        m.submit("علی", "B", 6.0)


def test_cannot_resolve_before_both_answered():
    m = make_match()
    m.start_round()
    m.submit("علی", "A", 5.0)
    with pytest.raises(ValueError):
        m.resolve_round()


def test_question_rejects_bad_data():
    with pytest.raises(ValueError):
        Question("سه گزینه؟", ["۱", "۲", "۳"], "A")
    with pytest.raises(ValueError):
        Question("گزینه‌ی درست بد", ["۱", "۲", "۳", "۴"], "E")
    with pytest.raises(ValueError):
        Question("قدرت ویژه‌ی ناشناس", ["۱", "۲", "۳", "۴"], "A", power_up="teleport")
