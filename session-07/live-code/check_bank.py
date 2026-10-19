"""🔍 بازرس بانک سؤال — جواب مرجعِ تمرین JSON شماره‌ی ۲.

یک گزارش از questions.json می‌دهد و مشکل‌هایش را پیدا می‌کند. اجرا:

    python check_bank.py

🎯 چیزی که یاد می‌دهد: گشتن در داده‌ی JSON، شمردن، و چک‌کردن — یعنی
   دقیقاً همان کاری که امروز pytest برای *کد* انجام می‌دهد، این‌بار برای *داده*.
"""

import json

PATH = "questions.json"
VALID_ANSWERS = ["A", "B", "C", "D"]
VALID_POWER_UPS = ["double", "steal", None]

with open(PATH, encoding="utf-8") as f:
    questions = json.load(f)

# ── شمارش‌ها ──
by_category: dict[str, int] = {}
with_power_up = 0

for question in questions:
    category = question.get("category", "بدون دسته")
    by_category[category] = by_category.get(category, 0) + 1
    if question.get("power_up"):
        with_power_up += 1

# ── پیدا کردن مشکل‌ها ──
problems: list[str] = []
seen_texts: list[str] = []

for number, question in enumerate(questions, start=1):
    text = question.get("text", "")

    if not text:
        problems.append(f"سؤال {number}: متن ندارد")
    elif text in seen_texts:
        problems.append(f"سؤال {number}: تکراری است — «{text}»")
    else:
        seen_texts.append(text)

    options = question.get("options", [])
    if len(options) != 4:
        problems.append(f"سؤال {number}: {len(options)} گزینه دارد، باید ۴ باشد")

    correct = question.get("correct")
    if correct not in VALID_ANSWERS:
        problems.append(f"سؤال {number}: جواب درستش «{correct}» است، باید A تا D باشد")

    power_up = question.get("power_up")
    if power_up not in VALID_POWER_UPS:
        problems.append(f"سؤال {number}: قدرت ویژه‌ی «{power_up}» را بازی نمی‌شناسد")

# ── گزارش ──
print(f"📊 بانک سؤال: {len(questions)} سؤال\n")

print("دسته‌ها:")
for category, count in by_category.items():
    print(f"  {category}: {count}")

print(f"\nسؤال با قدرت ویژه: {with_power_up} از {len(questions)}")

if problems:
    print(f"\n❌ {len(problems)} مشکل پیدا شد:")
    for problem in problems:
        print(f"  • {problem}")
else:
    print("\n✅ هیچ مشکلی پیدا نشد. بانک سالم است.")
