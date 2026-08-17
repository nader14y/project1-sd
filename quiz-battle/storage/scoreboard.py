"""رده‌بندی کل — تنها داده‌ای که بین اجراها می‌ماند.

قانون جلسه‌ی ۵: وضعیت خودِ مسابقه عمداً ذخیره نمی‌شود؛ مسابقه در همان اجرا
تمام می‌شود. فقط چیزی می‌ماند که از دست رفتنش واقعاً فاجعه باشد.
"""

import json
from pathlib import Path

from config import LEADERBOARD_PATH


class ScoreBoard:
    """برد و مجموع امتیاز هر بازیکن، در طول همه‌ی مسابقه‌ها."""

    def __init__(self, path: str | Path = LEADERBOARD_PATH):
        self._path = Path(path)
        self._data: dict[str, dict] = {}
        if self._path.exists():
            try:
                with open(self._path, encoding="utf-8") as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, OSError):
                # رده‌بندی خراب، دلیل خوبی برای مردنِ بازی نیست: از نو شروع می‌کنیم.
                self._data = {}

    def record_result(
        self, winner: str | None, p1: str, s1: int, p2: str, s2: int
    ) -> None:
        """نتیجه‌ی یک مسابقه را در رده‌بندی ثبت و ذخیره می‌کند."""
        for name, points in ((p1, s1), (p2, s2)):
            entry = self._data.setdefault(name, {"wins": 0, "draws": 0, "played": 0, "points": 0})
            entry["points"] += points
            entry["played"] += 1
        if winner is None:
            self._data[p1]["draws"] += 1
            self._data[p2]["draws"] += 1
        else:
            self._data[winner]["wins"] += 1
        self._save()

    def top(self, n: int = 10) -> list[tuple[str, dict]]:
        """n نفر برتر: اول بیشترین برد، بعد بیشترین امتیاز."""
        return sorted(
            self._data.items(),
            key=lambda kv: (kv[1]["wins"], kv[1]["points"]),
            reverse=True,
        )[:n]

    def is_empty(self) -> bool:
        return not self._data

    def _save(self) -> None:
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)
