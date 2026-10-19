#!/bin/sh
# Build a Mac executable. Run inside the venv: ./build.sh
set -e
cd "$(dirname "$0")"

python -c "import PyInstaller" 2>/dev/null || pip install pyinstaller
pyinstaller --onefile --clean --noconfirm --name QuizBattle game.py

mkdir -p release
cp dist/QuizBattle questions.json README.md release/
echo "Done: release/ is ready."
