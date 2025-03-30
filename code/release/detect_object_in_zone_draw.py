import os
import cv2
from config import config
import numpy as np
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
from video_selector import choose_video  # Import hàm chọn video

selected_video = choose_video()

if not selected_video:
    print("Không có video nào được chọn!")
    exit()

# Load model YOLO
model = YOLO(config["model_path"]+"/best.pt")

# Mở video
cap = cv2.VideoCapture(selected_video)

# Lấy thông số video
w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
# Calculate aspect ratio of the original video
aspect_ratio = w / h

# Determine the width and height based on a desired width (e.g., 900 pixels)
desired_width = 900
video_width = desired_width
video_height = int(video_width / aspect_ratio)
# Biến toàn cục để lưu vùng chọn
region_selected = False
region_pts = []

def draw_region(event, x, y, flags, param):
    global region_pts, region_selected
    if event == cv2.EVENT_LBUTTONDOWN:
        region_pts.append((x, y))
    elif event == cv2.EVENT_RBUTTONDOWN and len(region_pts) > 2:
        region_selected = True

cv2.namedWindow("Select Region")
cv2.setMouseCallback("Select Region", draw_region)

ret, frame = cap.read()
if not ret:
    print("Không thể mở video!")
    cap.release()
    exit()

while True:
    frame = cv2.resize(frame, (video_width, video_height))
    temp_frame = frame.copy()
    if len(region_pts) > 1:
        cv2.polylines(temp_frame, [np.array(region_pts, np.int32)], isClosed=False, color=(0, 255, 0), thickness=2)
    cv2.imshow("Select Region", temp_frame)
    if region_selected:
        cv2.fillPoly(frame, [np.array(region_pts, np.int32)], (0, 255, 0))
        cv2.imshow("Select Region", frame)
        cv2.waitKey(500)
        break
    if cv2.waitKey(1) & 0xFF == ord("q"):
        cap.release()
        exit()

cv2.destroyAllWindows()

mask = np.zeros((h, w), dtype=np.uint8)
cv2.fillPoly(mask, [np.array(region_pts, np.int32)], 255)

out = cv2.VideoWriter(config["output_video_path"]+"/object_in_zone/output.avi", cv2.VideoWriter_fourcc(*"MJPG"), fps, (video_width, video_height))
frame_count = 0 
objects_in_region=[]

while True:
    ret, im0 = cap.read()
    if not ret:
        print("Video kết thúc.")
        break

    im0 = cv2.resize(im0, (video_width, video_height))
    overlay = im0.copy()
    cv2.polylines(overlay, [np.array(region_pts, np.int32)], isClosed=True, color=(0, 255, 0), thickness=2)
    cv2.addWeighted(overlay, 0.4, im0, 0.6, 0, im0)

    annotator = Annotator(im0, line_width=2)
    results = model.track(im0, persist=True)

    if results[0].boxes.id is not None:
        boxes = results[0].boxes.xyxy.cpu().numpy()
        class_id = results[0].boxes.cls.cpu().numpy()
        track_ids = results[0].boxes.id.int().cpu().tolist()

        for box, class_id, track_id in zip(boxes, class_id, track_ids):
            bottom_midpoint_x = int((box[0] + box[2]) / 2)
            bottom_midpoint_y = int(box[3])
            if 0 <= bottom_midpoint_x < w and 0 <= bottom_midpoint_y < h :
                if mask[bottom_midpoint_y, bottom_midpoint_x] == 255 :
                    label = f"(IN REGION)"
                    color = (0, 0, 255)
                    if track_id not in objects_in_region:
                        objects_in_region.append(track_id)  
                        # Cắt ảnh đối tượng nhưng bỏ những box bao quanh object
                        x1, y1, x2, y2 = map(int, box)
                        cropped_person = im0[y1:y2, x1:x2]

                        # Kiểm tra kích thước hợp lệ trước khi lưu
                        if cropped_person.size > 0:
                            save_path = os.path.join(config["output_image_path"]+"/object_in_zone", f"person_{track_id}_{frame_count}.jpg")
                            cv2.imwrite(save_path, cropped_person)
                            print(f"Đã lưu ảnh: {save_path}")

                else:
                    label = ""
                    color = colors(track_id, True)
                annotator.box_label(box,label, color=color)

    out.write(im0)
    cv2.imshow("Object Detection", im0)
    frame_count += 1
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
