@ECHO OFF
REM GoodPay GUI'yi baslat - Yonetici olarak calistirmak icin sag tik > Yonetici olarak calistir

cd /d "%~dp0"

REM Python kontrolu
python --version >nul 2>&1
if errorlevel 1 (
    echo Python bulunamadi! Lutfen Python yukleyin: https://www.python.org/downloads/
    echo Kurulumda "Add Python to PATH" secenegini isaretleyin.
    pause
    exit /b 1
)

python goodpay_gui.py
if errorlevel 1 pause
