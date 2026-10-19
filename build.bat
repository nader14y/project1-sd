python -c "import PyInstaller" 2>nul || pip install pyinstaller
pyinstaller --onefile --clean --noconfirm --name QuizBattle game.py
