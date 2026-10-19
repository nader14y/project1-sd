# Quiz Battle

A two-player quiz game for the terminal. The game text is in Persian.

Each match has 5 rounds. In each round, both players answer the same multiple-choice question (A–D).

- A correct answer gets **10 points**.
- The fastest correct answer gets **+3 bonus** points.
- An answer that takes more than **30 seconds** gets 0 points.
- On a `"double"` power-up question, correct answers get double points.

A leaderboard, ranked by wins and then by points, is saved to `leaderboard.json`.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Play

```bash
python game.py
```

## Test

```bash
pytest
```

## Build an executable

Build a standalone program that runs without Python. Run the script inside the venv, on the system you are building for (PyInstaller cannot build a Windows `.exe` on a Mac, or the reverse).

- **Windows:** double-click `build.bat`, or run it in a terminal.
- **Mac:** `./build.sh`

The program is created in `dist/` (`QuizBattle.exe` on Windows, `QuizBattle` on Mac). To share it, put `questions.json` in the same folder as the program. The program creates `leaderboard.json` next to itself, and writes `quiz_game.log` in the folder it is started from.

On a Mac, the first time you open the program, right-click it and choose **Open**, because it is not signed. A program built on an Apple Silicon Mac does not run on an Intel Mac.

## Files

| File | Purpose |
|------|---------|
| `game.py` | Terminal UI (menu, rounds, leaderboard) |
| `engine.py` | Game rules: `Question`, `Match`, scoring |
| `storage.py` | `QuestionBank` (reads `questions.json`) and `ScoreBoard` (`leaderboard.json`) |
| `app_log.py` | Logging setup (writes to `quiz_game.log`) |
| `questions.json` | Question bank |
| `tests/` | pytest tests for the engine and storage |
| `build.bat` / `build.sh` | Build the executable on Windows / Mac |

## Adding questions

Add an entry to `questions.json`:

```json
{
  "text": "Question text",
  "options": ["A", "B", "C", "D"],
  "correct": "A",
  "power_up": "double"
}
```

Each question needs exactly 4 options, and `correct` must be a letter from A to D. `power_up` is optional.
