"""🧑‍🏫 چکِ مربی جلسه‌ی ۶ — قبل از کلاس، یک‌بار اجرا کنید.

⚠️ این فایل را **به بچه‌ها ندهید و روی فلش نگذارید** (تست‌نویسی جلسه‌ی ۷ است).

چه کار می‌کند: بانک سؤال و دفتر رده‌بندی را کامل امتحان می‌کند — خواندن فایل،
تصادفی‌بودن و بدون‌تکرار بودن سؤال‌ها، نگهبانِ «سؤال کم است»، ثبت نتیجه،
ماندنِ داده روی دیسک، و اینکه فارسیِ داخل فایل **فارسی** بماند نه \\u0639.

اجرا (در همان پوشه‌ای که storage.py و engine.py هستند):

    python _instructor_check.py
"""

import json
import tempfile
from pathlib import Path

try:
    import engine as e
    import storage as s
except ModuleNotFoundError:                # در پوشه‌ی live-code، اسم فایل‌ها *_complete است
    import sys, importlib
    e = importlib.import_module("engine_complete")
    sys.modules["engine"] = e              # تا storage بتواند «from engine import ...» کند
    s = importlib.import_module("storage_complete")

QuestionBank, ScoreBoard = s.QuestionBank, s.ScoreBoard

SAMPLE = [
    {"text": f"سؤال شماره‌ی {i}", "options": ["الف", "ب", "پ", "ت"],
     "correct": "B", "power_up": ("double" if i == 1 else None), "category": "آزمایشی"}
    for i in range(1, 9)
]

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    qpath = tmp / "questions.json"
    lpath = tmp / "leaderboard.json"
    json.dump(SAMPLE, open(qpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    # ── بانک سؤال ──
    bank = QuestionBank(str(qpath))
    assert bank.count() == 8
    picked = bank.pick(5)
    assert len(picked) == 5
    assert len({q.text for q in picked}) == 5, "سؤال تکراری در یک مسابقه!"
    assert all(isinstance(q, e.Question) for q in picked)
    assert any(q.power_up == "double" for q in bank.pick(8)), "power_up از فایل خوانده نشد"

    try:
        bank.pick(99)
        raise AssertionError("باید ValueError می‌داد: سؤال کافی نیست")
    except ValueError:
        pass

    # تصادفی است؟ (ده بار انتخاب، حتماً دو نتیجه‌ی متفاوت)
    orders = {tuple(q.text for q in bank.pick(5)) for _ in range(10)}
    assert len(orders) > 1, "انتخاب سؤال تصادفی نیست"

    # ── دفتر رده‌بندی ──
    board = ScoreBoard(str(lpath))
    assert board.is_empty() and not lpath.exists()      # اولین اجرا: فایل هنوز نیست

    board.record("سارا", "علی", 30, "سارا", 39)
    assert lpath.exists(), "_save صدا زده نشد — هیچ‌چیز روی دیسک نرفت"

    raw = lpath.read_text(encoding="utf-8")
    assert "سارا" in raw, "ensure_ascii=False جا افتاده — اسم‌ها \\u06.. شده‌اند"
    assert "\n" in raw, "indent=2 جا افتاده — کل فایل یک خط شده"

    # ── همان لحظه‌ی جادویی: بازی را ببند و باز کن ──
    again = ScoreBoard(str(lpath))
    assert not again.is_empty()
    assert again.top(5)[0][0] == "سارا"
    assert again.top(5)[0][1] == {"wins": 1, "points": 39}

    # تساوی: هیچ‌کس برد نمی‌گیرد، ولی امتیاز ثبت می‌شود
    again.record(None, "علی", 10, "رها", 10)
    third = ScoreBoard(str(lpath))
    names = dict(third.top(5))
    assert names["علی"] == {"wins": 0, "points": 40}
    assert names["رها"] == {"wins": 0, "points": 10}

    # ترتیب: اول برد، بعد امتیاز
    assert [n for n, _ in third.top(5)] == ["سارا", "علی", "رها"]

# ── قانون معماری: مغز هنوز نه حرف می‌زند، نه فایل می‌خواند ──
code = "\n".join(
    line for line in open(e.__file__, encoding="utf-8").read().splitlines()
    if not line.lstrip().startswith("#")
)
for forbidden in ("print(", "input(", "time.", "open(", "json.load", "json.dump"):
    assert forbidden not in code, f"موتور {forbidden} دارد! امروز نباید عوض می‌شد."

print("✅ همه‌ی چک‌ها پاس شد — بانک سؤال و رده‌بندی سالم‌اند.")
