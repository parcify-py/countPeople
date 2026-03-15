#!/usr/bin/env python3
"""
Скрипт для получения информации о доступе к серверу
Показывает локальный IP, способы подключения и статус сервера
"""

import socket
import subprocess
import os
import sys
import platform
from urllib.request import urlopen


def get_local_ip():
    """Получить локальный IP адрес"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


def get_public_ip():
    """Получить публичный IP адрес"""
    try:
        return urlopen('https://ident.me').read().decode('utf8').strip()
    except:
        return "Недоступно"


def check_ngrok_running():
    """Проверить работает ли NGROK"""
    try:
        response = urlopen('http://localhost:4040/api/tunnels', timeout=2)
        import json
        data = json.loads(response.read())
        tunnels = data.get('tunnels', [])
        for tunnel in tunnels:
            if tunnel['public_url'].startswith('https://'):
                return tunnel['public_url']
    except:
        pass
    return None


def check_server_running():
    """Проверить работает ли Flask сервер"""
    try:
        response = urlopen('http://localhost:5000/api/stats', timeout=2)
        if response.status == 200:
            return True
    except:
        pass
    return False


def show_access_info():
    """Показать информацию о доступе"""
    local_ip = get_local_ip()
    public_ip = get_public_ip()

    server_running = check_server_running()
    ngrok_url = check_ngrok_running()

    print("\n" + "="*70)
    print("  🌐 ИНФОРМАЦИЯ О ДОСТУПЕ К СЕРВЕРУ")
    print("="*70 + "\n")

    # Статус сервера
    if server_running:
        print("✅  Flask сервер: РАБОТАЕТ")
    else:
        print("❌  Flask сервер: НЕ ЗАПУЩЕН")
        print("   Запустите: python app.py\n")
        return

    print("\n" + "-"*70)
    print("  📍 ЛОКАЛЬНАЯ СЕТь (в доме/офисе)")
    print("-"*70)
    print(f"  URL: http://{local_ip}:5000")
    print(f"  или: http://localhost:5000")
    print(f"\n  Используй на других ПК в той же Wi-Fi сети:")
    print(f"  → http://{local_ip}:5000\n")

    print("-"*70)
    print("  🌍 ПУБЛИЧНЫЙ ИНТЕРНЕТ")
    print("-"*70)

    if ngrok_url:
        print(f"  NGROK: {ngrok_url}")
        print(f"  Скопируй эту ссылку для доступа из интернета!\n")
    else:
        print(f"  Публичный IP: {public_ip}")
        print(f"  ❌ NGROK не запущен")
        print(f"  Запусти: python run_public_server.py --ngrok\n")

    print("-"*70)
    print("  🧪 ТЕСТИРОВАНИЕ")
    print("-"*70)
    print("  API: http://localhost:5000/api/stats")
    print("  Видео: http://localhost:5000/video_feed")

    print("\n" + "="*70)
    print("  💡 СОВЕТ: Сохрани эту информацию для быстрого доступа")
    print("="*70 + "\n")

    # Показать команды для запуска
    print("⚡ БЫСТРЫЕ КОМАНДЫ:\n")
    if platform.system() == "Windows":
        print("  Локальная сеть:  python run_public_server.py --local")
        print("  NGROK туннель:   python run_public_server.py --ngrok")
        print("  Меню выбора:     run_server.bat")
    else:
        print("  Локальная сеть:  python3 run_public_server.py --local")
        print("  NGROK туннель:   python3 run_public_server.py --ngrok")
        print("  Меню выбора:     ./run_server.sh")


if __name__ == '__main__':
    try:
        show_access_info()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)
