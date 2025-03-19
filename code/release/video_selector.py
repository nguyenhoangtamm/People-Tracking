import tkinter as tk

# Danh sách video có sẵn
video_list = [
    "../../videos/test_videos/1.mp4",
    "../../videos/test_videos/2.mp4",
    "../../videos/test_videos/3.mp4",
    "../../videos/test_videos/4.mp4",
    "../../videos/test_videos/5.mp4",
    "../../videos/test_videos/6.mp4",
    "../../videos/test_videos/7.mp4"
]

def choose_video():
    """Hiển thị cửa sổ chọn video và trả về đường dẫn video được chọn."""
    selected_video = None

    def on_select(video_path):
        nonlocal selected_video
        selected_video = video_path
        root.quit()
        root.destroy()

    # Tạo giao diện Tkinter
    root = tk.Tk()
    root.title("Chọn Video")
    root.geometry("300x300")

    label = tk.Label(root, text="Chọn một video để xử lý:")
    label.pack()

    for video in video_list:
        btn = tk.Button(root, text=video.split('/')[-1], command=lambda v=video: on_select(v))
        btn.pack()

    root.mainloop()

    return selected_video
