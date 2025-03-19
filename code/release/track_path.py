import cv2
import numpy as np
from collections import defaultdict
from config import config
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors



# Ngưỡng xác định hướng
threshold = 5  

# Load YOLO model
model = YOLO(config["model_path"]+"/yolov9t.pt")

# Mở video
cap = cv2.VideoCapture(config["video_path"]+"/4.mp4")  # Chọn video

# Lấy thông số video
w, h, fps = (int(cap.get(x)) for x in (3, 4, 5))  # Thay vì CAP_PROP_*

# Video output
out = cv2.VideoWriter(config["output_video_path"]+"/track_path/output.avi", cv2.VideoWriter_fourcc(*"MJPG"), fps, (w, h))

# Dictionary lưu tracking history (tọa độ các đối tượng)
track_history = defaultdict(list)

# Frame counter
frame_counter = 0

# Bắt đầu chạy video
while cap.isOpened():
    ret, frame = cap.read()
    frame = cv2.resize(frame, (int(w/4), int(h/4)))
    if not ret:
        print("Video kết thúc.")
        break

    frame_counter += 1
    if frame_counter % 3 != 0:  # Bỏ qua 1 frame để tăng tốc
        cv2.imshow("Motion Trail Tracking", frame)
        continue

    annotator = Annotator(frame, line_width=2)

    # Dự đoán và tracking đối tượng
    results = model.track(frame, persist=True)

    if results[0].boxes.id is not None:
        boxes = results[0].boxes.xyxy.cpu().numpy()  # Bounding boxes
        track_ids = results[0].boxes.id.int().cpu().tolist()  # Track IDs
        class_ids = results[0].boxes.cls.cpu().numpy()

        for box, class_id, track_id in zip(boxes, class_ids, track_ids):
            # if class_id in [2, 3, 5, 7]:  # Assuming class IDs for vehicles
            if class_id ==0:  # Assuming class IDs for vehicles
                center_x = int((box[0] + box[2]) / 2)
                center_y = int((box[1] + box[3]) / 2)

                # Lưu lại lịch sử vị trí
                track_history[track_id].append((center_x, center_y))

                # Giữ lại tối đa 100 điểm gần nhất để tránh đường quá dài
                if len(track_history[track_id]) > 100:
                    track_history[track_id].pop(0)

        # Vẽ motion trail theo hướng di chuyển
        for track_id, points in track_history.items():
            if len(points) > 1:
                color = colors(track_id, True)
                # Vẽ đường di chuyển
                for i in range(1, len(points)):
                    pt1, pt2 = points[i - 1], points[i]
                    thickness = max(1, 5 - (len(points) - i) // 20)  # Giảm độ dày dần
                    cv2.line(frame, pt1, pt2, color, thickness)

        # Vẽ bounding box và ID
        for box, class_id, track_id in zip(boxes, class_ids, track_ids):
            if class_id in [2, 3, 5, 7]:  # Assuming class IDs for vehicles
                annotator.box_label(box, f"ID: {track_id}", color=colors(track_id, True))
            
    # Ghi video output
    out.write(frame)
    
    # Hiển thị khung hình
    cv2.imshow("Motion Trail Tracking", frame)

    # Nhấn 'q' để thoát
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Giải phóng tài nguyên
cap.release()
out.release()
cv2.destroyAllWindows()
