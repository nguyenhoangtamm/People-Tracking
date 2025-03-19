import subprocess
import tkinter as tk
from tkinter import messagebox
import sys

def detect_motion():
    subprocess.Popen([sys.executable, "detect_object_in_zone_draw.py"])  # Cập nhật đường dẫn file

def track_body_parts():
    subprocess.Popen([sys.executable, "get_count_in_zone.py"])  # Cập nhật đường dẫn file nếu cần
def track_path():
    subprocess.Popen([sys.executable, "track_path.py"])  # Cập nhật đường dẫn file nếu cần
def exit_program():
    tk_root.destroy()

# Tạo giao diện
tk_root = tk.Tk()
tk_root.title("Chương trình nhận diện cử động")
tk_root.geometry("500x400")

title_label = tk.Label(tk_root, text="Chọn chức năng", font=("Arial", 16))
title_label.pack(pady=20)

btn_motion = tk.Button(tk_root, text="Phát hiện đối tượng trong vùng", command=detect_motion, width=30, height=2)
btn_motion.pack(pady=10)

btn_tracking = tk.Button(tk_root, text="Ví dụ: Đếm số lượng người lên xuống", command=track_body_parts, width=30, height=2)
btn_tracking.pack(pady=10)
btn_tracking= tk.Button(tk_root, text="Ví dụ: Theo dõi đường đi", command=track_path, width=30, height=2)
btn_tracking.pack(pady=10)

btn_exit = tk.Button(tk_root, text="Thoát", command=exit_program, width=30, height=2, bg="red", fg="white")
btn_exit.pack(pady=10)

# Chạy giao diện
tk_root.mainloop()
