"""🛡 تست‌های نگهبان — مرجعِ مربی، جلسه‌ی ۱۰.

قانون امروز: **هر باگی که حل می‌شود، یک تستِ نگهبان می‌گیرد.**

هر تست اینجا یک باگِ واقعی است که امروز حلش کردیم. اگر فردا کسی (یا خودتان)
آن `try` را پاک کند، این تست قرمز می‌شود و جلویش را می‌گیرد.

⭐ و دقت کنید همه‌شان `tmp_path` دارند: تست هرگز فایل‌های واقعی را لمس نمی‌کند.
"""

import json

import pytest

from storage import QuestionBank, ScoreBoard

SAMPLE = [
    {"text": f"سؤال {i}", "options": ["الف", "ب", "پ", "ت"],
     "correct": "B", "power_up": None, "category": "آزمایشی"}
    for i in range(1, 7)
]


def write_bank(tmp_path, items):
    path = tmp_path / "questions.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    return str(path)


# ─────────────── باگ ۱: فایل بانک سؤال نبود → بازی می‌مُرد

def test_a_missing_question_bank_says_so_clearly(tmp_path):
    with pytest.raises(FileNotFoundError) as caught:
        QuestionBank(str(tmp_path / "نیست.json"))

    assert "پیدا نشد" in str(caught.value)      # پیام باید آدمیزاد باشد، نه خام


# ─────────────── باگ ۲: JSON خراب → دیوارِ قرمزِ پایتون

def test_a_broken_question_bank_reports_the_line_number(tmp_path):
    path = tmp_path / "questions.json"
    path.write_text('[{"text": "س", "options": [1,2,3,4],}]', encoding="utf-8")

    with pytest.raises(ValueError) as caught:
        QuestionBank(str(path))

    message = str(caught.value)
    assert "خراب" in message
    assert "خط" in message                      # ⭐ بدون شماره‌ی خط، پیام بی‌فایده است


def test_an_empty_question_bank_is_refused(tmp_path):
    with pytest.raises(ValueError):
        QuestionBank(write_bank(tmp_path, []))


def test_a_bank_too_small_for_a_match_is_refused(tmp_path):
    bank = QuestionBank(write_bank(tmp_path, SAMPLE[:2]))
    with pytest.raises(ValueError) as caught:
        bank.pick(5)

    assert "لازم است" in str(caught.value)


# ─────────────── باگ ۳: رده‌بندیِ خراب → بازی می‌مُرد (و نباید می‌مُرد)

def test_a_broken_leaderboard_does_not_kill_the_game(tmp_path):
    """⭐ تصمیمِ متفاوت برای فایلِ متفاوت.

    بدون بانک سؤال نمی‌شود بازی کرد → فریاد.
    بدون تاریخچه‌ی رده‌بندی می‌شود بازی کرد → از نو شروع کن و ادامه بده.
    """
    path = tmp_path / "leaderboard.json"
    path.write_text('{"علی": {"wins": 2, BROKEN', encoding="utf-8")

    board = ScoreBoard(str(path))               # نباید خطا بدهد
    assert board.is_empty()


def test_the_game_can_still_record_after_a_broken_leaderboard(tmp_path):
    path = tmp_path / "leaderboard.json"
    path.write_text("نه JSON است و نه چیز دیگر", encoding="utf-8")

    board = ScoreBoard(str(path))
    board.record("سارا", "علی", 10, "سارا", 13)

    again = ScoreBoard(str(path))               # فایلِ سالمِ تازه نوشته شد
    assert dict(again.top(5))["سارا"] == {"wins": 1, "points": 13}
