"""🧑‍🏫 چکِ مربی — قبل از کلاس، یک‌بار اجرا کنید.

⚠️ این فایل را **به بچه‌ها ندهید و روی فلش نگذارید.** تست‌نویسی، جلسه‌ی ۷ است و
   دیدنِ این فایل، «آهان!»ِ آن جلسه را خراب می‌کند.

چه کار می‌کند: کل موتور را در دو ثانیه امتحان می‌کند — بونوس سرعت، دیر شدن،
غلط، تساوی، پنج نگهبان ValueError، و اینکه از بیرون نمی‌شود تقلب کرد.

اجرا (در همان پوشه‌ای که engine.py هست):

    python _instructor_check.py

اگر «✅ همه‌ی چک‌ها پاس شد» را دیدید، فایل موتور سالم است.
"""

try:
    import engine as e                    # سر کلاس
except ModuleNotFoundError:
    import engine_complete as e           # در پوشه‌ی live-code

Question, Match = e.Question, e.Match
POINTS, SPEED_BONUS, ROUNDS = e.POINTS, e.SPEED_BONUS, e.ROUNDS

qs = [Question(f"سؤال {i}", ["الف", "ب", "پ", "ت"], "B") for i in range(ROUNDS)]

# ── یک راند سالم: بونوس سرعت به سریع‌ترین درست‌جواب ──
m = Match("علی", "سارا", qs)
assert m.round == 0 and not m.is_over() and m.score_of("علی") == 0
assert m.start_round() is qs[0] and m.round == 1

m.submit("علی", "b", 4.0)                 # درست، کندتر (و حرف کوچک)
m.submit("سارا", " B ", 2.0)              # درست، سریع‌تر (و با فاصله)
r = m.resolve_round()
assert r["علی"].status == "correct" and r["علی"].points == POINTS
assert r["سارا"].points == POINTS + SPEED_BONUS
assert m.score_of("سارا") == POINTS + SPEED_BONUS
assert m.answer_of("سارا") == (" B ", 2.0)

# ── غلط، و دیر ──
m.start_round()
m.submit("علی", "A", 1.0)
m.submit("سارا", "B", 99.0)               # درست بود، ولی دیر
r = m.resolve_round()
assert r["علی"].status == "wrong" and r["علی"].points == 0
assert r["سارا"].status == "too_late" and r["سارا"].points == 0

for _ in range(3):
    m.start_round()
    m.submit("علی", "B", 1.0)
    m.submit("سارا", "C", 1.0)
    m.resolve_round()
assert m.is_over() and m.winner() == "علی"

# ── تساوی ──
t = Match("الف", "ب", qs)
for _ in range(ROUNDS):
    t.start_round()
    t.submit("الف", "A", 5.0)
    t.submit("ب", "C", 5.0)
    t.resolve_round()
assert t.winner() is None

# ── کپسوله‌سازی: از بیرون نمی‌شود عوض کرد (نمایشِ دقیقه‌ی ۵۸) ──
def refused(action) -> bool:
    try:
        action()
        return False
    except AttributeError:
        return True

assert refused(lambda: setattr(m, "round", 99))
assert refused(lambda: setattr(qs[0], "correct", "A"))
assert refused(lambda: setattr(r["علی"], "points", 1000))
assert not hasattr(m, "scores")

m.players.append("متقلب")
assert len(m.players) == 2                # کپی گرفتیم، نه اصل

qs[0].options[0] = "هک"
assert qs[0].options[0] == "الف"          # کپی گرفتیم، نه اصل

# ── نگهبان‌ها: مسابقه/سؤالِ بی‌معنا ساخته نمی‌شود ──
for bad in [lambda: Match("علی", "علی", qs),                    # نام تکراری
            lambda: Match("الف", "ب", qs[:2]),                  # سؤال کم
            lambda: Question("س", ["الف", "ب"], "A"),           # گزینه کم
            lambda: Question("س", ["الف", "ب", "پ", "ت"], "E"), # جواب بی‌معنا
            lambda: Match("الف", "ب", qs).submit("غریبه", "A", 1.0)]:
    try:
        bad()
        raise AssertionError("باید ValueError می‌داد و نداد")
    except ValueError:
        pass

# ── قانون معماری: موتور نه حرف می‌زند، نه ساعت می‌خواند ──
source = open(e.__file__, encoding="utf-8").read()
code = "\n".join(line for line in source.splitlines() if not line.lstrip().startswith("#"))
assert "print(" not in code and "input(" not in code, "موتور print/input دارد!"
assert "time." not in code, "موتور خودش زمان می‌خواند!"

print("✅ همه‌ی چک‌ها پاس شد — موتور سالم است.")
