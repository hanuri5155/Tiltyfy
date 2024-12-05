import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import os

output_gif_path = r"F:\Projects\Deu\3-junior\3-2\DIP\Tiltyfy\tet_data\CreatedGIF.gif"


def select_file():
    file_paths = filedialog.askopenfilenames(filetypes=[("All Files", "*.*"),
                                                        ("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"),
                                                        ("Video Files", "*.mp4;*.avi;*.mkv;*.mov;*.flv")])
    if file_paths:
        file_extension = os.path.splitext(file_paths[0])[1].lower()
        if file_extension in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
            process_images(file_paths)
        elif file_extension in ['.mp4', '.avi', '.mkv', '.mov', '.flv']:
            process_video(file_paths[0])
        else:
            messagebox.showerror("Error", "지원하지 않는 파일 형식입니다.")


def process_images(image_files):
    try:
        frames = []
        base_image = Image.open(image_files[0])
        width, height = base_image.size

        for img_path in image_files:
            img = Image.open(img_path)
            img_resized = img.resize((width, height))
            frames.append(img_resized)

        os.makedirs(os.path.dirname(output_gif_path), exist_ok=True)
        frames[0].save(output_gif_path, format="GIF",
                       save_all=True, append_images=frames[1:],
                       duration=500, loop=0)
        messagebox.showinfo("성공", f"움짤 생성 완료: {output_gif_path}")
    except Exception as e:
        messagebox.showerror("Error", f"오류 발생: {e}")


def process_video(video_path):
    try:
        cap = cv2.VideoCapture(video_path)
        frames = []
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img_resized = img.resize((400, 300))
            frames.append(img_resized)

        cap.release()

        os.makedirs(os.path.dirname(output_gif_path), exist_ok=True)
        frames[0].save(output_gif_path, format="GIF",
                       save_all=True, append_images=frames[1:],
                       duration=100, loop=0)
        messagebox.showinfo("성공", f"움짤 생성 완료: {output_gif_path}")
    except Exception as e:
        messagebox.showerror("Error", f"동영상 처리 오류: {e}")


root = tk.Tk()
root.title("이미지 및 동영상 GIF 변환기")
root.geometry("800x600")

select_button = tk.Button(root, text="이미지/동영상 선택", command=select_file, height=2, width=20)
select_button.pack(pady=20)

root.mainloop()
