"""👄 دهانِ بازی.  ✅ وضعیت مطلوب پایان جلسه‌ی ۱۰

🆕 امروز بازی یاد گرفت **نمیرد**. چهار جا:

    ۱) نام تکراری        → دوباره می‌پرسد   (باگ عمدی از جلسه‌ی ۴)
    ۲) بانک سؤال خراب/نبود → پیام روشن و خروج تمیز
    ۳) Ctrl+C             → خداحافظی، نه صفحه‌ی قرمز
    ۴) هر خطای پیش‌بینی‌نشده → پیام کوتاه برای کاربر + جزئیات کامل در game.log

⚠️ قانون امروز: هر `except` **نوع‌دار** است و **واکنش** دارد.
   `except:` خالی یعنی «هر خطایی را قورت بده» — یعنی باگ را قایم کن.
"""

import logging
import time

from rich.console import Console  # pyright: ignore[reportMissingImports]

from engine import Match, ROUNDS
from storage import QuestionBank, ScoreBoard

console = Console()

# 📝 لاگ فقط داخل فایل می‌رود — خروجیِ کاربر و خروجیِ کارآگاه، دو کانالِ جدا
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("game.log", encoding="utf-8")],
)


def show_menu():
    console.print("\nQuiz Battle", style="bold cyan")
    console.print("۱) بازی جدید", style="bold green")
    console.print("۲) خروج", style="bold red")


def show_leaderboard(board):
    console.print("\nرده‌بندی کل", style="bold cyan")

    if board.is_empty():
        console.print("  هنوز هیچ مسابقه‌ای ثبت نشده.")
        return

    for rank, (name, stat) in enumerate(board.top(5), start=1):
        console.print(f"  {rank}) {name} — {stat['wins']} برد، {stat['points']} امتیاز")


def prompt_choice(player_name, question):
    console.print(f"\n{player_name}", style="bold cyan")
    console.print(question.text, style="bold")
    for letter, option in zip("ABCD", question.options):
        console.print(f"  {letter}) {option}", style="bold")

    while True:
        start = time.perf_counter()
        choice = input("جواب تو (A-D): ").strip().upper()
        elapsed = time.perf_counter() - start

        if choice in ("A", "B", "C", "D"):
            return choice, elapsed

        console.print("لطفاً فقط یکی از گزینه‌های A تا D را وارد کن.", style="yellow")


def play_match(match):
    logging.info("مسابقه شروع شد: %s vs %s", match.players[0], match.players[1])

    while not match.is_over():
        question = match.start_round()
        console.print(f"\nراند {match.round} از {ROUNDS}", style="bold yellow")

        for player in match.players:
            choice, elapsed = prompt_choice(player, question)
            match.submit(player, choice, elapsed)

        results = match.resolve_round()

        for player, result in results.items():
            if result.status == "too_late":
                console.print(f"  {player}: زمان تمام شد", style="red")
            elif result.status == "correct":
                console.print(f"  {player}: درست (+{result.points})", style="green")
            else:
                console.print(
                    f"  {player}: اشتباه — جواب درست: {question.correct_text()}", style="red"
                )

        console.print("\nامتیاز فعلی:", style="bold")
        for player in match.players:
            console.print(f"  {player}: {match.score_of(player)}", style="green")

    winner = match.winner()
    logging.info(
        "مسابقه تمام شد. برنده: %s | %s",
        winner or "مساوی",
        {p: match.score_of(p) for p in match.players},
    )

    if winner is None:
        console.print("\nبازی به تساوی پایان یافت!", style="bold yellow")
    else:
        console.print(f"\nبرنده: {winner}", style="bold green")

    console.print("امتیاز نهایی:", style="bold")
    for player in match.players:
        console.print(f"  {player}: {match.score_of(player)}", style="bold")

    return match


def ask_names(questions):
    """تا وقتی موتور مسابقه را قبول نکند، دوباره می‌پرسد.

    ⭐ دقت کنید قاعده را **دو جا ننوشتیم**: موتور می‌داند دو هم‌نام ممنوع است،
       و دهان فقط فریادش را می‌گیرد و دوباره می‌پرسد. اگر فردا قاعده عوض شود،
       فقط یک جا عوض می‌شود.
    """
    while True:
        player1_name = input("نام بازیکن اول: ").strip() or "بازیکن 1"
        player2_name = input("نام بازیکن دوم: ").strip() or "بازیکن 2"

        try:
            return Match(player1_name, player2_name, questions)
        except ValueError as error:
            logging.warning("ساختن مسابقه نشد: %s", error)
            console.print(f"⛔ {error}", style="bold red")
            console.print("دوباره امتحان کن.\n", style="yellow")


# Ask for Player names and then play match
def play(bank, board):
    match = play_match(ask_names(bank.pick(ROUNDS)))

    board.record(
        match.winner(),
        match.players[0], match.score_of(match.players[0]),
        match.players[1], match.score_of(match.players[1]),
    )
    show_leaderboard(board)


def main():
    logging.info("بازی اجرا شد")

    try:
        bank = QuestionBank()
    except FileNotFoundError as error:
        console.print(f"⛔ {error}", style="bold red")
        console.print("فایل questions.json باید کنار game.py باشد.", style="yellow")
        logging.error("بانک سؤال پیدا نشد: %s", error)
        return
    except ValueError as error:
        console.print(f"⛔ {error}", style="bold red")
        console.print("فایل را در VS Code باز کن و Shift+Alt+F بزن.", style="yellow")
        logging.error("بانک سؤال خراب است: %s", error)
        return

    board = ScoreBoard()
    show_leaderboard(board)

    while True:
        show_menu()
        choice = input("انتخاب تو (۱ یا ۲): ").strip()

        if choice in ("1", "۱"):
            play(bank, board)
        elif choice in ("2", "۲"):
            console.print("خداحافظ!", style="bold cyan")
            break
        else:
            console.print(" فقط ۱ یا ۲ را وارد کن.", style="bold yellow")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Ctrl+C هم یک خطاست — خروجِ تمیز، نه صفحه‌ی قرمز.
        console.print("\nخداحافظ!", style="bold cyan")
    except Exception as error:
        # 🥅 تورِ آخر: هر چیزی که پیش‌بینی نکرده بودیم.
        #    کاربر یک جمله می‌بیند، کارآگاه همه‌چیز را در game.log دارد.
        console.print("\n⛔ یک مشکل پیش‌بینی‌نشده پیش آمد و بازی بسته شد.", style="bold red")
        console.print("جزئیاتش در فایل game.log نوشته شد.", style="yellow")
        logging.exception("خطای پیش‌بینی‌نشده: %s", error)
