import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance
import cv2
import numpy as np
import os


class TiltShiftApp:
    def __init__(self, root):
        """
        애플리케이션 초기화: UI 구성 요소 및 변수 정의
        """
        self.root = root
        self.root.title("Tiltyfy")  # 애플리케이션 제목 설정
        self.root.geometry("800x850")  # 창 크기 설정

        # UI 구성 요소: 설명 라벨
        self.label = tk.Label(root, text="Choose an image to apply Tilt-Shift effect")
        self.label.pack(pady=10)

        # 이미지를 표시할 캔버스
        self.canvas = tk.Canvas(root, width=700, height=400, bg="gray")
        self.canvas.pack(pady=10)

        # 이미지 업로드 버튼
        self.upload_button = tk.Button(root, text="Select Image", command=self.select_image)
        self.upload_button.pack(pady=5)

        # 동영상 업로드 버튼
        self.video_button = tk.Button(root, text="Select Video", command=self.select_video)
        self.video_button.pack(pady=5)

        # 슬라이더를 위한 프레임 (초점 위치, 초점 너비, 흐림 강도)
        self.slider_frame = tk.Frame(root)
        self.slider_frame.pack(pady=10)

        # 초점 위치 슬라이더
        self.focus_position_label = tk.Label(self.slider_frame, text="Focus Position")
        self.focus_position_label.grid(row=0, column=0, padx=10)
        self.focus_position_slider = tk.Scale(self.slider_frame, from_=0, to=400, orient="horizontal", length=300,
                                              command=self.update_preview)  # 슬라이더 변경 시 미리보기 업데이트
        self.focus_position_slider.set(200)
        self.focus_position_slider.grid(row=0, column=1, padx=10)

        # 초점 너비 슬라이더
        self.focus_width_label = tk.Label(self.slider_frame, text="Focus Width")
        self.focus_width_label.grid(row=1, column=0, padx=10)
        self.focus_width_slider = tk.Scale(self.slider_frame, from_=10, to=200, orient="horizontal", length=300,
                                           command=self.update_preview)
        self.focus_width_slider.set(50)
        self.focus_width_slider.grid(row=1, column=1, padx=10)

        # 흐림 강도 슬라이더
        self.blur_strength_label = tk.Label(self.slider_frame, text="Blur Strength")
        self.blur_strength_label.grid(row=2, column=0, padx=10)
        self.blur_strength_slider = tk.Scale(self.slider_frame, from_=21, to=81, orient="horizontal", length=300,
                                             resolution=2, command=self.update_preview)
        self.blur_strength_slider.set(15)
        self.blur_strength_slider.grid(row=2, column=1, padx=10)

        # 색상 및 밝기 강화 체크박스
        self.enhance_var = tk.BooleanVar(value=True)
        self.enhance_checkbox = tk.Checkbutton(root, text="Enhance Colors and Brightness", variable=self.enhance_var,
                                               command=self.update_preview)
        self.enhance_checkbox.pack(pady=5)

        # 초기화 버튼
        self.reset_button = tk.Button(root, text="Reset", command=self.reset_image, state=tk.DISABLED)
        self.reset_button.pack(pady=5)

        # 저장 버튼
        self.save_button = tk.Button(root, text="Save Result", command=self.save_image, state=tk.DISABLED)
        self.save_button.pack(pady=5)

        # 이미지 관련 변수 초기화
        self.original_image = None  # 원본 이미지 저장
        self.result_image = None  # 변환된 이미지 저장
        self.image_ratio = 1.0  # 원본 이미지와 캔버스 이미지의 크기 비율
        self.original_filename = None  # 원본 이미지 파일 이름

        # 동영상 중단 플래그 초기화
        self.stop_video = False

    def select_image(self):
        """
        파일 탐색기를 열어 이미지를 선택하고 애플리케이션에 로드
        """
        self.stop_video = True  # 이미지 선택 시 동영상 재생 중단
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
        if file_path:
            self.original_filename = os.path.basename(file_path)  # 파일 이름 추출
            self.original_image = Image.open(file_path).convert("RGB")  # PIL 이미지를 RGB 형식으로 변환
            self.display_image(self.original_image)  # 선택된 이미지를 화면에 표시
            self.reset_button.config(state=tk.NORMAL)  # 초기화 버튼 활성화
            self.save_button.config(state=tk.NORMAL)  # 저장 버튼 활성화

    def display_image(self, image):
        """
        이미지를 캔버스에 표시
        """
        self.canvas.delete("all")  # 기존 캔버스 내용 삭제
        original_width, original_height = image.size
        resized_height = 400  # 캔버스 높이에 맞게 이미지 리사이즈
        self.image_ratio = original_height / resized_height  # 크기 비율 계산
        resized_image = image.resize((700, resized_height), Image.LANCZOS)  # 고품질 리사이즈
        image_tk = ImageTk.PhotoImage(resized_image)  # tkinter에서 표시 가능한 형식으로 변환
        self.canvas.image = image_tk
        self.canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)

    def update_canvas(self, *args):
        """
        슬라이더 값에 따라 중심선 및 범위 선 업데이트
        """
        self.canvas.delete("focus_lines")  # 이전 선 제거

        # 슬라이더 값 가져오기 및 비율 변환
        focus_position = int(self.focus_position_slider.get() * self.image_ratio)  # 초점 위치를 원본 비율로 변환
        focus_width = int(self.focus_width_slider.get() * self.image_ratio)  # 초점 너비를 원본 비율로 변환

        # 캔버스에 맞게 변환된 값 계산
        focus_position_canvas = int(focus_position / self.image_ratio)  # 캔버스 높이에 맞춘 초점 위치
        focus_width_canvas = int(focus_width / self.image_ratio)  # 캔버스 높이에 맞춘 초점 너비

        # 캔버스에 선 그리기
        self.focus_line = self.canvas.create_line(
            0, focus_position_canvas, 700, focus_position_canvas, fill="red", width=2, tags="focus_lines"
        )  # 초점 중심선 (빨간색)
        self.top_line = self.canvas.create_line(
            0, focus_position_canvas - focus_width_canvas, 700, focus_position_canvas - focus_width_canvas,
            fill="blue", width=1, dash=(4, 4), tags="focus_lines"
        )  # 초점 상단 경계선 (파란색 점선)
        self.bottom_line = self.canvas.create_line(
            0, focus_position_canvas + focus_width_canvas, 700, focus_position_canvas + focus_width_canvas,
            fill="blue", width=1, dash=(4, 4), tags="focus_lines"
        )  # 초점 하단 경계선 (파란색 점선)

    def update_preview(self, *args):
        """
        슬라이더 값 변경 시 이미지를 업데이트하여 미리보기 제공
        """
        if self.original_image is not None:
            # 슬라이더 값을 통해 효과 적용
            focus_position = int(self.focus_position_slider.get() * self.image_ratio)
            focus_width = int(self.focus_width_slider.get() * self.image_ratio)
            blur_strength = int(self.blur_strength_slider.get())
            enhance = self.enhance_var.get()

            # PIL 이미지를 NumPy 배열로 변환
            np_image = np.array(self.original_image)
            tilt_shift_result = self.tilt_shift(np_image, focus_position, focus_width, blur_strength, enhance)
            self.result_image = Image.fromarray(tilt_shift_result)  # NumPy 배열을 PIL 이미지로 변환
            self.display_image(self.result_image)  # 변환 결과를 캔버스에 표시
            self.update_canvas()  # 중심선 및 경계선 업데이트

    def reset_image(self):
        """
        원본 이미지를 복원하여 초기 상태로 리셋
        """
        if self.original_image is not None:
            self.display_image(self.original_image)  # 원본 이미지로 돌아감
            self.result_image = None  # 결과 이미지 초기화
            self.save_button.config(state=tk.DISABLED)  # 저장 버튼 비활성화

    def save_image(self):
        """
        변환된 이미지를 저장
        """
        if self.result_image is not None:
            default_filename = os.path.splitext(self.original_filename)[0] + "_Tilt.jpg"
            file_path = filedialog.asksaveasfilename(defaultextension=".jpg", initialfile=default_filename,
                                                     filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
            if file_path:
                self.result_image.save(file_path, "JPEG")  # 결과 이미지를 JPEG 형식으로 저장
                messagebox.showinfo("Save Image", "Image saved successfully!")  # 저장 완료 메시지

    def select_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov")])
        if file_path:
            self.stop_video = False  # 동영상 재생 중단 플래그 초기화
            self.play_video(file_path)

    def play_video(self, file_path):
        cap = cv2.VideoCapture(file_path)

        def video_loop():
            if not self.stop_video and cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    # OpenCV 이미지를 RGB로 변환 및 리사이즈
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = cv2.resize(frame, (700, 400))
                    frame_image = ImageTk.PhotoImage(Image.fromarray(frame))

                    # 캔버스에 표시
                    self.canvas.create_image(0, 0, anchor=tk.NW, image=frame_image)
                    self.canvas.image = frame_image

                    # 다음 프레임 호출
                    self.root.after(30, video_loop)
                else:
                    cap.release()  # 동영상 종료 시 자원 해제

        video_loop()  # 재생 시작

    # 종료 로직 추가
    def stop_video(self):
        self.stop_video = True


    def tilt_shift(self, image, focus_position, focus_width, blur_strength, enhance):
        """
        틸트 시프트 효과 생성
        """
        height, width, _ = image.shape
        mask = np.zeros((height, width), dtype=np.float32)

        # 초점 너비 제한
        max_focus_width = height // 2 - 1
        focus_width = min(focus_width, max_focus_width)

        # 블러 처리 시작 범위를 초점 너비에 비례하여 설정
        blur_start = focus_width * 1.5  # 초점 너비에 따라 블러 처리 시작 거리 설정

        for i in range(height):
            distance = abs(i - focus_position)

            if distance <= focus_width:
                # 초점 영역: 선명한 값을 유지
                mask[i, :] = 1
            elif distance <= focus_width + blur_start:
                # 초점 영역과 블러 처리 영역 사이의 선형 감소 (점진적 블러 처리)
                decay_factor = (distance - focus_width) / blur_start
                mask[i, :] = max(0, 1 - decay_factor)  # 선형 감소
            else:
                # 블러 처리 영역 : 이 영역에서는 원본 이미지가 사용되지 않고 블러 처리된 이미지만 사용
                mask[i, :] = 0

        # 블러 처리
        kernel_size = max(3, blur_strength | 1)  # 홀수 보장 -> 가우시안 블러 연산에서 커널 크기는 홀수여야만 중심 픽셀이 올바르게 계산되므로
        blurred_image = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)

        # 마스크를 3채널로 확장 (R, G, B)
        mask_3ch = cv2.merge([mask, mask, mask])

        # 원본 이미지에서 선명한 영역 + 블러 처리된 이미지에서 흐릿한 영역
        tilt_shift_image = image * mask_3ch + blurred_image * (1 - mask_3ch)

        # 체크 박스를 체크할때만 색감 보정(boost_colors) 적용
        if enhance:
            tilt_shift_image = self.boost_colors(tilt_shift_image)

        # uint8로 변환하여 반환
        tilt_shift_image = tilt_shift_image.clip(0, 255).astype(np.uint8)
        return tilt_shift_image

    def boost_colors(self, image):
        """
        채도, 밝기 및 대비를 조정하여 이미지 더욱 미니어쳐스럽게 보정
        """
        pil_image = Image.fromarray(image.astype(np.uint8))  # NumPy 배열을 PIL 이미지로 변환

        # 채도 강화
        color_enhancer = ImageEnhance.Color(pil_image)
        enhanced_image = color_enhancer.enhance(1.5)

        # 밝기 강화
        brightness_enhancer = ImageEnhance.Brightness(enhanced_image)
        enhanced_image = brightness_enhancer.enhance(1.1)

        # 대비 감소
        contrast_enhancer = ImageEnhance.Contrast(enhanced_image)
        enhanced_image = contrast_enhancer.enhance(0.8)

        return np.array(enhanced_image, dtype=np.uint8)


if __name__ == "__main__":
    root = tk.Tk()
    app = TiltShiftApp(root)
    root.mainloop()