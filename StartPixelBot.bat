@echo off
cd /d "%~dp0"

echo ==========================================
echo      Uruchamianie Pixel Bot Tibia
echo ==========================================

:: 1. Sprawdz czy Python jest zainstalowany
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [BLAD] Nie znaleziono Pythona!
    echo Prosze zainstalowac Python 3.10 lub nowszy.
    echo Pamietaj aby zaznaczyc opcje "Add Python to PATH" podczas instalacji.
    pause
    exit /b
)

:: 2. Sprawdz czy istnieje wirtualne srodowisko (venv)
if not exist venv (
    echo [INFO] Tworzenie wirtualnego srodowiska (pierwsze uruchomienie)...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [BLAD] Nie udalo sie stworzyc venv.
        pause
        exit /b
    )
)

:: 3. Aktywuj venv
call venv\Scripts\activate.bat

:: 4. Zainstaluj biblioteki (jesli to pierwsze uruchomienie lub brakuje)
echo [INFO] Sprawdzanie bibliotek...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Instalowanie wymaganych bibliotek (moze to chwile potrwac)...
    pip install -r requirements.txt
)

:: 5. Uruchom bota
echo [SUKCES] Uruchamianie bota...
python main.py

pause
