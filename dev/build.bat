@echo off
REM ساخت فایل اجرایی ویندوزی — جلسه‌ی ۱۱
REM این فایل را کنار game.py بگذارید و دوبار کلیک کنید.

echo.
echo === ۱/۳  چک کردن محیط ===
python -c "import PyInstaller" 2>nul || pip install pyinstaller
echo.

echo === ۲/۳  ساختن exe (ممکن است ۱ تا ۳ دقیقه طول بکشد) ===
pyinstaller --onefile --clean --noconfirm --name QuizBattle game.py
echo.

echo === ۳/۳  ساختن بسته‌ی تحویل ===
if not exist release mkdir release
copy /Y dist\QuizBattle.exe release\ >nul
copy /Y questions.json       release\ >nul
copy /Y README.md            release\ >nul 2>nul

echo.
echo ========================================
echo   تمام شد. پوشه‌ی release آماده است:
echo     QuizBattle.exe
echo     questions.json
echo     README.md
echo ========================================
echo.
echo حالا پوشه‌ی release را روی فلش بگذار و به دوستت بده.
pause
