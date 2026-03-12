import cv2
import time
from ultralytics import YOLO

print("Загружаю модель...")
model = YOLO("../yolov8n.pt")
print("Модель загружена!")

print("Открываю камеру...")
cap = cv2.VideoCapture("http://172.21.211.156:8080/video")  # 0 = первая камера

if not cap.isOpened():
    print("Камера не открылась")
    exit()

print("Камера открыта!")

# Параметры оптимизации
delay = 5  # 5 мс - хорошая задержка для видео
detection_interval = 1.0  # Детекция раз в 5 секунд
frame_skip = 10  # Пропускаем кадры для лучшего FPS

# Переменные для отслеживания времени
last_detection_time = time.time()
people_count = 0
detected_boxes = []  # Сохраняем последние детектированные боксы

# FPS счетчик
fps_time = time.time()
fps_counter = 0
current_fps = 0

# Создаём окно перед циклом
cv2.namedWindow("Queue detector", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Queue detector", 800, 600)

frame_counter = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Видео закончилось")
        break

    frame_counter += 1

    # Проверяем, прошло ли 5 секунд для новой детекции
    current_time = time.time()
    if current_time - last_detection_time >= detection_interval:
        # Выполняем детекцию раз в 5 секунд
        results = model(frame)

        people_count = 0
        detected_boxes = []

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                if cls == 0:  # person
                    people_count += 1
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    detected_boxes.append((x1, y1, x2, y2))

        last_detection_time = current_time
        print(f"Детекция: найдено {people_count} человек")

    # Отрисовка сохраненных боксов на каждом кадре (быстро)
    for x1, y1, x2, y2 in detected_boxes:
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # FPS счетчик
    fps_counter += 1
    elapsed_time = time.time() - fps_time
    if elapsed_time >= 1:
        current_fps = fps_counter / elapsed_time
        fps_counter = 0
        fps_time = time.time()

    cv2.putText(frame, f"People: {people_count}", (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Вывод FPS
    cv2.putText(frame, f"FPS: {current_fps:.1f}", (20, 75),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)

    # Расчет времени ожидания (30 секунд на человека)
    wait_time_seconds = people_count * 30
    minutes = wait_time_seconds // 60
    seconds = wait_time_seconds % 60

    # Вывод времени ожидания на чешском
    if people_count == 0:
        wait_text = "Fronta je prázdná ✓"
    elif minutes == 0:
        wait_text = f"Čekací doba: {seconds}s"
    else:
        wait_text = f"Čekací doba: {minutes}m {seconds}s"

    cv2.putText(frame, wait_text, (20, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("Queue detector", frame)

    if cv2.waitKey(delay) == 27:
        break

cap.release()
cv2.destroyAllWindows()
