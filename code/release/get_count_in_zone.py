import cv2
import numpy as np
from config import config
from collections import defaultdict
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
from video_selector import choose_video  # Import hàm chọn video

model = YOLO(config["model_path"]+"/yolov9t.pt")

# Mở video
cap = cv2.VideoCapture(config["video_path"]+"/7.mp4")  # Chọn video


# Lấy thông số video
w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

# Biến toàn cục để lưu vùng chọn
region_selected = False
region_pts = []
vector_pts = [(0, 0), (0, 1)]

# Hàm xử lý sự kiện chuột để vẽ vùng chọn
def draw_region(event, x, y, flags, param):
    global region_pts, region_selected

    if event == cv2.EVENT_LBUTTONDOWN:  # Click chuột để chọn điểm
        region_pts.append((x, y))
    
    elif event == cv2.EVENT_RBUTTONDOWN and len(region_pts) > 2:  # Nhấn chuột phải để hoàn tất vùng chọn
        region_selected = True

# Tạo cửa sổ video và gán sự kiện chuột
cv2.namedWindow("Select Region")
cv2.setMouseCallback("Select Region", draw_region)

# Lấy khung hình đầu tiên để chọn vùng
ret, frame = cap.read()
if not ret:
    print("Không thể mở video!")
    cap.release()
    cv2.destroyAllWindows()
    exit()

# Chọn vùng trên khung hình đầu tiên
while True:
    frame = cv2.resize(frame, (int(w/2), int(h/2)))
    temp_frame = frame.copy()
    
    if len(region_pts) > 1:
        cv2.polylines(temp_frame, [np.array(region_pts, np.int32)], isClosed=False, color=(0, 255, 0), thickness=2)

    cv2.imshow("Select Region", temp_frame)

    if region_selected:
        cv2.fillPoly(frame, [np.array(region_pts, np.int32)], (0, 255, 0))
        cv2.imshow("Select Region", frame)
        cv2.waitKey(500)
        break

    if cv2.waitKey(1) & 0xFF == ord("q"):  # Nhấn 'q' để hủy
        cap.release()
        cv2.destroyAllWindows()
        exit()

cv2.destroyAllWindows()

# Chuyển vùng chọn thành mặt nạ
mask = np.zeros((h, w), dtype=np.uint8)
cv2.fillPoly(mask, [np.array(region_pts, np.int32)], 255)

# Video output
out = cv2.VideoWriter(config["output_video_path"]+"count_in_zone/output.avi", cv2.VideoWriter_fourcc(*"MJPG"), fps, (w, h))

# Dictionary lưu tracking
track_history = defaultdict(lambda: [])
last_positions = {}
# Biến đếm số người đi lên và đi xuống
count_up = 0
count_down = 0

# Bắt đầu chạy video
while True:
    ret, im0 = cap.read()
    im0 = cv2.resize(im0, (int(w/2), int(h/2)))

    if not ret:
        print("Video kết thúc.")
        break

    annotator = Annotator(im0, line_width=2)
    results = model.track(im0, persist=True)

    if results[0].boxes.id is not None:
        boxes = results[0].boxes.xyxy.cpu().numpy()
        class_id = results[0].boxes.cls.cpu().numpy()

        track_ids = results[0].boxes.id.int().cpu().tolist()

        for box,class_id, track_id in zip(boxes,class_id, track_ids):
            bottom_midpoint_x = int((box[0] + box[2]) / 2)
            bottom_midpoint_y = int(box[3])

            # Ensure the midpoint coordinates are within the bounds of the mask
            if 0 <= bottom_midpoint_x < w and 0 <= bottom_midpoint_y < h:
                # Kiểm tra điểm có trong vùng không
                in_region = (mask[bottom_midpoint_y, bottom_midpoint_x] == 255) 
                label = f"ID: {track_id} (IN REGION)" if in_region else f"ID: {track_id}"
                color = (0, 0, 255) if in_region else colors(track_id, True)

                # vector tracking
                vector = (bottom_midpoint_x, bottom_midpoint_y)
                # Lưu tracking history
                track_history[track_id].append(vector)

                # Tính hướng di chuyển
                if len(track_history[track_id]) > 1:
                    last_pos = track_history[track_id][-2]
                    if len(track_history[track_id]) > 3:
                        last_pos_2 = track_history[track_id][-3]
                        last_pos_3 = track_history[track_id][-4]
                    current_pos = track_history[track_id][-1]

                    # Tính hướng di chuyển dựa trên vector người dùng vẽ
                    vector_direction = (vector_pts[1][0] - vector_pts[0][0], vector_pts[1][1] - vector_pts[0][1])
                    movement_direction = (current_pos[0] - last_pos[0], current_pos[1] - last_pos[1])
                    dot_product = vector_direction[0] * movement_direction[0] + vector_direction[1] * movement_direction[1]
                    if  model.names[int(class_id)] == "person":
                    # Đếm số người đi lên và đi xuống
                        if dot_product < 0 and( not in_region) and mask[last_pos[1], last_pos[0]] == 255 and mask[last_pos_2[1], last_pos_2[0]] == 255 and mask[last_pos_3[1], last_pos_3[0]] == 255:
                            count_up += 1
                        elif dot_product > 0 and in_region and mask[last_pos[1], last_pos[0]] != 255:
                            count_down += 1
                # Vẽ bounding box và label
                annotator.box_label(box, label, color=color)

    out.write(im0)
    # Hiển thị số lượng người đi lên và đi xuống
    cv2.putText(im0, f"Count Up: {count_up}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    cv2.putText(im0, f"Count Down: {count_down}", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
    cv2.imshow("Object Detection", im0)
 

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
