@echo off
REM Запуск приложения как публичного сервера на Windows

echo.
echo ============================================================
echo   ЗАПУСК ПУБЛИЧНОГО СЕРВЕРА
echo ============================================================
echo.

color 0A

if "%1"=="" (
    echo Выберите способ запуска:
    echo.
    echo   1 - Локальная сеть (192.168.x.x:5000)
    echo   2 - NGROK туннель (интернет)
    echo.
    set /p choice="Введите номер (1 или 2): "
    
    if "%choice%"=="1" (
        python run_public_server.py --local
    ) else if "%choice%"=="2" (
        python run_public_server.py --ngrok
    ) else (
        echo Неверный выбор!
        exit /b 1
    )
) else if "%1"=="--local" (
    echo Запуск для локальной сети...
    python run_public_server.py --local
) else if "%1"=="--ngrok" (
    echo Запуск с NGROK туннелем...
    python run_public_server.py --ngrok
) else (
    echo Неизвестный аргумент: %1
    echo Используйте: run_server.bat [--local^|--ngrok]
    exit /b 1
)

pause
