"""دهان بازی — همه‌ی print و input و رنگ و کرنومتر.  ✅ وضعیت مطلوب پایان جلسه‌ی ۴

📌 اسم فایل سر کلاس: game.py  (همان اسمی که سه هفته است اجرا می‌کنند)

⚠️ کرنومتر اینجاست، نه در موتور. زمان را همین فایل اندازه می‌گیرد و
   به موتور می‌دهد. جلسه‌ی ۷ می‌فهمند چرا این تصمیم طلاست.
"""

import time

from rich.console import Console

from engine import Match, Question, ROUNDS, TIME_LIMIT

console = Console()

questions = [
    Question("پایتخت ژاپن کدام است؟", ["توکیو", "کیوتو", "اوساکا", "سئول"], "A"),
    Question("بزرگ‌ترین سیاره‌ی منظومه‌ی شمسی؟", ["زمین", "زحل", "مشتری", "نپتون"], "C"),
    Question("نماد شیمیایی طلا چیست؟", ["Ag", "Au", "Fe", "Gd"], "B"),
    Question("شاهنامه اثر کیست؟", ["حافظ", "سعدی", "فردوسی", "مولوی"], "C"),
    Question("خروجی len('سلام') چیست؟", ["3", "4", "5", "خطا"], "B"),
]


def ask(player, question, round_no):
    """سؤال را نشان می‌دهد، جواب می‌گیرد، و مدت پاسخ‌گویی را برمی‌گرداند."""
    console.clear()
    console.print(f"[bold cyan]راند {round_no} از {ROUNDS}[/bold cyan]")
    console.print(f"\n[bold yellow]نوبت {player}[/bold yellow] — ⏱ {TIME_LIMIT} ثانیه فرصت داری!")
    console.print(f"\n{question.text}")
    for letter, option in zip("ABCD", question.options):
        console.print(f"  [bold]{letter})[/bold] {option}")

    start = time.time()                 # ← کرنومتر روشن
    choice = input("\nجواب تو (A-D): ")
    elapsed = time.time() - start       # ← کرنومتر خاموش

    return choice, elapsed


def hand_over(player):
    """صفحه را پاک می‌کند تا نفر دوم جواب نفر اول را نبیند."""
    console.clear()
    console.print(f"\n[bold magenta]نوبت {player} است.[/bold magenta]")
    console.print("بازیکن قبلی لطفاً نگاه نکند 🙈")
    input("\nوقتی آماده بودی Enter را بزن… ")


def show_round_result(match, results, question):
    """نتیجه‌ی راند + تابلوی امتیاز."""
    console.clear()
    console.print(f"[bold]نتیجه‌ی راند {match.round}[/bold]")
    console.print(f"\n✅ جواب درست: [bold green]{question.correct}) {question.correct_text()}[/bold green]\n")

    for player in match.players:
        result = results[player]
        choice, elapsed = match.answers[player]

        if result["status"] == "correct":
            mark = "[bold green]✅ درست[/bold green]"
        elif result["status"] == "too_late":
            mark = "[bold red]⏰ دیر شد[/bold red]"
        else:
            mark = "[bold red]❌ غلط[/bold red]"

        console.print(
            f"  {player}: {choice.strip().upper()}  {mark}  "
            f"({elapsed:.1f} ثانیه)  →  [bold]+{result['points']}[/bold]"
        )

    console.print("\n[bold cyan]تابلوی امتیاز:[/bold cyan]")
    for player in match.players:
        console.print(f"  {player}: [bold]{match.scores[player]}[/bold]")

    input("\nEnter برای راند بعد… ")


def show_final(match):
    """تشریفات برنده."""
    console.clear()
    winner = match.winner()

    if winner is None:
        console.print("\n🤝 [bold yellow]مساوی شد![/bold yellow] هیچ‌کس نباخت.")
    else:
        console.print(f"\n🏆 [bold yellow]برنده: {winner}[/bold yellow] 🏆")

    console.print("\n[bold cyan]امتیاز نهایی:[/bold cyan]")
    for player in match.players:
        console.print(f"  {player}: [bold]{match.scores[player]}[/bold]")


# ───────────────────────────────────────────── حلقه‌ی اصلی بازی

console.print("[bold cyan]⚔  Quiz Battle  ⚔[/bold cyan]\n")
name1 = input("نام بازیکن اول: ").strip()
name2 = input("نام بازیکن دوم: ").strip()

match = Match(name1, name2, questions)

while not match.is_over():
    question = match.start_round()

    for index, player in enumerate(match.players):
        if index == 1:                  # قبل از نوبت نفر دوم
            hand_over(player)
        choice, elapsed = ask(player, question, match.round)
        match.submit(player, choice, elapsed)

    results = match.resolve_round()
    show_round_result(match, results, question)

show_final(match)


# ─────────────────────────────────────────────────────────────────────
# ⚠️ نکته‌ی مربی — این باگ را عمداً باز می‌گذاریم:
#
#    اگر هر دو بازیکن یک نام وارد کنند، Match یک ValueError می‌دهد و
#    برنامه با یک صفحه‌ی قرمز می‌میرد.
#
#    این درست است! موتور وظیفه‌اش را انجام داد و فریاد زد.
#    فقط این فایل هنوز فریادش را ترجمه نمی‌کند.
#
#    🌱 عمداً حلش نکنید — خوراک جلسه‌ی ۹ (مدیریت خطا) است.
#       اگر بچه‌ای پیدایش کرد، تحسینش کنید و بگویید: «درست دیدی. جلسه‌ی ۹.»
