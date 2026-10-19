"""💬 کارآگاهِ گروه — جواب مرجعِ تمرین جانبی ۲.

یک روزِ کاملِ چتِ یک گروه در chat.json است. گزارشش را دربیاور.

اجرا:  python chat_detective.py
"""

import json

with open("chat.json", encoding="utf-8") as f:
    messages = json.load(f)

total = len(messages)

# ── شمارش دو سطحی: هر نفر، و هر ساعت ──
count_by_person: dict[str, int] = {}
letters_by_person: dict[str, int] = {}
count_by_hour: dict[str, int] = {}
questions = 0

longest = messages[0]

for message in messages:
    person = message["from"]
    text = message["text"]
    hour = message["time"].split(":")[0]        # "20:07" → "20"

    count_by_person[person] = count_by_person.get(person, 0) + 1
    letters_by_person[person] = letters_by_person.get(person, 0) + len(text)
    count_by_hour[hour] = count_by_hour.get(hour, 0) + 1

    if text.strip().endswith("؟") or text.strip().endswith("?"):
        questions += 1

    if len(text) > len(longest["text"]):
        longest = message

# ── گزارش ──
print(f"💬 {total} پیام از {len(count_by_person)} نفر\n")

print("پرحرف‌ترین‌ها:")
ranking = sorted(count_by_person.items(), key=lambda item: item[1], reverse=True)
for rank, (person, count) in enumerate(ranking, start=1):
    share = round(count / total * 100)
    average = round(letters_by_person[person] / count)
    bar = "█" * count
    print(f"  {rank}) {person:6} {bar} {count} پیام ({share}٪) · میانگین {average} حرف")

busiest = max(count_by_hour, key=count_by_hour.get)
print(f"\nشلوغ‌ترین ساعت: {busiest}:00 تا {busiest}:59 با {count_by_hour[busiest]} پیام")
print(f"سؤال‌ها: {questions} تا از {total} پیام ({round(questions / total * 100)}٪)")

print(f"\nبلندترین پیام، از {longest['from']} در {longest['time']}:")
print(f"  «{longest['text']}»")

quietest = ranking[-1]
print(f"\n🤫 کم‌حرف‌ترین: {quietest[0]} با فقط {quietest[1]} پیام")
