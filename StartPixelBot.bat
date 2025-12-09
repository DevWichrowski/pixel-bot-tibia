@echo off
cd /d "%~dp0"

echo ==========================================
echo      Uruchamianie Pixel Bot Tibia
echo ==========================================

echo [1/4] Sprawdzanie Pythona...
python --version
if errorlevel 1 (
    echo [BLAD] Nie znaleziono Pythona lub nie dodano do PATH.
    echo Zainstaluj Python ze strony python.org i zaznacz "Add to PATH".
    pause
    exit /b
)

echo [2/4] Sprawdzanie venv...
if not exist venv (
    echo [INFO] Tworzenie venv...
    python -m venv venv
)

echo [3/4] Aktywacja venv...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo [BLAD] Nie udalo sie znalezc venv\Scripts\activate.bat.
    echo Sprobuj usunac folder 'venv' i uruchomic ponownie.
    pause
    exit /b
)

echo [4/4] Instalacja bibliotek...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo ==========================================
echo      STARTOWANIE BOTA...
echo ==========================================
python main.py

echo.
echo [KONIEC] Aplikacja zakonczyla dzialanie.
pause
