# مرحله‌ی ۱ (دقیقه‌ی ۴۵ تا ۵۲) — سه ابزار rich، در یک فایل جدا
#
# ⚠️ این فایل عمداً جدا از بازی است: اول ابزار را بشناسند، بعد در بازی به کارش ببرند.
#    فایل را کنار game.py بسازند، به اسم rich_test.py
#
# پیش‌نیاز: (venv) باید در ترمینال دیده شود و rich نصب شده باشد.

from rich.console import Console

console = Console()

# ابزار ۱ — console.print به‌جای print
console.print("سلام! این خط با rich چاپ شده.")

# ابزار ۲ — رنگ کل خط با style
console.print("✅ درست!", style="bold green")
console.print("❌ غلط! جواب درست: C", style="bold red")
console.print("🏁 بازی تمام شد!", style="bold yellow")

# ابزار ۳ — رنگ بخشی از خط با تگ
console.print("[bold cyan]سؤال ۲ از ۵[/bold cyan] — بزرگ‌ترین سیاره؟")
console.print("امتیاز تو: [bold green]30[/bold green] از [bold]50[/bold]")


# ─────────────────────────────────────────────────────────────────────
# ۳ دقیقه بازی کنید: رنگ‌ها را عوض کنید.
#     red · green · yellow · blue · cyan · magenta · white
#     و ترکیبشان با  bold  →  "bold magenta"
#
# 🔒 مرز امروز: فقط همین سه ابزار.
#    rich کادر و جدول و نوار پیشرفت هم دارد — عمقش مال جلسه‌ی ۱۱ است.
#
# ⚠️ خطای رایج امروز:
#     ModuleNotFoundError: No module named 'rich'
#     یعنی (venv) فعال نیست — نه اینکه rich نصب نشده.
#     حل:  venv\Scripts\activate
