"""🔍 بازرسِ نقشه — بخش ⭐ تمرین جانبی ۱.

قبل از اینکه نقشه‌ات را به کسی بدهی، چک کن سالم است:
هر دری باید به اتاقی برود که **واقعاً وجود دارد**.

اجرا:  python check_house.py
"""

import json

with open("house.json", encoding="utf-8") as f:
    house = json.load(f)

rooms = house["rooms"]
problems: list[str] = []

if house["start"] not in rooms:
    problems.append(f"اتاق شروع «{house['start']}» اصلاً وجود ندارد")

reachable = [house["start"]]                     # از شروع کجاها می‌شود رفت؟
for room_id in reachable:
    for door, target in rooms[room_id]["exits"].items():
        if target not in rooms:
            problems.append(f"اتاق «{room_id}»: درِ «{door}» به اتاقِ ناموجودِ «{target}» می‌رود")
        elif target not in reachable:
            reachable.append(target)

for room_id, room in rooms.items():
    if room_id not in reachable:
        problems.append(f"اتاق «{room_id}» ساخته شده ولی هیچ راهی به آن نیست")
    for key in ["name", "text"]:
        if key not in room:
            problems.append(f"اتاق «{room_id}»: کلید «{key}» را ندارد")

ends = [room_id for room_id, room in rooms.items() if room.get("end")]

print(f"🗺  نقشه: {len(rooms)} اتاق · {len(reachable)} اتاق قابل‌دسترس · {len(ends)} پایان")

if not ends:
    problems.append("هیچ اتاقی end ندارد — بازی هیچ‌وقت تمام نمی‌شود")

if problems:
    print(f"\n❌ {len(problems)} مشکل:")
    for problem in problems:
        print(f"  • {problem}")
else:
    print("\n✅ نقشه سالم است. می‌توانی به دوستت بدهی.")
