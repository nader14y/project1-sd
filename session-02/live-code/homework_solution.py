# حل تمرین خانه‌ی جلسه‌ی ۲ — 🔒 فقط برای مربی، پخش نکنید
#
# خواسته‌ها:
#   ۱) منوی شروع رنگی: «۱) بازی جدید   ۲) خروج»
#   ۲) بازی فقط با انتخاب ۱ شروع شود
#   ۳) (تمرین دوم، روی کاغذ نیست: راه‌اندازی پروژه از صفر در پوشه‌ی جدید)

from rich.console import Console

console = Console()

questions = [
    ("پایتخت ژاپن کدام است؟", ["توکیو", "کیوتو", "اوساکا", "سئول"], "A"),
    ("خروجی len('سلام') چیست؟", ["3", "4", "5", "خطا"], "B"),
    ("بزرگ‌ترین سیاره‌ی منظومه‌ی شمسی؟", ["زمین", "زحل", "مشتری", "نپتون"], "C"),
    ("نماد شیمیایی طلا چیست؟", ["Ag", "Au", "Fe", "Gd"], "B"),
    ("شاهنامه اثر کیست؟", ["حافظ", "سعدی", "فردوسی", "مولوی"], "C"),
]


def show_menu():
    console.print("\n[bold cyan]⚔  Quiz Battle  ⚔[/bold cyan]")
    console.print("[bold green]۱)[/bold green] بازی جدید")
    console.print("[bold red]۲)[/bold red] خروج")


def play():
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


while True:
    show_menu()
    choice = input("انتخاب تو (۱ یا ۲): ").strip()

    if choice == "1" or choice == "۱":
        play()
    elif choice == "2" or choice == "۲":
        console.print("خداحافظ! 👋", style="bold cyan")
        break
    else:
        console.print("⚠️  فقط ۱ یا ۲ را وارد کن.", style="bold yellow")


# ─────────────────────────────────────────────────────────────────────
# نکته‌های تصحیح — دنبال این‌ها بگردید:
#
# ✅ عالی:  حلقه‌ی while True با break در گزینه‌ی خروج
#           (بازی بعد از تمام شدن، برمی‌گردد به منو)
#
# ⚠️  قابل‌قبول: منو فقط یک بار نشان داده شود و بعد از بازی برنامه تمام شود.
#           بپرسید: «چطور کاری کنیم بعد از بازی برگردد به منو؟» — درس حلقه، رایگان.
#
# ⚠️  رقم فارسی: بچه‌ها «۱» فارسی تایپ می‌کنند و بعد گیج می‌شوند که چرا کار نمی‌کند.
#           این یک لحظه‌ی آموزشی طلایی است: "۱" == "1" غلط است!
#           در ترمینال نشانشان بدهید. راه‌حل من در کد بالا: هر دو را قبول می‌کنم.
#
# ❌ اشتباه رایج: if choice == 1  (بدون کوتیشن)
#           input() همیشه رشته می‌دهد. مقایسه با عدد هیچ‌وقت درست نمی‌شود.
#
# 💡 اگر کسی تابع تعریف نکرد و همه‌چیز را داخل حلقه نوشت، امروز کاملاً قبول است.
#    تابع و کلاس مال جلسه‌ی ۴ است — الان تعمیمش ندهید.
