"""👄 دهانِ بازی — نمایش، ورودی، رنگ، کرنومتر.  ✅ وضعیت مطلوب پایان جلسه‌ی ۶

📌 اسم فایل سر کلاس: game.py
🐍 نیاز: پایتون ۳٫۱۰ یا بالاتر

🎓 دقت کنید این فایل هیچ‌جا داخلِ Match دست نمی‌برد — نه سراغ ویژگی‌های «_»دار
   می‌رود، نه چیزی را عوض می‌کند. فقط *می‌پرسد*:
       match.score_of(...)   و   match.answer_of(...)
   دهان اجازه‌ی خواندن دارد، اجازه‌ی دست‌کاری ندارد.

🆕 امروز: سؤال‌ها دیگر اینجا نیستند. دهان از **دفتردار** می‌خواهدشان.
   و آخر مسابقه، نتیجه را به دفتردار می‌دهد تا در دفتر بنویسد.
"""

import time

from rich.console import Console

from engine import Match, Question, RoundResult, ROUNDS, TIME_LIMIT
from storage import QuestionBank, ScoreBoard

console = Console()



def ask(player: str, question: Question, round_no: int) -> tuple[str, float]:
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


def hand_over(player: str) -> None:
    """صفحه را پاک می‌کند تا نفر دوم جواب نفر اول را نبیند."""
    console.clear()
    console.print(f"\n[bold magenta]نوبت {player} است.[/bold magenta]")
    console.print("بازیکن قبلی لطفاً نگاه نکند 🙈")
    input("\nوقتی آماده بودی Enter را بزن… ")


def show_round_result(match: Match, results: dict[str, RoundResult], question: Question) -> None:
    """نتیجه‌ی راند + تابلوی امتیاز."""
    console.clear()
    console.print(f"[bold]نتیجه‌ی راند {match.round}[/bold]")
    console.print(f"\n✅ جواب درست: [bold green]{question.correct}) {question.correct_text()}[/bold green]\n")

    for player in match.players:
        result = results[player]
        choice, elapsed = match.answer_of(player)     # ← از پنجره‌ی خواندنی می‌پرسیم

        if result.status == "correct":
            mark = "[bold green]✅ درست[/bold green]"
        elif result.status == "too_late":
            mark = "[bold red]⏰ دیر شد[/bold red]"
        else:
            mark = "[bold red]❌ غلط[/bold red]"

        console.print(
            f"  {player}: {choice.strip().upper()}  {mark}  "
            f"({elapsed:.1f} ثانیه)  →  [bold]+{result.points}[/bold]"
        )

    console.print("\n[bold cyan]تابلوی امتیاز:[/bold cyan]")
    for player in match.players:
        console.print(f"  {player}: [bold]{match.score_of(player)}[/bold]")

    input("\nEnter برای راند بعد… ")


def show_leaderboard(board: ScoreBoard) -> None:
    """رده‌بندیِ همه‌ی مسابقه‌ها — از دفتر خوانده می‌شود، نه از این اجرا."""
    console.print("\n[bold cyan]🏅 رده‌بندی کل[/bold cyan]")

    if board.is_empty():
        console.print("  هنوز هیچ مسابقه‌ای ثبت نشده.")
        return

    for rank, (name, stat) in enumerate(board.top(5), start=1):
        console.print(
            f"  {rank}) [bold]{name}[/bold] — "
            f"{stat['wins']} برد، {stat['points']} امتیاز"
        )


def show_final(match: Match) -> None:
    """تشریفات برنده."""
    console.clear()
    winner: str | None = match.winner()

    if winner is None:
        console.print("\n🤝 [bold yellow]مساوی شد![/bold yellow] هیچ‌کس نباخت.")
    else:
        console.print(f"\n🏆 [bold yellow]برنده: {winner}[/bold yellow] 🏆")

    console.print("\n[bold cyan]امتیاز نهایی:[/bold cyan]")
    for player in match.players:
        console.print(f"  {player}: [bold]{match.score_of(player)}[/bold]")


# ───────────────────────────────────────────── حلقه‌ی اصلی بازی

console.print("[bold cyan]Quiz Battle[/bold cyan]\n")

bank = QuestionBank()               # 📒 سؤال‌ها را از فایل بیاور
board = ScoreBoard()                # 📒 دفتر رده‌بندی را باز کن

console.print(f"[dim]بانک سؤال: {bank.count()} سؤال[/dim]\n")
show_leaderboard(board)
console.print()

name1: str = input("نام بازیکن اول: ").strip()
name2: str = input("نام بازیکن دوم: ").strip()

match = Match(name1, name2, bank.pick(ROUNDS))     # ۵ سؤال تصادفی

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

# 📒 نتیجه را در دفتر بنویس، بعد رده‌بندیِ تازه را نشان بده
board.record(
    match.winner(),
    match.players[0], match.score_of(match.players[0]),
    match.players[1], match.score_of(match.players[1]),
)
show_leaderboard(board)


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
#
# 🌱 و از امروز یک باگ عمدیِ دوم هم داریم: اگر questions.json خراب باشد یا نباشد،
#    بازی با یک صفحه‌ی قرمز می‌میرد. همان جلسه‌ی ۹.
#
# 🌱 و یک حس: این فایل حالا هم حرف می‌زند، هم از دفتردار جنس می‌گیرد.
#    آیا شغلش دو تا شد؟ این سؤال را نگه دارید تا جلسه‌ی ۱۱.
