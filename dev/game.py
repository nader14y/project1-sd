import time

from rich.console import Console  # pyright: ignore[reportMissingImports]

from engine import TIME_LIMIT, Match, Question, ROUNDS

console = Console()

questions = [
    Question("پایتخت ژاپن کدام است؟", ["توکیو", "کیوتو", "اوساکا", "سئول"], "A"),
    Question("خروجی len('سلام') چیست؟", ["3", "4", "5", "خطا"], "B"),
    Question("بزرگ‌ترین سیاره‌ی منظومه‌ی شمسی؟", ["زمین", "زحل", "مشتری", "نپتون"], "C"),
    Question("نماد شیمیایی طلا چیست؟", ["Ag", "Au", "Fe", "Gd"], "B"),
    Question("شاهنامه اثر کیست؟", ["حافظ", "سعدی", "فردوسی", "مولوی"], "C"),
]


def show_menu():
    console.print("\n⚔  Quiz Battle  ⚔", style="bold cyan")
    console.print("۱) بازی جدید", style="bold green")
    console.print("۲) خروج", style="bold red")


def ask(player, question, round_no):
    console.print(f"\nراند {round_no} از {ROUNDS}", style="bold cyan")
    console.print(f"نوبت {player} — ⏱ {TIME_LIMIT} ثانیه فرصت داری!", style="bold yellow")
    console.print(question.text, style="bold")
    for letter, option in zip("ABCD", question.options):
        console.print(f"  {letter}) {option}", style="bold")

    start = time.perf_counter()
    choice = input("جواب تو (A-D): ").strip().upper()
    elapsed = time.perf_counter() - start
    return choice, elapsed


def hand_over(player):
    console.print(f"\nنوبت {player} است.", style="bold magenta")
    console.print("بازیکن قبلی لطفاً نگاه نکند.")
    input("وقتی آماده بودی Enter را بزن… ")


def show_round_result(match, question):
    console.print(f"\nنتیجه‌ی راند {match.round}", style="bold")
    console.print(f"جواب درست: {question.correct}) {question.correct_text()}", style="bold green")

    for player in match.players:
        if player not in match.answers:
            console.print(f"  {player}: جواب نداد", style="red")
            continue

        choice, elapsed = match.answers[player]
        if elapsed > TIME_LIMIT:
            mark = "زمان تمام شد"
            style = "bold red"
        elif question.is_correct(choice):
            mark = "درست"
            style = "bold green"
        else:
            mark = "غلط"
            style = "bold red"

        console.print(f"  {player}: {choice}  {mark}  ({elapsed:.1f} ثانیه)", style=style)

    console.print("\nتابلوی امتیاز:", style="bold cyan")
    for player in match.players:
        console.print(f"  {player}: {match.scores[player]}", style="green")


def show_final(match):
    winner = match.winner()
    if winner is None:
        console.print("\nبازی به تساوی پایان یافت!", style="bold yellow")
    else:
        console.print(f"\nبرنده: {winner}", style="bold green")

    console.print("امتیاز نهایی:", style="bold")
    for player in match.players:
        console.print(f"  {player}: {match.scores[player]}", style="bold")


def ask_player_names():
    while True:
        name1 = input("نام بازیکن اول: ").strip() or "بازیکن 1"
        name2 = input("نام بازیکن دوم: ").strip() or "بازیکن 2"
        if name1 != name2:
            return name1, name2
        console.print("نام دو بازیکن باید متفاوت باشد.", style="bold yellow")


def play_match(player1, player2, bank=None):
    match = Match(player1, player2, bank or questions)

    while not match.is_over():
        question = match.start_round()
        if question is None:
            break

        for index, player in enumerate(match.players):
            if index == 1:
                hand_over(player)
            choice, elapsed = ask(player, question, match.round)
            match.submit(player, choice, elapsed)

        match.resolve_round()
        show_round_result(match, question)

    show_final(match)
    return match


def play():
    player1, player2 = ask_player_names()
    return play_match(player1, player2)


def main():
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


if __name__ == "__main__":
    main()
