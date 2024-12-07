import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageSequence
import os

output_gif_path = r"F:\Projects\Deu\3-junior\3-2\DIP\Tiltyfy\test_data\CreatedGIF.gif"
canvas_width = 800  # 캔버스 너비
canvas_height = 450  # 캔버스 높이

selected_images = []  # 사용자가 선택한 이미지 파일 리스트


def select_file():
    """
    이미지 파일 선택 및 캔버스에 미리보기 표시
    """
    global selected_images
    file_paths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
    if file_paths:
        selected_images = list(file_paths)  # 선택한 이미지 경로 저장
        create_preview_gif(selected_images)  # 선택한 이미지로 미리보기 GIF 생성
    else:
        messagebox.showerror("Error", "이미지를 선택하지 않았습니다.")


def create_preview_gif(image_files):
    """
    선택한 이미지로 미리보기 GIF 생성
    """
    try:
        frames = []
        base_image = Image.open(image_files[0])
        width, height = base_image.size

        for img_path in image_files:
            img = Image.open(img_path)
            img_resized = img.resize((width, height))
            frames.append(img_resized)

        # 임시 GIF 생성 경로
        temp_gif_path = "temp_preview.gif"
        frames[0].save(temp_gif_path, format="GIF",
                       save_all=True, append_images=frames[1:],
                       duration=500, loop=0)

        display_gif(temp_gif_path)  # 캔버스에 미리보기로 표시
    except Exception as e:
        messagebox.showerror("Error", f"미리보기 생성 오류: {e}")


def save_gif():
    """
    선택된 이미지를 GIF로 저장
    """
    global selected_images
    if not selected_images:
        messagebox.showerror("Error", "저장할 이미지가 없습니다. 먼저 이미지를 선택해주세요.")
        return

    try:
        frames = []
        base_image = Image.open(selected_images[0])
        width, height = base_image.size

        for img_path in selected_images:
            img = Image.open(img_path)
            img_resized = img.resize((width, height))
            frames.append(img_resized)

        os.makedirs(os.path.dirname(output_gif_path), exist_ok=True)
        frames[0].save(output_gif_path, format="GIF",
                       save_all=True, append_images=frames[1:],
                       duration=500, loop=0)
        messagebox.showinfo("성공", f"움짤 생성 완료: {output_gif_path}")
    except Exception as e:
        messagebox.showerror("Error", f"저장 중 오류 발생: {e}")


def display_gif(gif_path):
    """
    GIF를 캔버스에 표시
    """
    global gif_frames, gif_index

    # GIF 열기
    gif = Image.open(gif_path)
    gif_frames = [resize_to_canvas(frame.copy()) for frame in ImageSequence.Iterator(gif)]
    gif_index = 0

    def update_frame():
        global gif_index
        if gif_frames:
            canvas.itemconfig(canvas_image, image=gif_frames[gif_index])
            gif_index = (gif_index + 1) % len(gif_frames)
            root.after(800, update_frame)

    # 캔버스에 첫 프레임 표시
    canvas.itemconfig(canvas_image, image=gif_frames[gif_index])
    update_frame()


def resize_to_canvas(image):
    """
    이미지 크기를 캔버스 크기에 맞추되, 비율을 유지하여 리사이즈
    """
    img_width, img_height = image.size
    scale = min(canvas_width / img_width, canvas_height / img_height)  # 축소 비율 계산
    new_width = int(img_width * scale)
    new_height = int(img_height * scale)
    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(resized_image)


# GUI 설정
root = tk.Tk()
root.title("Tiltypy Studio")  # 제목 설정
root.geometry("900x750")  # 창 크기 설정
root.configure(bg="#f0f0f5")  # 배경 색상 설정

# 커스텀 폰트 설정
header_font = ("Helvetica", 18, "bold")
button_font = ("Helvetica", 12)

# 헤더 라벨
header_label = tk.Label(root, text="Tiltypy Studio", font=header_font, bg="#f0f0f5", fg="#333")
header_label.pack(pady=20)

# 설명 라벨
description_label = tk.Label(root, text="Select images to preview and save them as a GIF!", font=("Helvetica", 12),
                             bg="#f0f0f5", fg="#555")
description_label.pack(pady=10)

# 캔버스: GIF 미리보기
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="gray", relief="ridge", bd=2)
canvas.pack(pady=20)

# 캔버스 이미지 초기화
canvas_image = canvas.create_image(canvas_width // 2, canvas_height // 2, anchor="center")

# 버튼 프레임
button_frame = tk.Frame(root, bg="#f0f0f5")
button_frame.pack(pady=20)

# 파일 선택 버튼
select_button = tk.Button(button_frame, text="Select Image(s)", font=button_font, command=select_file, height=2,
                          width=15)
select_button.grid(row=0, column=0, padx=10)

# GIF 저장 버튼
save_button = tk.Button(button_frame, text="Save as GIF", font=button_font, command=save_gif, height=2, width=15)
save_button.grid(row=0, column=1, padx=10)

root.mainloop()
