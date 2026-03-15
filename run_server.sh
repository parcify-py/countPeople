#!/bin/bash

# Запуск приложения как публичного сервера на macOS/Linux

clear

echo "============================================================"
echo "  ЗАПУСК ПУБЛИЧНОГО СЕРВЕРА"
echo "============================================================"
echo ""

if [ -z "$1" ]; then
    echo "Выберите способ запуска:"
    echo ""
    echo "  1 - Локальная сеть (192.168.x.x:5000)"
    echo "  2 - NGROK туннель (интернет)"
    echo ""
    read -p "Введите номер (1 или 2): " choice
    
    case $choice in
        1)
            python3 run_public_server.py --local
            ;;
        2)
            python3 run_public_server.py --ngrok
            ;;
        *)
            echo "Неверный выбор!"
            exit 1
            ;;
    esac
else
    case "$1" in
        --local)
            echo "Запуск для локальной сети..."
            python3 run_public_server.py --local
            ;;
        --ngrok)
            echo "Запуск с NGROK туннелем..."
            python3 run_public_server.py --ngrok
            ;;
        *)
            echo "Неизвестный аргумент: $1"
            echo "Используйте: ./run_server.sh [--local|--ngrok]"
            exit 1
            ;;
    esac
fi
