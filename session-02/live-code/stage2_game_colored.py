# مرحله‌ی ۲ (دقیقه‌ی ۵۲ تا ۷۰) — بازی رنگی
#
# ✅ این «وضعیت مطلوب پایان جلسه‌ی ۲» است.
#    نقطه‌ی شروع: کد پایان جلسه‌ی ۱ + تمرین خانه (۵ سؤال، شمارنده، درصد).
#
# تنها تغییرات امروز:
#   ۱) دو خط بالای فایل: import و ساخت Console
#   ۲) هر print → console.print با رنگ

from rich.console import Console

console = Console()

questions = [
    ("پایتخت ژاپن کدام است؟", ["توکیو", "کیوتو", "اوساکا", "سئول"], "A"),
    ("خروجی len('سلام') چیست؟", ["3", "4", "5", "خطا"], "B"),
    ("بزرگ‌ترین سیاره‌ی منظومه‌ی شمسی؟", ["زمین", "زحل", "مشتری", "نپتون"], "C"),
    ("نماد شیمیایی طلا چیست؟", ["Ag", "Au", "Fe", "Gd"], "B"),
    ("شاهنامه اثر کیست؟", ["حافظ", "سعدی", "فردوسی", "مولوی"], "C"),
]

total = len(questions)
score = 0
correct_count = 0

for i, (text, options, correct) in enumerate(questions, start=1):
    console.print(f"\n[bold cyan]سؤال {i} از {total}:[/bold cyan] {text}")
    for letter, opt in zip("ABCD", options):
        console.print(f"  [bold]{letter})[/bold] {opt}")

    answer = input("جواب تو (A-D): ").strip().upper()

    if answer == correct:
        console.print("✅ درست!", style="bold green")
        score += 10
        correct_count += 1
    else:
        console.print(f"❌ غلط! جواب درست: {correct}", style="bold red")

percent = correct_count / total * 100

console.print("\n🏁 بازی تمام شد!", style="bold yellow")
console.print(f"   امتیاز تو: [bold green]{score}[/bold green]")
console.print(f"   درست: {correct_count} از {total}  ([bold]{percent:.0f}٪[/bold])")


# ─────────────────────────────────────────────────────────────────────
# نکته‌های حین کار:
#
# • input() را عوض نکنید. rich برای ورودی هم ابزار دارد، ولی امروز لازم نیست —
#   «چیزی که لازم نیست، اضافه نکن.»
#
# • تگ باید بسته شود:  [bold]متن[/bold]
#   اگر یادتان رفت، rich خطا نمی‌دهد ولی رنگ تا آخر خط ادامه پیدا می‌کند.
#
# • اگر ایموجی مربع دیده شد: فونت ترمینال است، نه باگ کد. رهایش کنید.
