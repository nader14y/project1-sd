from rich.console import Console  # pyright: ignore[reportMissingImports]

console = Console()

questions = [
    ("پایتخت ژاپن کدام است؟", ["توکیو", "کیوتو", "اوساکا", "سئول"], "A"),
    ("خروجی len('سلام') چیست؟", ["3", "4", "5", "خطا"], "B"),
    ("بزرگ‌ترین سیاره‌ی منظومه‌ی شمسی؟", ["زمین", "زحل", "مشتری", "نپتون"], "C"),
    ("نماد شیمیایی طلا چیست؟", ["Ag", "Au", "Fe", "Gd"], "B"),
    ("شاهنامه اثر کیست؟", ["حافظ", "سعدی", "فردوسی", "مولوی"], "C"),
]


def show_menu():
    console.print("\n⚔  Quiz Battle  ⚔", style="bold cyan")
    console.print("۱) بازی جدید", style="bold green")
    console.print("۲) خروج", style="bold red")


def play():
    total = len(questions)
    score = 0
    correct_count = 0

    for i, (text, options, correct) in enumerate(questions, start=1):
        console.print(f"\nسؤال {i} از {total}:", style="bold cyan")
        console.print(text, style="bold")
        for letter, opt in zip("ABCD", options):
            console.print(f"  {letter}) {opt}", style="bold")

        answer = input("جواب تو (A-D): ").strip().upper()

        if answer == correct:
            console.print(" درست!", style="bold green")
            score += 10
            correct_count += 1
        else:
            console.print(f" غلط! جواب درست: {correct}", style="bold red")

    percent = correct_count / total * 100
    console.print("\nبازی تمام شد!", style="bold yellow")
    console.print(f"   امتیاز تو: {score}", style="bold green")
    console.print(f"   درست: {correct_count} از {total}  ({percent:.0f}٪)", style="bold")


while True:
    show_menu()
    choice = input("انتخاب تو (۱ یا ۲): ").strip()

    if choice in ("1", "۱"):
        play()
    elif choice in ("2", "۲"):
        console.print("خداحافظ!", style="bold cyan")
        break
    else:
        console.print(" فقط ۱ یا ۲ را وارد کن.", style="bold yellow")