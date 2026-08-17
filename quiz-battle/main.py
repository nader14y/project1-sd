"""نقطه‌ی شروع Quiz Battle — فقط راه‌اندازی و منو.

اجرا:
    python main.py             بازی معمولی
    python main.py --demo      مسابقه‌ی از پیش‌چیده‌شده برای دموی کلاس
"""

import logging
import sys

from config import APP_NAME, APP_VERSION, LOG_PATH, ROUNDS
from game.match import Match
from game.question_bank import QuestionBank
from storage.scoreboard import ScoreBoard
from ui import console as ui

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """لاگ فقط داخل فایل — خروجیِ کاربر و خروجیِ کارآگاه، دو کانال جدا."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8")],
    )


def init_monitoring() -> None:
    """اگر Sentry نصب و DSN تنظیم شده باشد، مانیتورینگ خطا را روشن می‌کند."""
    import os

    dsn = os.environ.get("SENTRY_DSN", "")
    if not dsn:
        return
    try:
        import sentry_sdk
    except ImportError:
        logger.warning("SENTRY_DSN تنظیم شده اما sentry-sdk نصب نیست")
        return
    sentry_sdk.init(dsn=dsn, release=APP_VERSION)
    logger.info("Sentry فعال شد")


def play(bank: QuestionBank, board: ScoreBoard, demo: bool = False) -> None:
    """یک مسابقه‌ی کامل، از گرفتن نام تا ثبت نتیجه — با امکان ری‌مچ."""
    questions = bank.demo_set() if demo else bank.pick(ROUNDS)
    match = ui.ask_names(lambda n1, n2: Match(n1, n2, questions))
    players = tuple(match.players)

    while True:
        logger.info("مسابقه شروع شد: %s vs %s", *players)

        while not match.is_over():
            question = match.start_round()
            ui.announce_round(match, question)
            for index, player in enumerate(match.players):
                if index:
                    ui.hand_over(player)
                choice, elapsed = ui.ask_answer(match, question, player)
                match.submit(player, choice, elapsed)
            summary = match.resolve_round()
            logger.info("راند %s: %s", summary["round"], summary["scores"])
            ui.show_round_result(match, summary)

        winner = match.winner()
        board.record_result(
            winner,
            players[0], match.scores[players[0]],
            players[1], match.scores[players[1]],
        )
        logger.info("پایان مسابقه — برنده: %s | امتیازها: %s", winner or "مساوی", match.scores)
        ui.show_final(match)

        if not ui.ask_rematch():
            return
        questions = bank.demo_set() if demo else bank.pick(ROUNDS)
        match = Match(players[0], players[1], questions)


def main() -> int:
    setup_logging()
    init_monitoring()
    demo = "--demo" in sys.argv
    logger.info("%s نسخه‌ی %s اجرا شد (demo=%s)", APP_NAME, APP_VERSION, demo)

    try:
        bank = QuestionBank()
    except (FileNotFoundError, ValueError) as e:
        logger.error("بانک سؤال خوانده نشد: %s", e)
        ui.console.print(f"⛔ بانک سؤال خوانده نشد:\n   {e}", style="bold red")
        return 1

    board = ScoreBoard()
    ui.banner()
    if demo:
        ui.console.print("   [dim]حالت دمو: سؤال‌ها از پیش چیده شده‌اند.[/dim]\n")

    while True:
        choice = ui.main_menu()
        if choice == "1":
            play(bank, board, demo=demo)
            ui.banner()
        elif choice == "2":
            ui.show_leaderboard(board)
            ui.banner()
        elif choice == "3":
            ui.show_rules()
            ui.banner()
        elif choice == "4":
            ui.goodbye()
            return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        # Ctrl+C هم یک Exception است — خروج تمیز، نه صفحه‌ی قرمز.
        ui.goodbye()
        sys.exit(0)
