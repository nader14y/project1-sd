"""لایه‌ی نمایش — تنها جایی از پروژه که print و input دارد.

قانون جلسه‌ی ۶: مغز (game) هرگز اینجا را نمی‌شناسد؛ اینجا مغز را می‌شناسد.
قانون جلسه‌ی ۱۴: زیباسازی بازی فقط در همین پوشه اتفاق می‌افتد.
"""

import time

from rich.align import Align
from rich.console import Console, Group
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich import box

from config import (
    APP_NAME,
    APP_VERSION,
    LETTERS,
    POWER_UPS,
    ROUNDS,
    SPEED_BONUS,
    STEAL_AMOUNT,
    TIME_LIMIT,
)

console = Console()

_FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")

BANNER = r"""
  ___  _   _ ___ ____    ___    _ _____ _____ _    ___
 / _ \| | | |_ _|_  /   | _ )  /_\_   _|_   _| |  | __|
| (_) | |_| || | / /    | _ \ / _ \| |   | | | |__| _|
 \__\_\\___/|___/___|   |___//_/ \_\_|   |_| |____|___|
"""


def fa(value) -> str:
    """عدد را با رقم‌های فارسی نشان می‌دهد."""
    return str(value).translate(_FA_DIGITS)


def fa_secs(seconds: float) -> str:
    """زمان را با رقم و ممیز فارسی نشان می‌دهد — مثل «۱۲٫۴s»."""
    return fa(f"{seconds:.1f}").replace(".", "٫") + "s"


# ───────────────────────────────────────────────────────────── صفحه‌های عمومی


def clear() -> None:
    console.clear()


def banner() -> None:
    """صفحه‌ی افتتاحیه‌ی بازی."""
    clear()
    console.print(Text(BANNER, style="bold cyan"), justify="center")
    console.print(
        Align.center(
            Text(f"⚔  مسابقه‌ی دونفره‌ی دانستنی‌ها  ⚔   نسخه‌ی {fa(APP_VERSION)}", style="bold yellow")
        )
    )
    console.print()


def main_menu() -> str:
    """منوی اصلی را نشان می‌دهد و انتخاب معتبر کاربر را برمی‌گرداند."""
    menu = Group(
        Text("۱) شروع مسابقه‌ی جدید", style="bold green"),
        Text("۲) رده‌بندی کل", style="bold cyan"),
        Text("۳) قوانین بازی", style="bold magenta"),
        Text("۴) خروج", style="bold red"),
    )
    console.print(Panel(menu, title=f"[bold]{APP_NAME}[/bold]", border_style="cyan",
                        box=box.ROUNDED, padding=(1, 4), width=54))
    return _ask_choice("انتخاب تو (۱ تا ۴): ", valid="1234", hint="فقط عددهای ۱ تا ۴")


def show_rules() -> None:
    """۵ قانون محصول + قدرت‌های ویژه."""
    clear()
    rules = [
        f"۱. هر راند، هر دو بازیکن به [bold]همان سؤال[/bold] جواب می‌دهند؛ "
        f"نتیجه بعد از جواب هر دو اعلام می‌شود.",
        f"۲. جواب درست = [bold green]۱۰[/bold green] امتیاز. بین درست‌جواب‌ها، "
        f"سریع‌تر [bold green]+{fa(SPEED_BONUS)}[/bold green] بونوس سرعت می‌گیرد.",
        f"۳. حدود یکی از هر سه سؤال، یک [bold]قدرت ویژه[/bold] دارد.",
        f"۴. هر مسابقه دقیقاً [bold]{fa(ROUNDS)}[/bold] راند؛ هر جواب "
        f"[bold]{fa(TIME_LIMIT)}[/bold] ثانیه مهلت — دیرتر یعنی صفر.",
        f"۵. بعد از راند {fa(ROUNDS)} برنده اعلام می‌شود. فقط رده‌بندی کل ذخیره می‌ماند.",
    ]
    console.print(Panel("\n\n".join(rules), title="[bold]قوانین بازی[/bold]",
                        border_style="cyan", box=box.ROUNDED, padding=(1, 3)))

    table = Table(box=box.SIMPLE_HEAD, show_edge=False, padding=(0, 2))
    table.add_column("قدرت ویژه", style="bold")
    table.add_column("چه می‌کند؟")
    for emoji, name, description in POWER_UPS.values():
        table.add_row(f"{emoji} {name}", fa(description))
    console.print(Panel(table, title="[bold]قدرت‌های ویژه[/bold]",
                        border_style="yellow", box=box.ROUNDED, padding=(1, 3)))
    _pause()


def show_leaderboard(board) -> None:
    """رده‌بندی کل بین همه‌ی اجراها."""
    clear()
    if board.is_empty():
        console.print(Panel("هنوز هیچ مسابقه‌ای ثبت نشده. اولین نفر باش! 🏁",
                            border_style="yellow", box=box.ROUNDED, padding=(1, 3)))
        _pause()
        return

    table = Table(title="🏆  رده‌بندی کل  🏆", box=box.ROUNDED, border_style="cyan",
                  title_style="bold yellow")
    table.add_column("رتبه", justify="center", style="bold")
    table.add_column("بازیکن", style="bold white")
    table.add_column("برد", justify="center", style="green")
    table.add_column("مساوی", justify="center", style="yellow")
    table.add_column("بازی", justify="center", style="dim")
    table.add_column("مجموع امتیاز", justify="center", style="bold cyan")

    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    for rank, (name, row) in enumerate(board.top(10), start=1):
        table.add_row(
            medals.get(rank, fa(rank)),
            name,
            fa(row["wins"]),
            fa(row.get("draws", 0)),
            fa(row.get("played", 0)),
            fa(row["points"]),
        )
    console.print(table)
    _pause()


def goodbye() -> None:
    console.print()
    console.print(Align.center(Text("خداحافظ! 👋  دوباره بیا مسابقه بده.", style="bold cyan")))
    console.print()


# ────────────────────────────────────────────────────────────────── مسابقه


def ask_names(match_factory):
    """نام دو بازیکن را می‌گیرد و مسابقه می‌سازد؛ تا وقتی ورودی درست شود، می‌پرسد.

    مغز با raise حرف می‌زند، دهان ترجمه می‌کند و دوباره می‌پرسد (قانون جلسه‌ی ۱۰).
    """
    clear()
    console.print(Panel("اسم دو بازیکن را وارد کنید — بعد نوبتی پشت همین کیبورد بازی می‌کنید.",
                        title="[bold]بازیکن‌ها[/bold]", border_style="cyan",
                        box=box.ROUNDED, padding=(1, 3)))
    while True:
        name1 = _ask_text("👤 نام بازیکن اول: ")
        name2 = _ask_text("👤 نام بازیکن دوم: ")
        try:
            return match_factory(name1, name2)
        except ValueError as e:
            console.print(f"⚠️  {e} — دوباره امتحان کنید.", style="bold yellow")
            console.print()


def announce_round(match, question) -> None:
    """شروع راند: شماره‌ی راند، تابلوی امتیاز کوچک، و اعلام قدرت ویژه."""
    clear()
    console.print(Rule(f"[bold cyan]راند {fa(match.round)} از {fa(ROUNDS)}[/bold cyan]",
                       style="cyan"))
    console.print(Align.center(_mini_score(match)))
    console.print()
    if question.power_up:
        emoji, name, description = POWER_UPS[question.power_up]
        console.print(Align.center(
            Panel(Text(f"{emoji}  سؤال {name}!  {emoji}\n{fa(description)}",
                       style="bold yellow", justify="center"),
                  border_style="yellow", box=box.DOUBLE, padding=(0, 2), width=64)
        ))
        console.print()
    time.sleep(0.6)


def hand_over(player: str) -> None:
    """صفحه را پاک می‌کند تا نفر دوم از جواب نفر اول سرنخ نگیرد."""
    clear()
    console.print()
    console.print(Align.center(
        Panel(Text(f"نوبت {player} است.\nبازیکن قبلی لطفاً نگاه نکند 🙈",
                   style="bold magenta", justify="center"),
              border_style="magenta", box=box.ROUNDED, padding=(1, 2), width=54)
    ))
    input("\n   وقتی آماده بودی Enter را بزن… ")


def ask_answer(match, question, player: str) -> tuple[str, float]:
    """سؤال را نشان می‌دهد، جواب می‌گیرد، و زمان پاسخ‌گویی را برمی‌گرداند.

    کرنومتر اینجاست، نه در موتور — همین است که تست‌های جلسه‌ی ۷ را ممکن می‌کند.
    """
    clear()
    console.print(Rule(f"[cyan]راند {fa(match.round)} از {fa(ROUNDS)}[/cyan]", style="cyan"))

    header = f"[bold yellow]نوبت {player}[/bold yellow]"
    if question.power_up:
        emoji, name, _ = POWER_UPS[question.power_up]
        header += f"   {emoji} [bold]{name}[/bold]"
    if match.shields.get(player, 0):
        header += f"   🛡️ ×{fa(match.shields[player])}"
    console.print(Align.center(header))
    console.print()

    console.print(Panel(Text(question.text, style="bold white"),
                        title=f"[cyan]سؤال {fa(match.round)}[/cyan]",
                        border_style="cyan", box=box.ROUNDED, padding=(1, 3)))

    options = Table(box=None, show_header=False, padding=(0, 1))
    options.add_column(style="bold cyan", justify="right", width=3)
    options.add_column(style="white")
    for letter, option in zip(LETTERS, question.options):
        options.add_row(f"{letter})", option)
    console.print(options)

    console.print(f"\n⏱  [dim]{fa(TIME_LIMIT)} ثانیه فرصت داری[/dim]")
    start = time.time()
    choice = _ask_choice("   جواب تو (A-D): ", valid=LETTERS, hint="فقط حرف‌های A تا D")
    elapsed = time.time() - start

    console.print(f"   {_time_bar(elapsed)}")
    time.sleep(0.7)
    return choice, elapsed


def show_round_result(match, summary) -> None:
    """نتیجه‌ی راند: جواب هر دو، امتیاز راند، و تابلوی امتیاز."""
    clear()
    question = summary["question"]

    console.print(Rule(f"[bold]نتیجه‌ی راند {fa(summary['round'])}[/bold]", style="cyan"))
    console.print()
    console.print(Panel(Text(question.text, style="white"),
                        subtitle=f"[bold green]✅ جواب درست: {question.correct}) "
                                 f"{question.correct_option}[/bold green]",
                        border_style="green", box=box.ROUNDED, padding=(1, 3)))
    console.print()

    table = Table(box=box.ROUNDED, border_style="cyan", show_lines=False)
    table.add_column("بازیکن", style="bold white")
    table.add_column("جواب", justify="center")
    table.add_column("زمان", justify="center", style="dim")
    table.add_column("امتیاز راند", justify="center", style="bold")
    table.add_column("مجموع", justify="center", style="bold cyan")

    marks = {"correct": "[green]✅ درست[/green]",
             "wrong": "[red]❌ غلط[/red]",
             "too_late": "[red]⏰ دیر[/red]"}

    for player in match.players:
        row = summary["results"][player]
        gained = row["points"] - row["lost_to_steal"]
        color = "green" if gained > 0 else "red" if gained < 0 else "dim"
        sign = "+" if gained > 0 else ""
        table.add_row(
            player,
            f"{row['choice']}  {marks[row['status']]}",
            fa_secs(row["elapsed"]),
            f"[{color}]{sign}{fa(gained)}[/{color}]",
            fa(summary["scores"][player]),
        )
    console.print(table)

    for note in _round_notes(match, summary):
        console.print(f"   {note}")

    _pause("   Enter برای راند بعد… ")


def show_final(match, board_entry_saved: bool = True) -> None:
    """پایان مسابقه: تشریفات برنده + مرور راندها."""
    clear()
    winner = match.winner()
    console.print()

    if winner is None:
        body = Text("🤝  مساوی شد!  🤝\n\nهیچ‌کس نباخت — ری‌مچ؟",
                    style="bold yellow", justify="center")
    else:
        loser = match.rival_of(winner)
        body = Text(
            f"🏆  برنده: {winner}  🏆\n\n"
            f"{winner}: {fa(match.scores[winner])}   |   "
            f"{loser}: {fa(match.scores[loser])}",
            style="bold yellow", justify="center")

    console.print(Align.center(
        Panel(body, border_style="yellow", box=box.DOUBLE, padding=(1, 2), width=60)
    ))

    console.print()
    review = Table(title="مرور مسابقه", box=box.ROUNDED, border_style="cyan",
                   title_style="bold cyan")
    review.add_column("راند", justify="center", style="bold")
    review.add_column("قدرت ویژه", justify="center")
    for player in match.players:
        review.add_column(player, justify="center")

    for summary in match.history:
        power_up = summary["question"].power_up
        # در جدول، نامِ متنی می‌گذاریم نه ایموجی: عرض ایموجی‌ها در ترمینال‌های
        # مختلف یکسان نیست و ستون‌ها را به هم می‌ریزد.
        label = POWER_UPS[power_up][1] if power_up else "—"
        cells = []
        for player in match.players:
            row = summary["results"][player]
            gained = row["points"] - row["lost_to_steal"]
            style = "green" if gained > 0 else "red" if gained < 0 else "dim"
            sign = "+" if gained > 0 else ""
            cells.append(f"[{style}]{sign}{fa(gained)}[/{style}]")
        review.add_row(fa(summary["round"]), label, *cells)

    review.add_row("[bold]کل[/bold]", "",
                   *[f"[bold cyan]{fa(match.scores[p])}[/bold cyan]" for p in match.players])
    console.print(review)

    if board_entry_saved:
        console.print("\n   [dim]نتیجه در رده‌بندی کل ثبت شد.[/dim]")


def ask_rematch() -> bool:
    """ری‌مچ با همان بازیکن‌ها؟"""
    answer = _ask_choice("\n   ری‌مچ با همین بازیکن‌ها؟ (y/n): ", valid="YN",
                         hint="فقط y یا n")
    return answer == "Y"


# ───────────────────────────────────────────────────────────────── کمکی‌ها


def _mini_score(match) -> Text:
    """تابلوی امتیاز یک‌خطی برای بالای هر راند."""
    parts = []
    for player in match.players:
        shield = " 🛡️" * match.shields.get(player, 0)
        parts.append(f"{player}: {fa(match.scores[player])}{shield}")
    return Text("   ⚔   ".join(parts), style="bold cyan")


def _time_bar(elapsed: float, width: int = 24) -> str:
    """نوار زمان مصرف‌شده — سبز، زرد، یا قرمز."""
    ratio = min(elapsed / TIME_LIMIT, 1.0)
    filled = int(round(ratio * width))
    if elapsed > TIME_LIMIT:
        color, label = "bold red", f"{fa_secs(elapsed)} — دیر شد!"
    elif ratio < 0.5:
        color, label = "green", fa_secs(elapsed)
    elif ratio < 0.85:
        color, label = "yellow", fa_secs(elapsed)
    else:
        color, label = "red", fa_secs(elapsed)
    return f"[{color}]{'█' * filled}{'░' * (width - filled)}[/{color}] [dim]{label}[/dim]"


def _round_notes(match, summary) -> list[str]:
    """جمله‌های اتفاق‌های ویژه‌ی راند — جمله‌سازی کار همین لایه است."""
    notes = []
    for player in match.players:
        row = summary["results"][player]
        if row["speed_bonus"]:
            notes.append(f"[green]⚡ {player} سریع‌تر بود: +{fa(SPEED_BONUS)} بونوس سرعت.[/green]")
        if row["doubled"]:
            notes.append(f"[yellow]⚡ امتیاز {player} دوبرابر شد![/yellow]")
        if row["stole"]:
            notes.append(f"[magenta]🎯 {player} از حریفش {fa(STEAL_AMOUNT)} امتیاز دزدید![/magenta]")
        if row["shield_used"]:
            notes.append(f"[cyan]🛡️ سپر {player} سرقت را خنثی کرد![/cyan]")
        if row["shield_gained"]:
            notes.append(f"[cyan]🛡️ {player} یک سپر گرفت — جلوی سرقت بعدی را می‌گیرد.[/cyan]")
    return notes


def _ask_text(prompt: str) -> str:
    """یک متن غیرخالی می‌گیرد."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        console.print("   ⚠️  نمی‌تواند خالی باشد.", style="yellow")


def _ask_choice(prompt: str, valid: str, hint: str) -> str:
    """تا وقتی یکی از حرف‌ها/عددهای مجاز وارد نشود، دوباره می‌پرسد."""
    while True:
        value = input(prompt).strip().upper()
        if value in valid:
            return value
        console.print(f"   ⚠️  {hint}.", style="yellow")


def _pause(prompt: str = "\n   Enter برای ادامه… ") -> None:
    input(prompt)
