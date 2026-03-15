#!/usr/bin/env python3
"""
Пример: Как запустить сервер в разных режимах

Скопируй эту функцию в свой код для пользовательского запуска
"""

import sys
import os

# Пример 1: Запуск на всех интерфейсах (по умолчанию)


def run_public():
    """Запуск как публичный сервер для локальной сети"""
    os.system(f"{sys.executable} app.py")
    # Flask будет доступен на:
    # - http://localhost:5000 (этот ПК)
    # - http://192.168.x.x:5000 (другие ПК в сети)

# Пример 2: Запуск только локально


def run_local_only():
    """Запуск только для этого ПК"""
    from app import app
    app.run(debug=False, host='127.0.0.1', port=5000, threaded=True)
    # Flask будет доступен только на:
    # - http://localhost:5000

# Пример 3: На статическом IP адресе


def run_on_specific_ip(ip_address='192.168.1.100'):
    """Запуск на конкретном IP адресе"""
    from app import app
    app.run(debug=False, host=ip_address, port=5000, threaded=True)
    # Flask будет доступен на:
    # - http://192.168.1.100:5000

# Пример 4: На другом порте


def run_on_port(port=8080):
    """Запуск на другом порте (если 5000 занят)"""
    from app import app
    app.run(debug=False, host='0.0.0.0', port=port, threaded=True)
    # Flask будет доступен на:
    # - http://localhost:8080
    # - http://192.168.x.x:8080

# Пример 5: С NGROK туннелем


def run_with_ngrok():
    """Запуск с NGROK туннелем для публичного доступа"""
    import subprocess
    import time

    # Запусти Flask
    print("Запуск Flask сервера...")
    flask_proc = subprocess.Popen([sys.executable, 'app.py'])

    time.sleep(2)  # Жди загрузки Flask

    # Запусти NGROK
    print("Инициализация NGROK туннеля...")
    ngrok_proc = subprocess.Popen(['ngrok', 'http', '5000'])

    try:
        flask_proc.wait()
    except KeyboardInterrupt:
        print("\nОстанавливаю сервер...")
        flask_proc.terminate()
        ngrok_proc.terminate()

# Пример 6: Production режим (с Gunicorn)


def run_production():
    """Запуск в production режиме (требует Gunicorn)"""
    # Установи: pip install gunicorn
    os.system("gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app")

# Пример 7: С переменными окружения


def run_with_config():
    """Запуск с переменными окружения"""
    os.environ['FLASK_ENV'] = 'production'
    os.environ['FLASK_DEBUG'] = '0'

    from app import app
    app.run(
        debug=False,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )

# Пример 8: С SSL (HTTPS)


def run_with_ssl():
    """Запуск с самоподписанным SSL сертификатом"""
    from app import app

    # Требует openssl для создания сертификата:
    # openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

    if os.path.exists('cert.pem') and os.path.exists('key.pem'):
        app.run(
            debug=False,
            host='0.0.0.0',
            port=5000,
            threaded=True,
            ssl_context=('cert.pem', 'key.pem')
        )
    else:
        print("❌ Сертификаты не найдены!")
        print("Создай: openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365")

# Пример 9: С логированием


def run_with_logging():
    """Запуск с подробным логированием"""
    import logging

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('flask')
    logger.setLevel(logging.DEBUG)

    from app import app
    app.run(
        debug=False,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )

# Пример 10: С кастомными параметрами


def run_custom(
    host='0.0.0.0',
    port=5000,
    debug=False,
    threaded=True,
    use_reloader=False,
    use_debugger=False
):
    """Запуск с кастомными параметрами"""
    from app import app

    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=threaded,
        use_reloader=use_reloader,
        use_debugger=use_debugger
    )

# ============================================================================
# БЫСТРЫЕ КОМАНДЫ ДЛЯ ИСПОЛЬЗОВАНИЯ
# ============================================================================


if __name__ == '__main__':
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()

        if cmd == 'public':
            print("✅ Запуск как публичного сервера...")
            run_public()

        elif cmd == 'local':
            print("✅ Запуск только для локального доступа...")
            run_local_only()

        elif cmd == 'ngrok':
            print("✅ Запуск с NGROK туннелем...")
            run_with_ngrok()

        elif cmd == 'production':
            print("✅ Запуск в production режиме...")
            run_production()

        elif cmd == 'ssl':
            print("✅ Запуск с SSL (HTTPS)...")
            run_with_ssl()

        elif cmd == 'logging':
            print("✅ Запуск с логированием...")
            run_with_logging()

        else:
            print(f"Неизвестная команда: {cmd}")
            print("\nДоступные команды:")
            print("  public     - Публичный сервер (локальная сеть)")
            print("  local      - Только локальный доступ")
            print("  ngrok      - С NGROK туннелем (интернет)")
            print("  production - Production режим (Gunicorn)")
            print("  ssl        - С SSL сертификатом (HTTPS)")
            print("  logging    - С подробным логированием")

    else:
        print("\n" + "="*60)
        print("  🌐 ПРИМЕРЫ ЗАПУСКА СЕРВЕРА")
        print("="*60 + "\n")

        print("Используй эти примеры в своём коде:\n")

        print("1. Публичный сервер (локальная сеть):")
        print("   run_public()\n")

        print("2. Только локальный доступ:")
        print("   run_local_only()\n")

        print("3. С NGROK туннелем (интернет):")
        print("   run_with_ngrok()\n")

        print("4. Production (Gunicorn):")
        print("   run_production()\n")

        print("5. С SSL (HTTPS):")
        print("   run_with_ssl()\n")

        print("6. С логированием:")
        print("   run_with_logging()\n")

        print("7. Кастомные параметры:")
        print("   run_custom(host='0.0.0.0', port=8080)\n")

        print("ИЛИ используй команды:\n")
        print("   python examples.py public")
        print("   python examples.py ngrok")
        print("   python examples.py production")
