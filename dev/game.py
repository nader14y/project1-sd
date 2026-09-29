import time
from rich.console import Console  # pyright: ignore[reportMissingImports]
from engine import Match, ROUNDS
from storage import QuestionBank, ScoreBoard

console = Console()


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


def play_match(questions, player1_name="بازیکن 1", player2_name="بازیکن 2"):
    match = Match(player1_name, player2_name, questions)

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
    if winner is None:
        console.print("\nبازی به تساوی پایان یافت!", style="bold yellow")
    else:
        console.print(f"\nبرنده: {winner}", style="bold green")

    console.print("امتیاز نهایی:", style="bold")
    for player in match.players:
        console.print(f"  {player}: {match.score_of(player)}", style="bold")

    return match


# Ask for Player names and then play match
def play(bank, board):
    player1_name = input("نام بازیکن اول: ").strip() or "بازیکن 1"
    player2_name = input("نام بازیکن دوم: ").strip() or "بازیکن 2"

    match = play_match(bank.pick(ROUNDS), player1_name, player2_name)

    board.record(
        match.winner(),
        match.players[0], match.score_of(match.players[0]),
        match.players[1], match.score_of(match.players[1]),
    )
    show_leaderboard(board)


def main():
    bank = QuestionBank()
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
    main()
