#!/usr/bin/env python3
"""
Скрипт для запуска сервера как публичного со следующими опциями:
1. Локальная сеть через IP адрес (192.168.x.x:5000)
2. Через ngrok туннель (автоматическое создание публичного URL)
3. Через портфорвардинг роутера (ручная настройка)
"""


import os
import sys
import subprocess
import socket
import platform
from pathlib import Path


def get_local_ip():
    """Получить локальный IP адрес"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"Ошибка при получении IP: {e}")
        return "127.0.0.1"


def check_ngrok():
    """Проверить установлен ли ngrok"""
    try:
        subprocess.run(['ngrok', '--version'], capture_output=True, check=True)
        return True
    except:
        return False


def install_ngrok():
    """Установить ngrok"""
    print("🔧 Установка ngrok...")

    system = platform.system()

    if system == "Windows":
        print("Windows обнаружена. Скачивание ngrok...")
        os.system("powershell -Command \"Invoke-WebRequest https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip -OutFile ngrok.zip; Expand-Archive ngrok.zip -DestinationPath .\"")
    elif system == "Darwin":  # macOS
        print("macOS обнаружена. Установка через brew...")
        os.system("brew install ngrok")
    elif system == "Linux":
        print("Linux обнаружена. Скачивание ngrok...")
        os.system(
            "curl -s https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tar.gz | tar xz")

    print("✅ ngrok установлен!")


def start_with_ngrok():
    """Запустить сервер с ngrok туннелем"""
    print("\n" + "="*60)
    print("🚀 Запуск сервера с ngrok туннелирование...")
    print("="*60 + "\n")

    if not check_ngrok():
        print("ngrok не установлен. Установка...")
        install_ngrok()

    print("⏳ Запуск Flask приложения на порте 5000...")
    print("⏳ Инициализация ngrok туннеля...\n")

    # Запуск Flask в отдельном процессе и ngrok параллельно
    flask_process = subprocess.Popen(
        [sys.executable, 'app.py'], cwd=Path(__file__).parent)

    import time
    time.sleep(2)  # Ждём пока Flask запустится

    print("🔗 Создание публичного URL через ngrok...")
    ngrok_process = subprocess.Popen(
        ['ngrok', 'http', '5000'], cwd=Path(__file__).parent)

    try:
        flask_process.wait()
    except KeyboardInterrupt:
        print("\n\n⏹️  Останавливаю сервер...")
        flask_process.terminate()
        ngrok_process.terminate()
        print("✅ Сервер остановлен")


def start_local_server():
    """Запустить сервер только для локальной сети"""
    print("\n" + "="*60)
    print("🚀 Запуск сервера для локальной сети...")
    print("="*60 + "\n")

    local_ip = get_local_ip()

    print(f"📱 Локальный IP адрес: {local_ip}")
    print(f"🌐 Доступен по адресам:")
    print(f"   • http://localhost:5000  (этот ПК)")
    print(f"   • http://127.0.0.1:5000  (этот ПК)")
    print(f"   • http://{local_ip}:5000  (другие ПК в сети)")
    print(
        f"\n💡 Используйте http://{local_ip}:5000 на других устройствах в сети")
    print("⏹️  Нажмите Ctrl+C для остановки\n")

    os.system(f"{sys.executable} app.py")


def show_menu():
    """Показать меню выбора"""
    print("\n" + "="*60)
    print("🔥 Запуск приложения как ПУБЛИЧНОГО СЕРВЕРА")
    print("="*60 + "\n")

    local_ip = get_local_ip()

    print("Выберите способ запуска:\n")
    print("1️⃣  ЛОКАЛЬНАЯ СЕТь (для других ПК в доме/офисе)")
    print(f"   URL: http://{local_ip}:5000")
    print("   Требует: настройка в локальной сети\n")

    print("2️⃣  NGROK ТУННЕЛЬ (публичный доступ через интернет)")
    print("   URL: будет сгенерирован автоматически")
    print("   Требует: интернет, ngrok аккаунт (бесплатно)\n")

    print("3️⃣  ПОРТФОРВАРДИНГ (через роутер)")
    print("   URL: http://ваш-публичный-ip:5000")
    print("   Требует: ручная настройка роутера\n")

    choice = input("Выберите вариант (1, 2 или 3): ").strip()
    return choice


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == '--ngrok' or arg == '--public':
            start_with_ngrok()
        elif arg == '--local':
            start_local_server()
        else:
            print(f"Неизвестный аргумент: {arg}")
            print("Используйте: --local, --ngrok, или --public")
    else:
        choice = show_menu()

        if choice == '1':
            start_local_server()
        elif choice == '2':
            start_with_ngrok()
        elif choice == '3':
            print("\n📖 Для портфорвардинга см. PUBLIC_SERVER.md")
            print("\n⏳ Запуск локального сервера...")
            start_local_server()
        else:
            print("❌ Неверный выбор!")
            sys.exit(1)
