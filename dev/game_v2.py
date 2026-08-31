import time

from rich.console import Console  # pyright: ignore[reportMissingImports]

from engine import Match, Question, POINTS, ROUNDS, TIME_LIMIT

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


def prompt_choice(player_name, question):
    console.print(f"\n{player_name}", style="bold cyan")
    console.print(question.text, style="bold")
    for letter, option in zip("ABCD", question.options):
        console.print(f"  {letter}) {option}", style="bold")

    start = time.perf_counter()
    choice = input("جواب تو (A-D): ").strip().upper()
    elapsed = time.perf_counter() - start

    if choice not in "ABCD":
        console.print("لطفاً فقط یکی از گزینه‌های A تا D را وارد کن.", style="yellow")
        return prompt_choice(player_name, question)

    return choice, elapsed


def play_match(player1_name="بازیکن 1", player2_name="بازیکن 2"):
    match = Match(player1_name, player2_name, questions)

    while not match.is_over():
        question = match.start_round()
        if question is None:
            break

        console.print(f"\nراند {match.round} از {ROUNDS}", style="bold yellow")

        player1_choice, player1_elapsed = prompt_choice(player1_name, question)
        player2_choice, player2_elapsed = prompt_choice(player2_name, question)

        match.submit(player1_name, player1_choice, player1_elapsed)
        match.submit(player2_name, player2_choice, player2_elapsed)
        match.resolve_round()

        console.print("\nامتیاز فعلی:", style="bold")
        for player in match.players:
            console.print(f"  {player}: {match.scores[player]}", style="green")

        for player in match.players:
            if player not in match.answers:
                continue
            choice, elapsed = match.answers[player]
            if elapsed > TIME_LIMIT:
                console.print(f"  {player}: زمان تمام شد", style="red")
                continue
            if question.is_correct(choice):
                console.print(f"  {player}: درست ({choice})", style="green")
            else:
                console.print(f"  {player}: اشتباه — جواب درست: {question.correct_text()}", style="red")

    winner = match.winner()
    if winner is None:
        console.print("\nبازی به تساوی پایان یافت!", style="bold yellow")
    else:
        console.print(f"\nبرنده: {winner}", style="bold green")

    console.print("امتیاز نهایی:", style="bold")
    for player in match.players:
        console.print(f"  {player}: {match.scores[player]}", style="bold")

    return match


def play():
    player1_name = input("نام بازیکن اول: ").strip() or "بازیکن 1"
    player2_name = input("نام بازیکن دوم: ").strip() or "بازیکن 2"
    play_match(player1_name, player2_name)

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