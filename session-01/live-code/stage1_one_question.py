print("سؤال ۱: پایتخت ژاپن کدام است؟")
print("  A) توکیو")
print("  B) کیوتو")
print("  C) اوساکا")
print("  D) سئول")

answer = input("جواب تو (A-D): ")
# answer = input("جواب تو (A-D): ").strip().upper()

if answer == "A":
    print("✅ درست!")
else:
    print("❌ غلط! جواب درست: A")
