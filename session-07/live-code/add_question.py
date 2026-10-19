"""➕ ابزار اضافه‌کردن سؤال — جواب مرجعِ تمرین JSON شماره‌ی ۱.

این فایل **بخشی از بازی نیست**؛ یک ابزار جداست. به همین دلیل اجازه دارد
print و input داشته باشد. اجرا:

    python add_question.py

🎯 چیزی که یاد می‌دهد: چرخه‌ی «بخوان → عوض کن → بنویس» روی یک فایل JSON.
"""

import json

PATH = "questions.json"


def load() -> list[dict]:
    with open(PATH, encoding="utf-8") as f:
        return json.load(f)


def save(questions: list[dict]) -> None:
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)


def ask_new_question() -> dict:
    text = input("متن سؤال: ").strip()

    options = []
    for letter in "ABCD":
        options.append(input(f"گزینه‌ی {letter}: ").strip())

    correct = input("جواب درست (A-D): ").strip().upper()
    while correct not in ["A", "B", "C", "D"]:
        correct = input("فقط A یا B یا C یا D: ").strip().upper()

    power_up = input("قدرت ویژه (double / steal / خالی): ").strip()
    while power_up not in ["double", "steal", ""]:
        power_up = input("فقط double یا steal — یا Enter برای هیچ‌کدام: ").strip()
    category = input("دسته: ").strip()

    return {
        "text": text,
        "options": options,
        "correct": correct,
        "power_up": power_up if power_up else None,   # خالی → null در فایل
        "category": category if category else "عمومی",
    }


questions = load()
print(f"بانک سؤال الان {len(questions)} سؤال دارد.\n")

questions.append(ask_new_question())
save(questions)

print(f"\n✅ ذخیره شد. بانک سؤال حالا {len(questions)} سؤال دارد.")
print("بازی را اجرا کن — سؤال تازه‌ات ممکن است همین دور بیاید!")
