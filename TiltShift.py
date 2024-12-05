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

        # 이미지, 동영상 업로드 버튼
        self.upload_button = tk.Button(root, text="Select Image or Video", command=self.select_file)
        self.upload_button.pack(pady=5)

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
        self.enhance_checkbox = tk.Checkbutton(root, text="Enhance Colors and Brightness",
                                               variable=self.enhance_var,
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
        self.video_playing = False

    def select_file(self):
        """
        파일 탐색기를 열어 이미지 또는 동영상을 선택
        """
        self.video_playing = False  # 선택 시 기존 동영상 재생 중단
        file_path = filedialog.askopenfilename(
            filetypes=[("Image and Video Files", "*.jpg;*.jpeg;*.png;*.mp4;*.avi;*.mov")]
        )
        if file_path:
            # 파일 확장자를 확인하여 처리
            _, ext = os.path.splitext(file_path)
            ext = ext.lower()
            if ext in [".jpg", ".jpeg", ".png"]:  # 이미지 파일
                self.original_filename = os.path.basename(file_path)
                self.original_image = Image.open(file_path).convert("RGB")
                self.display_image(self.original_image)

                # 버튼 활성화
                self.reset_button.config(state=tk.NORMAL)
                self.save_button.config(state=tk.NORMAL)

            elif ext in [".mp4", ".avi", ".mov"]:  # 동영상 파일
                self.original_filename = file_path  # 동영상 파일 경로 저장
                self.video_playing = True  # 동영상 재생 시작
                self.play_video(file_path)

                # 버튼 활성화
                self.reset_button.config(state=tk.NORMAL)
                self.save_button.config(state=tk.NORMAL)

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

        # 이미지 중심선 및 디버깅 로그 업데이트
        self.update_canvas_image()

    def display_video(self, frame, y_offset, new_height):
        """
        동영상을 캔버스에 표시하고 중심선 업데이트
        """
        canvas_width, canvas_height = 700, 400

        # 슬라이더 값 변환 (패딩 및 비율 고려)
        focus_position_canvas = self.focus_position_slider.get()
        focus_width_canvas = self.focus_width_slider.get()

        # 중심선 계산 (패딩 포함)
        focus_position_effect = max(0, focus_position_canvas - y_offset)
        focus_width_effect = focus_width_canvas

        # 디버깅 출력
        # print(f"[DEBUG] Video Slider focus_position (slider): {focus_position_canvas}")
        # print(f"[DEBUG] Video Slider focus_width (slider): {focus_width_canvas}")
        # print(f"[DEBUG] y_offset: {y_offset}, new_height: {new_height}")

        # 틸트-시프트 효과 적용
        blur_strength = int(self.blur_strength_slider.get())
        enhance = self.enhance_var.get()
        processed_frame = self.tilt_shift(frame, focus_position_effect, focus_width_effect, blur_strength, enhance)

        # 캔버스에 표시
        frame_image = ImageTk.PhotoImage(Image.fromarray(processed_frame))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=frame_image)
        self.canvas.image = frame_image

        # 중심선 업데이트
        self.update_canvas(canvas_width, canvas_height, focus_position_canvas, focus_width_canvas, new_height)

    def update_canvas(self, canvas_width, canvas_height, focus_position, focus_width, height):
        """
        캔버스에 중심선 및 범위 선 업데이트 (이미지와 동영상 공통 사용)
        """
        self.canvas.delete("focus_lines")  # 기존 선 제거

        # 슬라이더 값 변환
        focus_position_canvas = int(focus_position * canvas_height / height)
        focus_width_canvas = int(focus_width * canvas_height / height)

        # 디버깅 정보
        print(f"[DEBUG] Canvas focus_position: {focus_position_canvas}, focus_width: {focus_width_canvas}")

        # 중심선 및 범위 선 그리기
        self.canvas.create_line(
            0, focus_position_canvas, canvas_width, focus_position_canvas,
            fill="red", width=2, tags="focus_lines"
        )  # 초점 중심선 (빨간색)
        self.canvas.create_line(
            0, focus_position_canvas - focus_width_canvas, canvas_width, focus_position_canvas - focus_width_canvas,
            fill="blue", width=1, dash=(4, 4), tags="focus_lines"
        )  # 초점 상단 경계선 (파란색 점선)
        self.canvas.create_line(
            0, focus_position_canvas + focus_width_canvas, canvas_width, focus_position_canvas + focus_width_canvas,
            fill="blue", width=1, dash=(4, 4), tags="focus_lines"
        )  # 초점 하단 경계선 (파란색 점선)

    def update_canvas_image(self):
        """
        이미지 중심선 및 범위 선 업데이트
        """
        if self.original_image:
            canvas_width, canvas_height = 700, 400
            height = self.original_image.size[1]

            # 슬라이더 값 변환
            focus_position = int(self.focus_position_slider.get() * height / canvas_height)
            focus_width = int(self.focus_width_slider.get() * height / canvas_height)

            # 디버깅 출력
            # print(f"[DEBUG] Image Slider focus_position (slider): {self.focus_position_slider.get()}")
            # print(f"[DEBUG] Image Slider focus_width (slider): {self.focus_width_slider.get()}")
            # print(f"[DEBUG] Image Calculated focus_position: {focus_position}")
            # print(f"[DEBUG] Image Calculated focus_width: {focus_width}")
            # print(f"[DEBUG] Image original_height: {height}, canvas_height: {canvas_height}")

            # 중심선 업데이트
            self.update_canvas(canvas_width, canvas_height, focus_position, focus_width, height)

    def update_canvas_video(self, y_offset, new_height):
        """
        동영상 중심선 및 범위 선 업데이트
        """
        canvas_width, canvas_height = 700, 400

        # 슬라이더 값 변환 (패딩 포함)
        focus_position_canvas = self.focus_position_slider.get()
        focus_width_canvas = self.focus_width_slider.get()

        # 중심선과 범위 선 계산 (패딩 보정 포함)
        focus_position = max(0, focus_position_canvas - y_offset)
        focus_width = focus_width_canvas

        # 디버깅 출력
        print(f"[DEBUG] Video focus_position: {focus_position}, focus_width: {focus_width}")

        self.update_canvas(canvas_width, canvas_height, focus_position, focus_width, new_height)

    def update_preview(self, *args):
        """
        슬라이더 값 변경 시 이미지를 업데이트하여 미리보기 제공
        """
        if self.original_image is not None:
            height = self.original_image.size[1]
        elif self.video_playing:
            height = 400  # 동영상 캔버스 기준 높이
        else:
            return

        # 슬라이더 값 변환
        focus_position = int(self.focus_position_slider.get() * height / 400)
        focus_width = int(self.focus_width_slider.get() * height / 400)
        blur_strength = int(self.blur_strength_slider.get())
        enhance = self.enhance_var.get()

        if self.original_image:
            np_image = np.array(self.original_image)
            tilt_shift_result = self.tilt_shift(np_image, focus_position, focus_width, blur_strength, enhance)
            self.result_image = Image.fromarray(tilt_shift_result)
            self.display_image(self.result_image)  # 결과 이미지 표시
            self.update_canvas(700, 400, focus_position, focus_width, height)

    def reset_image(self):
        """
        원본 이미지를 복원하여 초기 상태로 리셋
        """
        if self.video_playing:  # 동영상이 재생 중인 경우
            self.stop_video()  # 동영상 재생 중단
            self.canvas.delete("all")  # 캔버스 초기화
            self.video_playing = False
        elif self.original_image is not None:  # 이미지인 경우
            self.display_image(self.original_image)  # 원본 이미지로 돌아감
            self.result_image = None  # 결과 이미지 초기화

        self.save_button.config(state=tk.DISABLED)  # 저장 버튼 비활성화

    def save_image(self):
        """
        변환된 이미지를 저장
        """
        if self.result_image is not None:  # 이미지인 경우
            default_filename = os.path.splitext(self.original_filename)[0] + "_Tilt.jpg"
            file_path = filedialog.asksaveasfilename(defaultextension=".jpg", initialfile=default_filename,
                                                     filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
            if file_path:
                self.result_image.save(file_path, "JPEG")  # 결과 이미지를 JPEG 형식으로 저장
                messagebox.showinfo("Save Image", "Image saved successfully!")  # 이미지 저장 완료 메시지
        elif self.video_playing:  # 동영상인 경우
            default_filename = os.path.splitext(self.original_filename)[0] + "_Tilt.mp4"
            file_path = filedialog.asksaveasfilename(defaultextension=".mp4", initialfile=default_filename,
                                                     filetypes=[("MP4", "*.mp4"), ("AVI", "*.avi")])
            if file_path:
                self.save_video(file_path)  # 동영상 저장 로직 호출

    def save_video(self, output_path):
        """
        변환된 동영상을 저장
        """
        if not self.original_filename:
            messagebox.showerror("Error", "No video file selected.")
            return

        cap = cv2.VideoCapture(self.original_filename)  # 원본 동영상 열기
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # MP4 코덱 설정
        fps = int(cap.get(cv2.CAP_PROP_FPS))  # 프레임 속도 가져오기
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # 원본 동영상 너비
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # 원본 동영상 높이
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))  # 동영상 저장 설정

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # 슬라이더 값 변환 (원본 해상도 기준)
            focus_position_canvas = self.focus_position_slider.get()
            focus_width_canvas = self.focus_width_slider.get()

            # 슬라이더 값을 원본 해상도에 맞게 변환
            focus_position_effect = int(focus_position_canvas * height / 400)
            focus_width_effect = int(focus_width_canvas * height / 400)

            # 틸트-시프트 효과 적용
            blur_strength = int(self.blur_strength_slider.get())
            enhance = self.enhance_var.get()
            processed_frame = self.tilt_shift(frame, focus_position_effect, focus_width_effect, blur_strength,
                                              enhance)

            # 색감 보정 적용 (필요 시)
            if enhance:
                processed_frame = self.boost_colors(processed_frame)

            # 동영상 저장
            out.write(processed_frame)  # BGR로 저장

        cap.release()
        out.release()
        messagebox.showinfo("Save Video", f"Video saved successfully to {output_path}!")  # 동영상 저장 완료 메시지

    def play_video(self, file_path):
        """
        원본 비율을 유지하면서 동영상을 캔버스에 표시하고 슬라이더 적용
        """
        cap = cv2.VideoCapture(file_path)

        def video_loop():
            if self.video_playing and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 동영상 끝나면 반복 재생
                    ret, frame = cap.read()

                if ret:
                    # BGR -> RGB 변환
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # 원본 비율 유지하며 캔버스 크기에 맞게 리사이즈
                    height, width, _ = frame.shape
                    canvas_width, canvas_height = 700, 400
                    scale = min(canvas_width / width, canvas_height / height)  # 스케일 계산
                    new_width = int(width * scale)  # 새 너비
                    new_height = int(height * scale)  # 새 높이

                    # 디버깅 출력: 리사이즈 및 스케일 정보
                    # print(f"[DEBUG] Original width: {width}, height: {height}")
                    # print(f"[DEBUG] Scale: {scale}")
                    # print(f"[DEBUG] Resized width: {new_width}, Resized height: {new_height}")

                    # 패딩 추가 (중앙 정렬)
                    padded_frame = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)
                    y_offset = (canvas_height - new_height) // 2
                    x_offset = (canvas_width - new_width) // 2
                    padded_frame[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = cv2.resize(frame,
                                                                                                             (
                                                                                                                 new_width,
                                                                                                                 new_height))

                    # 디버깅 출력: 패딩 정보
                    # print(f"[DEBUG] y_offset: {y_offset}, x_offset: {x_offset}")
                    # print(f"[DEBUG] Canvas size: {canvas_width}x{canvas_height}")
                    # print(f"[DEBUG] New frame size: {new_width}x{new_height}")

                    # 동영상 표시 및 중심선 업데이트
                    self.display_video(padded_frame, y_offset, new_height)

                # 다음 프레임 호출
                self.root.after(30, video_loop)

        self.video_playing = True
        video_loop()

    # 종료 로직 추가
    def stop_video(self):
        self.video_playing = False

    def tilt_shift(self, image, focus_position, focus_width, blur_strength, enhance):
        """
        틸트-시프트 효과 생성, 슬라이더 값은 원본 크기에 맞게 변환됨
        """
        height, width, _ = image.shape
        mask = np.zeros((height, width), dtype=np.float32)

        # 초점 너비 제한
        max_focus_width = height // 2 - 1
        focus_width = min(focus_width, max_focus_width)

        # 블러 처리 시작 범위를 초점 너비에 비례하여 설정
        blur_start = focus_width * 1.5

        for i in range(height):
            distance = abs(i - focus_position)

            if distance <= focus_width:
                mask[i, :] = 1
            elif distance <= focus_width + blur_start:
                decay_factor = (distance - focus_width) / blur_start
                mask[i, :] = max(0, 1 - decay_factor)
            else:
                mask[i, :] = 0

        # 블러 처리
        kernel_size = max(3, blur_strength | 1)
        blurred_image = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)

        # 마스크를 3채널로 확장 (R, G, B)
        mask_3ch = cv2.merge([mask, mask, mask])

        # 원본 이미지와 블러 이미지 결합
        tilt_shift_image = image * mask_3ch + blurred_image * (1 - mask_3ch)

        if enhance:
            tilt_shift_image = self.boost_colors(tilt_shift_image)

        return tilt_shift_image.clip(0, 255).astype(np.uint8)

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