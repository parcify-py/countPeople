from flask import Flask, render_template, Response, jsonify
from flask_cors import CORS
import cv2
import time
from ultralytics import YOLO
import threading
import json

app = Flask(__name__)
CORS(app)

# Загружаем модель
print("Загружаю модель...")
model = YOLO("./yolov8n.pt")
print("Модель загружена!")

# Глобальные переменные для потокобезопасности
people_count = 0
wait_time = 0
last_detection_time = time.time()
detected_boxes = []
statistics = {
    "total_detections": 0,
    "max_people": 0,
    "min_people": 999,
    "average_people": 0,
    "detections_count": 0,
    "uptime": 0,
    "fps": 0
}
lock = threading.Lock()

# Время запуска
start_time = time.time()

# Параметры
DETECTION_INTERVAL = 0.3  # Детекция раз в 1.5 секунды
TIME_PER_PERSON = 30  # 30 секунд на человека

# Переменная для хранения текущего кадра для детекции
current_frame_for_detection = None


def detection_loop():
    """Отдельный поток для детекции людей (с задержкой 1-2 сек)"""
    global people_count, wait_time, current_frame_for_detection, detected_boxes, statistics

    print("🤖 Поток детекции запущен...")

    while True:
        try:
            # Ждем перед следующей детекцией (1-2 сек)
            time.sleep(DETECTION_INTERVAL)

            # Если нет кадра, пропускаем
            if current_frame_for_detection is None:
                continue

            # Выполняем детекцию на копии кадра
            frame_copy = current_frame_for_detection.copy()
            results = model(frame_copy)

            with lock:
                people_count = 0
                detected_boxes = []

                for r in results:
                    for box in r.boxes:
                        cls = int(box.cls[0])
                        if cls == 0:  # person
                            people_count += 1
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            detected_boxes.append((x1, y1, x2, y2))

                # Обновляем статистику
                statistics["total_detections"] += people_count
                statistics["detections_count"] += 1
                statistics["max_people"] = max(
                    statistics["max_people"], people_count)
                if people_count > 0:
                    statistics["min_people"] = min(
                        statistics["min_people"], people_count)
                statistics["average_people"] = statistics["total_detections"] / \
                    max(1, statistics["detections_count"])
                statistics["uptime"] = int(time.time() - start_time)

                # Время ожидания
                wait_time = people_count * TIME_PER_PERSON

        except Exception as e:
            print(f"Ошибка в потоке детекции: {e}")


def generate_frames():
    """Генератор кадров видео БЕЗ задержек (только передача)"""
    global people_count, detected_boxes, current_frame_for_detection, statistics

    print("🎥 Открываю камеру для видео потока...")
    cap = cv2.VideoCapture("http://100.74.84.99:8080/video")

    if not cap.isOpened():
        print("❌ Ошибка: Камера не открылась")
        return

    fps_time = time.time()
    fps_counter = 0
    current_fps = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
            continue

        frame = cv2.resize(frame, (800, 600))

        # Сохраняем кадр для потока детекции
        with lock:
            current_frame_for_detection = frame.copy()

        # Рисуем боксы которые получили из потока детекции (они уже рассчитаны)
        with lock:
            for x1, y1, x2, y2 in detected_boxes:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, "Person", (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # FPS счетчик
        fps_counter += 1
        elapsed = time.time() - fps_time
        if elapsed >= 1:
            current_fps = fps_counter / elapsed
            statistics["fps"] = round(current_fps, 1)
            fps_counter = 0
            fps_time = time.time()

        # Информация на кадре удалена (видео чистое)

        # Кодируем в JPEG И ОТПРАВЛЯЕМ БЕЗ ЗАДЕРЖЕК
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n'
               b'Content-Length: ' +
               str(len(frame_bytes)).encode() + b'\r\n\r\n'
               + frame_bytes + b'\r\n')

    cap.release()


@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    """Видео поток MJPEG"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/stats')
def get_stats():
    """API для получения статистики"""
    with lock:
        minutes = wait_time // 60
        seconds = wait_time % 60

        wait_text = "Очередь пуста ✓" if people_count == 0 else f"{minutes}м {seconds}с"

        return jsonify({
            "people_count": people_count,
            "wait_time": wait_time,
            "wait_text": wait_text,
            "fps": statistics["fps"],
            "max_people": statistics["max_people"],
            "min_people": 0 if statistics["min_people"] == 999 else statistics["min_people"],
            "average_people": round(statistics["average_people"], 1),
            "detections": statistics["detections_count"],
            "uptime": statistics["uptime"]
        })


if __name__ == '__main__':
    # Запускаем поток детекции в фоне
    detection_thread = threading.Thread(target=detection_loop, daemon=True)
    detection_thread.start()
    print("✅ Основной поток готов\n")

    # Запускаем на всех интерфейсах для доступа из локальной сети и через портфорвардинг
    # 0.0.0.0 = доступен с других ПК в локальной сети и через интернет (если портфорвардинг настроен)
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
