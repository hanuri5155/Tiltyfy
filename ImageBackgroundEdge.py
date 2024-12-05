import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np


def refine_edges(edges):
    kernel = np.ones((10, 10), np.uint8)
    closed_edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    refined_edges = cv2.dilate(closed_edges, kernel, iterations=1)
    refined_edges = cv2.erode(refined_edges, kernel, iterations=1)
    return refined_edges


def remove_background(image, edges):
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError("객체를 감지할 수 없습니다.")

    largest_contour = max(contours, key=cv2.contourArea)

    mask = np.zeros_like(edges, dtype=np.uint8)
    cv2.drawContours(mask, [largest_contour], -1, (255), thickness=cv2.FILLED)

    image_rgba = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
    image_rgba[mask == 0, 3] = 0

    return Image.fromarray(cv2.cvtColor(image_rgba, cv2.COLOR_BGRA2RGBA))


def update_edge_preview(lower_threshold, upper_threshold):
    global current_processed_image

    if current_image is None:
        return

    gray = cv2.cvtColor(current_image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, lower_threshold, upper_threshold)
    refined_edges = refine_edges(edges)

    # 경계선 이미지 표시
    edges_image = Image.fromarray(cv2.cvtColor(refined_edges, cv2.COLOR_GRAY2RGB))
    edges_image = edges_image.resize((300, 300))
    edge_photo = ImageTk.PhotoImage(edges_image)
    edge_label.config(image=edge_photo)
    edge_label.image = edge_photo

    # 처리된 이미지 표시
    try:
        processed_image = remove_background(current_image, refined_edges)
        processed_image = processed_image.resize((300, 300))
        processed_photo = ImageTk.PhotoImage(processed_image)
        processed_label.config(image=processed_photo)
        processed_label.image = processed_photo

        current_processed_image = remove_background(current_image, refined_edges)

    except Exception as e:
        processed_label.config(image='')
        processed_label.image = None
        current_processed_image = None


def process_image():
    global current_image, lower_threshold, upper_threshold

    try:
        input_path = filedialog.askopenfilename(
            title="이미지 파일 선택",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if not input_path:
            return

        upload_button.grid_forget()

        # 이미지 로드
        current_image = cv2.imread(input_path)
        original_image = Image.open(input_path)
        update_image_display(original_image, image_label)

        # 슬라이더 표시
        lower_threshold_label.grid(row=3, column=0, padx=10, pady=10)
        lower_threshold_slider.grid(row=4, column=0, padx=10, pady=10)
        upper_threshold_label.grid(row=3, column=1, padx=10, pady=10)
        upper_threshold_slider.grid(row=4, column=1, padx=10, pady=10)

        # 초기 경계선 처리 및 표시
        update_edge_preview(lower_threshold.get(), upper_threshold.get())

        save_button.config(state=tk.NORMAL)
        new_image_button.config(state=tk.NORMAL)

        upload_text.config(text="업로드 이미지")
        edge_text.config(text="경계선 이미지")
        processed_text.config(text="처리된 이미지")

    except Exception as e:
        messagebox.showerror("오류", str(e))


def update_image_display(image, image_label):
    image = image.resize((300, 300))
    photo = ImageTk.PhotoImage(image)

    image_label.config(image=photo)
    image_label.image = photo


def save_image():
    if current_processed_image is None:
        messagebox.showerror("오류", "저장할 이미지가 없습니다.")
        return

    save_path = filedialog.asksaveasfilename(
        title="결과 파일 저장",
        defaultextension=".png",
        filetypes=[("PNG Files", "*.png")]
    )
    if save_path:
        current_processed_image.save(save_path)
        messagebox.showinfo("완료", f"결과 파일 저장 완료!\n결과 파일: {save_path}")


def upload_new_image():
    global current_image, current_processed_image
    current_image = None
    current_processed_image = None

    image_label.config(image='')
    edge_label.config(image='')
    processed_label.config(image='')

    upload_button.grid(row=1, column=0, columnspan=3, pady=20)
    save_button.config(state=tk.DISABLED)
    new_image_button.config(state=tk.DISABLED)

    lower_threshold_label.grid_remove()
    lower_threshold_slider.grid_remove()
    upper_threshold_label.grid_remove()
    upper_threshold_slider.grid_remove()

    upload_text.config(text="")
    edge_text.config(text="")
    processed_text.config(text="")


def create_gui():
    global image_label, edge_label, processed_label, upload_button
    global save_button, new_image_button, current_image, current_processed_image
    global lower_threshold, upper_threshold
    global lower_threshold_label, lower_threshold_slider, upper_threshold_label, upper_threshold_slider
    global upload_text, edge_text, processed_text

    current_image = None
    current_processed_image = None

    root = tk.Tk()
    root.title("경계선 조정 및 처리된 이미지 미리보기")

    root.geometry("1000x600")
    root.resizable(True, True)

    # 원본 이미지 레이블
    image_label = tk.Label(root)
    image_label.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    # 경계선 이미지 레이블
    edge_label = tk.Label(root)
    edge_label.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

    # 처리된 이미지 레이블
    processed_label = tk.Label(root)
    processed_label.grid(row=0, column=2, padx=20, pady=20, sticky="nsew")

    # 텍스트 레이블
    upload_text = tk.Label(root, text="", font=("Arial", 12))
    upload_text.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
    edge_text = tk.Label(root, text="", font=("Arial", 12))
    edge_text.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")
    processed_text = tk.Label(root, text="", font=("Arial", 12))
    processed_text.grid(row=1, column=2, padx=10, pady=5, sticky="nsew")

    # 이미지 업로드 버튼
    upload_button = tk.Button(root, text="이미지 업로드", command=process_image, font=("Arial", 14))
    upload_button.grid(row=2, column=0, columnspan=3, pady=20, sticky="nsew")

    # 슬라이더 (초기 상태는 숨김)
    lower_threshold = tk.IntVar(value=50)
    upper_threshold = tk.IntVar(value=150)

    lower_threshold_label = tk.Label(root, text="Lower Threshold", font=("Arial", 12))
    lower_threshold_slider = tk.Scale(root, from_=0, to=255, orient=tk.HORIZONTAL, variable=lower_threshold,
                                      command=lambda _: update_edge_preview(lower_threshold.get(),
                                                                            upper_threshold.get()))
    upper_threshold_label = tk.Label(root, text="Upper Threshold", font=("Arial", 12))
    upper_threshold_slider = tk.Scale(root, from_=0, to=255, orient=tk.HORIZONTAL, variable=upper_threshold,
                                      command=lambda _: update_edge_preview(lower_threshold.get(),
                                                                            upper_threshold.get()))

    lower_threshold_label.grid_remove()
    lower_threshold_slider.grid_remove()
    upper_threshold_label.grid_remove()
    upper_threshold_slider.grid_remove()

    # 저장 및 새 이미지 버튼
    save_button = tk.Button(root, text="이미지 저장", command=save_image, state=tk.DISABLED, font=("Arial", 14))
    save_button.grid(row=5, column=0, columnspan=3, pady=20, sticky="nsew")

    new_image_button = tk.Button(root, text="새로운 이미지 업로드", command=upload_new_image, font=("Arial", 14),
                                 state=tk.DISABLED)
    new_image_button.grid(row=6, column=0, columnspan=3, pady=20, sticky="nsew")

    # Grid 가로, 세로 비율을 맞추기 위해
    for i in range(7):
        root.grid_rowconfigure(i, weight=1)
    for i in range(3):
        root.grid_columnconfigure(i, weight=1)

    root.mainloop()


if __name__ == "__main__":
    create_gui()
