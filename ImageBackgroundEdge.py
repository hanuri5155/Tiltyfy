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
        raise ValueError("No contours found.")

    largest_contour = max(contours, key=cv2.contourArea)

    mask = np.zeros_like(edges, dtype=np.uint8)
    cv2.drawContours(mask, [largest_contour], -1, 255, thickness=cv2.FILLED)

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
    edge_label.image = edge_photo  # 참조 유지

    # 처리된 이미지 표시
    try:
        processed_image = remove_background(current_image, refined_edges)
        processed_image = processed_image.resize((300, 300))
        processed_photo = ImageTk.PhotoImage(processed_image)
        processed_label.config(image=processed_photo)
        processed_label.image = processed_photo  # 참조 유지

        current_processed_image = processed_image
    except Exception as e:
        processed_label.config(image='')
        processed_label.image = None
        current_processed_image = None


def process_image():
    """
    새로운 이미지를 업로드하거나 기존 상태를 초기화한 후 처리하는 함수
    """
    global current_image, current_processed_image

    try:
        # 파일 선택 대화 상자 열기
        input_path = filedialog.askopenfilename(
            title="이미지 파일 선택",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if not input_path:  # 파일을 선택하지 않은 경우 함수 종료
            return

        # 상태 초기화
        current_image = None
        current_processed_image = None

        image_label.config(image='')
        edge_label.config(image='')
        processed_label.config(image='')

        save_button.config(state=tk.DISABLED)

        lower_threshold_label.grid_remove()
        lower_threshold_slider.grid_remove()
        upper_threshold_label.grid_remove()
        upper_threshold_slider.grid_remove()

        upload_text.config(text="")
        edge_text.config(text="")
        processed_text.config(text="")

        # 새로운 이미지 로드
        current_image = cv2.imread(input_path)
        original_image = Image.open(input_path)
        update_image_display(original_image, image_label)

        # 슬라이더 표시
        lower_threshold_label.grid(row=3, column=0, padx=10, pady=10)
        lower_threshold_slider.grid(row=4, column=0, padx=10, pady=10)
        upper_threshold_label.grid(row=3, column=1, padx=10, pady=10)
        upper_threshold_slider.grid(row=4, column=1, padx=10, pady=10)

        # 경계선 및 배경 제거 미리보기 업데이트
        update_edge_preview(lower_threshold.get(), upper_threshold.get())

        # 상태 업데이트
        save_button.config(state=tk.NORMAL)
        upload_text.config(text="업로드 이미지")
        edge_text.config(text="경계선 이미지")
        processed_text.config(text="처리된 이미지")

    except Exception as e:
        messagebox.showerror("오류", f"이미지 처리 중 오류 발생: {str(e)}")


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


def create_gui():
    global image_label, edge_label, processed_label, upload_button
    global save_button, current_image, current_processed_image
    global lower_threshold, upper_threshold
    global lower_threshold_label, lower_threshold_slider, upper_threshold_label, upper_threshold_slider
    global upload_text, edge_text, processed_text

    current_image = None
    current_processed_image = None

    # 메인 창 설정
    root = tk.Tk()
    root.title("Tiltypy Studio - Edge Refinement and Image Processing")
    root.geometry("1200x800")
    root.configure(bg="#f0f0f5")

    # 커스텀 폰트 설정
    header_font = ("Helvetica", 18, "bold")
    label_font = ("Helvetica", 12)
    button_font = ("Helvetica", 14)

    # 헤더 라벨
    header_label = tk.Label(root, text="Edge Refinement and Background Removal", font=header_font, bg="#f0f0f5",
                            fg="#333")
    header_label.grid(row=0, column=0, columnspan=3, pady=20, sticky="nsew")

    # 원본 이미지 레이블
    image_label = tk.Label(root, bg="gray", relief="ridge", bd=2)
    image_label.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

    # 경계선 이미지 레이블
    edge_label = tk.Label(root, bg="gray", relief="ridge", bd=2)
    edge_label.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")

    # 처리된 이미지 레이블
    processed_label = tk.Label(root, bg="gray", relief="ridge", bd=2)
    processed_label.grid(row=1, column=2, padx=20, pady=20, sticky="nsew")

    # 텍스트 라벨
    upload_text = tk.Label(root, text="", font=label_font, bg="#f0f0f5", fg="#555")
    upload_text.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
    edge_text = tk.Label(root, text="", font=label_font, bg="#f0f0f5", fg="#555")
    edge_text.grid(row=2, column=1, padx=10, pady=5, sticky="nsew")
    processed_text = tk.Label(root, text="", font=label_font, bg="#f0f0f5", fg="#555")
    processed_text.grid(row=2, column=2, padx=10, pady=5, sticky="nsew")

    # 이미지 업로드 버튼
    upload_button = tk.Button(root, text="이미지 업로드", command=process_image, font=button_font, bg="#f0f0f5")
    upload_button.grid(row=5, column=1, pady=20, padx=10, sticky="ew")

    # 슬라이더 (초기 상태는 숨김)
    lower_threshold = tk.IntVar(value=50)
    upper_threshold = tk.IntVar(value=150)

    lower_threshold_label = tk.Label(root, text="Lower Threshold", font=label_font, bg="#f0f0f5")
    lower_threshold_slider = tk.Scale(root, from_=0, to=255, orient=tk.HORIZONTAL, variable=lower_threshold,
                                      command=lambda _: update_edge_preview(lower_threshold.get(),
                                                                            upper_threshold.get()), bg="#f0f0f5")
    upper_threshold_label = tk.Label(root, text="Upper Threshold", font=label_font, bg="#f0f0f5")
    upper_threshold_slider = tk.Scale(root, from_=0, to=255, orient=tk.HORIZONTAL, variable=upper_threshold,
                                      command=lambda _: update_edge_preview(lower_threshold.get(),
                                                                            upper_threshold.get()), bg="#f0f0f5")

    lower_threshold_label.grid_remove()
    lower_threshold_slider.grid_remove()
    upper_threshold_label.grid_remove()
    upper_threshold_slider.grid_remove()

    # 저장 버튼
    save_button = tk.Button(root, text="이미지 저장", command=save_image, state=tk.DISABLED, font=button_font,
                            bg="#f0f0f5", width=15)
    save_button.grid(row=6, column=1, pady=20, padx=10, sticky="ew")

    # Grid 가로, 세로 비율을 맞추기 위해
    for i in range(8):  # 총 8개의 행
        root.grid_rowconfigure(i, weight=1)
    for i in range(3):  # 총 3개의 열
        root.grid_columnconfigure(i, weight=1)

    root.mainloop()


if __name__ == "__main__":
    create_gui()
