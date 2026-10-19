"""🏚 خانه‌ی ارواح — جواب مرجعِ تمرین جانبی ۱.

⭐ نکته‌ی کل تمرین: **اسم هیچ اتاقی در این فایل نیست.**
   کل نقشه، داستان، درها و اشیا در house.json زندگی می‌کنند.
   همین برنامه، نقشه‌ی هر کسی را بازی می‌کند.

اجرا:  python adventure.py
"""

import json

with open("house.json", encoding="utf-8") as f:
    house = json.load(f)

rooms = house["rooms"]
current = house["start"]
bag: list[str] = []
steps = 0

print("🏚  خانه‌ی ارواح")
print("(برای خروج، q بزن)\n")

while True:
    room = rooms[current]
    steps += 1

    print(f"\n📍 {room['name']}")
    print(room["text"])

    item = room.get("item")                      # get: اگر اتاق شیء نداشت، None
    if item and item not in bag:
        bag.append(item)
        print(f"🎒 برداشتی: {item}")

    if room.get("end"):
        print(f"\n🏁 تمام شد! در {steps} قدم، با {len(bag)} شیء در کوله‌ات.")
        break

    exits = room["exits"]
    print("راه‌ها:", "، ".join(exits))

    choice = input("کجا بروم؟ ").strip()
    if choice == "q":
        print("ترسیدی؟ 😄")
        break

    if choice not in exits:
        print("❌ از این طرف راهی نیست.")
        continue

    target = rooms[exits[choice]]
    needed = target.get("needs")                 # در قفل؟
    if needed and needed not in bag:
        print(f"🔒 قفل است. انگار به «{needed}» احتیاج داری.")
        continue

    current = exits[choice]
