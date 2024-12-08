import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2


class ImageVideoProcessor:
    def __init__(self, root):
        # GUI 초기 설정
        self.root = root
        self.root.title("Tiltypy Studio - Image and Video Processor")
        self.root.geometry("900x950")  # 창 크기 설정
        self.root.configure(bg="#f0f0f5")  # 배경 색상 설정

        self.filepath = None  # 현재 파일 경로
        self.cap = None  # 비디오 캡처 객체
        self.video_playing = False
        self.original_image = None  # 원본 이미지 저장
        self.current_image = None  # 현재 상태의 이미지 저장
        self.operation_stack = []  # 작업 기록 스택

        # 폰트 설정
        self.header_font = ("Helvetica", 18, "bold")
        self.button_font = ("Helvetica", 12)

        # 헤더 라벨
        self.header_label = tk.Label(root, text="Tiltypy Studio", font=self.header_font, bg="#f0f0f5", fg="#333")
        self.header_label.pack(pady=10)

        # 설명 라벨
        self.description_label = tk.Label(root, text="Process images and videos with various tools!",
                                          font=("Helvetica", 12), bg="#f0f0f5", fg="#555")
        self.description_label.pack(pady=5)

        # 캔버스 (이미지 및 비디오 표시)
        self.canvas = tk.Canvas(root, width=800, height=450, bg="gray", relief="ridge", bd=2)
        self.canvas.pack(pady=20)
        self.canvas_image = self.canvas.create_image(400, 225, anchor="center")

        # 버튼 및 슬라이더 레이아웃 프레임
        self.central_frame = tk.Frame(root, bg="#f0f0f5")
        self.central_frame.pack(pady=20)

        # 첫 번째 행: Load 및 Reset 버튼
        self.load_button = tk.Button(self.central_frame, text="Load Image/Video", font=self.button_font,
                                     bg="#f0f0f5", command=self.load_file, width=20)
        self.load_button.grid(row=0, column=0, padx=5, pady=10)

        self.reset_button = tk.Button(self.central_frame, text="Reset", font=self.button_font,
                                      bg="#f0f0f5", command=self.reset, width=20)
        self.reset_button.grid(row=0, column=1, padx=5, pady=10)

        # 두 번째 행: Flip 버튼
        self.flip_horizontal_button = tk.Button(self.central_frame, text="Flip Horizontal", font=self.button_font,
                                                bg="#f0f0f5", command=self.flip_horizontal, width=20)
        self.flip_horizontal_button.grid(row=1, column=0, padx=5, pady=5)

        self.flip_vertical_button = tk.Button(self.central_frame, text="Flip Vertical", font=self.button_font,
                                              bg="#f0f0f5", command=self.flip_vertical, width=20)
        self.flip_vertical_button.grid(row=1, column=1, padx=5, pady=5)

        # 세 번째 행: Rotate 버튼
        self.rotate_left_button = tk.Button(self.central_frame, text="Rotate Left (-90°)", font=self.button_font,
                                            bg="#f0f0f5", command=self.rotate_left, width=20)
        self.rotate_left_button.grid(row=2, column=0, padx=5, pady=5)

        self.rotate_right_button = tk.Button(self.central_frame, text="Rotate Right (90°)", font=self.button_font,
                                             bg="#f0f0f5", command=self.rotate_right, width=20)
        self.rotate_right_button.grid(row=2, column=1, padx=5, pady=5)

        # 네 번째 행: Grayscale 버튼
        self.grayscale_button = tk.Button(self.central_frame, text="Grayscale", font=self.button_font,
                                          bg="#f0f0f5", command=self.grayscale, width=43)
        self.grayscale_button.grid(row=3, column=0, columnspan=2, pady=5)

        # 다섯 번째 행: Blur 버튼 및 슬라이더
        self.blur_button = tk.Button(self.central_frame, text="Blur", font=self.button_font,
                                     bg="#f0f0f5", command=self.blur, width=20)
        self.blur_button.grid(row=4, column=0, padx=5, pady=5)

        blur_frame = tk.Frame(self.central_frame, bg="#f0f0f5")
        blur_frame.grid(row=4, column=1, sticky="w")

        self.blur_slider_label = tk.Label(blur_frame, text="Blur Intensity:", font=("Helvetica", 10),
                                          bg="#f0f0f5", fg="#555")
        self.blur_slider_label.pack(side="left", padx=5)

        self.blur_slider = tk.Scale(blur_frame, from_=1, to=31, orient=tk.HORIZONTAL, bg="#f0f0f5", width=10)
        self.blur_slider.set(15)
        self.blur_slider.pack(side="left", padx=5)

        # 여섯 번째 행: Resize 버튼 및 입력 필드
        self.resize_button = tk.Button(self.central_frame, text="Resize", font=self.button_font,
                                       bg="#f0f0f5", command=self.resize, width=20)
        self.resize_button.grid(row=5, column=0, padx=5, pady=5)

        resize_frame = tk.Frame(self.central_frame, bg="#f0f0f5")
        resize_frame.grid(row=5, column=1, sticky="w")

        self.resize_width_label = tk.Label(resize_frame, text="Width:", font=("Helvetica", 10),
                                           bg="#f0f0f5", fg="#555")
        self.resize_width_label.pack(side="left", padx=5)

        self.resize_width_entry = tk.Entry(resize_frame, width=5)
        self.resize_width_entry.pack(side="left", padx=5)

        self.resize_height_label = tk.Label(resize_frame, text="Height:", font=("Helvetica", 10),
                                            bg="#f0f0f5", fg="#555")
        self.resize_height_label.pack(side="left", padx=5)

        self.resize_height_entry = tk.Entry(resize_frame, width=5)
        self.resize_height_entry.pack(side="left", padx=5)

        # Save 버튼
        self.save_button = tk.Button(root, text="Save Result", font=self.button_font,
                                     bg="#f0f0f5", command=self.save_result, width=30)
        self.save_button.pack(pady=5)

    def load_file(self):
        """
        파일 선택 후 이미지 또는 비디오 로드.
        """
        self.filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg"), ("Video Files", "*.mp4")])
        if not self.filepath:
            messagebox.showerror("Error", "No file selected!")
            return

        # 이미지 파일 로드
        if self.filepath.lower().endswith('.jpg'):
            img = cv2.imread(self.filepath)
            if img is None:
                messagebox.showerror("Error", "Could not load image!")
                return

            # RGB로 변환
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # 비율을 유지하며 캔버스 크기에 맞게 리사이즈
            canvas_width, canvas_height = 800, 450
            img_resized = self.resize_to_canvas(img_rgb, canvas_width, canvas_height)

            # original_image와 current_image 초기화
            self.original_image = img_resized.copy()
            self.current_image = img_resized.copy()

            # Resize 여부 초기화
            self.was_resized = False  # 새로운 파일 로드 시 초기화

            # 캔버스에 표시
            self.update_canvas_image()

        # 비디오 파일 로드
        elif self.filepath.lower().endswith('.mp4'):
            self.cap = cv2.VideoCapture(self.filepath)
            if not self.cap.isOpened():
                messagebox.showerror("Error", "Could not open video file!")
                return
            self.video_playing = True
            self.play_video()

        else:
            messagebox.showerror("Error", "Unsupported file format!")

    @staticmethod
    def resize_to_canvas(img, canvas_width, canvas_height):
        """
        이미지를 비율에 맞게 캔버스 크기로 리사이즈.
        """
        h, w, _ = img.shape
        aspect_ratio = w / h

        if aspect_ratio > canvas_width / canvas_height:  # 가로 기준으로 맞춤
            new_width = canvas_width
            new_height = int(canvas_width / aspect_ratio)
        else:  # 세로 기준으로 맞춤
            new_height = canvas_height
            new_width = int(canvas_height * aspect_ratio)

        return cv2.resize(img, (new_width, new_height))

    def apply_operations(self):
        """
        작업 스택을 기반으로 이미지를 변환.
        """
        if self.original_image is None:
            messagebox.showerror("Error", "No image loaded!")
            return

        temp_image = self.original_image.copy()

        # 작업 순서대로 적용
        for operation in self.operation_stack:
            if operation['type'] == 'grayscale': # 흑백 처리
                temp_image = cv2.cvtColor(temp_image, cv2.COLOR_BGR2GRAY)
                temp_image = cv2.cvtColor(temp_image, cv2.COLOR_GRAY2BGR)

            elif operation['type'] == 'blur':   # 블러 처리
                kernel_size = operation.get('kernel', 5)
                temp_image = cv2.GaussianBlur(temp_image, (kernel_size, kernel_size), 0)

            elif operation['type'] == 'resize': # 크키 조정
                width, height = operation.get('size', (temp_image.shape[1], temp_image.shape[0]))
                temp_image = cv2.resize(temp_image, (width, height))

            elif operation['type'] == 'flip_horizontal': # 좌우 대칭
                temp_image = cv2.flip(temp_image, 1)

            elif operation['type'] == 'flip_vertical':  # 상하 대칭
                temp_image = cv2.flip(temp_image, 0)

            elif operation['type'] == 'rotate_right':   # +90도 회전
                temp_image = self.rotate_and_resize(temp_image, 90)

            elif operation['type'] == 'rotate_left':    # -90도 회전
                temp_image = self.rotate_and_resize(temp_image, -90)

        self.current_image = temp_image
        self.update_canvas_image()

    def update_canvas_image(self):
        """
        현재 이미지를 캔버스에 업데이트.
        """
        if self.current_image is None:
            return

        img_pil = Image.fromarray(self.current_image)
        img_tk = ImageTk.PhotoImage(img_pil)
        self.display_image(img_tk)

    def display_image(self, img_tk):
        """
        캔버스에 이미지를 표시.
        """
        self.canvas.itemconfig(self.canvas_image, image=img_tk)
        self.canvas.image = img_tk

    def play_video(self):
        """
        비디오를 재생.
        """
        if self.cap.isOpened() and self.video_playing:
            ret, frame = self.cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_pil = Image.fromarray(frame_rgb)
                frame_tk = ImageTk.PhotoImage(frame_pil)
                self.display_image(frame_tk)
                self.root.after(10, self.play_video)
            else:
                self.cap.release()

    # Placeholder methods
    def grayscale(self):
        if not hasattr(self, 'operation_stack'):
            self.operation_stack = []

        if any(op['type'] == 'grayscale' for op in self.operation_stack):
            # 흑백 해제
            self.operation_stack = [op for op in self.operation_stack if op['type'] != 'grayscale']
        else:
            # 흑백 추가
            self.operation_stack.append({'type': 'grayscale'})

        self.apply_operations()

    def blur(self):
        if not hasattr(self, 'operation_stack'):
            self.operation_stack = []

        kernel_size = int(self.blur_slider.get()) if hasattr(self, 'blur_slider') else 5
        if kernel_size % 2 == 0:
            kernel_size += 1

        if any(op['type'] == 'blur' for op in self.operation_stack):
            # 블러 해제
            self.operation_stack = [op for op in self.operation_stack if op['type'] != 'blur']
        else:
            # 블러 추가
            self.operation_stack.append({'type': 'blur', 'kernel': kernel_size})

        self.apply_operations()

    def resize(self):
        """
        사용자가 지정한 크기로 이미지를 리사이즈.
        """
        if not hasattr(self, 'operation_stack'):
            self.operation_stack = []

        width = self.get_input(self.resize_width_entry)
        height = self.get_input(self.resize_height_entry)
        if not (width and height):
            return

        # 기존 리사이즈 작업 제거 후 새 작업 추가
        self.operation_stack = [op for op in self.operation_stack if op['type'] != 'resize']
        self.operation_stack.append({'type': 'resize', 'size': (width, height)})

        # 사용자 Resize 플래그 설정
        self.was_resized = True

        self.apply_operations()

    def rotate_and_resize(self, img, angle):
        """
        이미지를 회전하고, Resize 여부에 따라 캔버스 크기에 맞게 조정.
        """
        # 회전 행렬 생성
        h, w = img.shape[:2]
        center = (w // 2, h // 2)

        # OpenCV의 좌표계 때문에 각도를 반전
        rotation_matrix = cv2.getRotationMatrix2D(center, -angle, 1)  # 각도를 반전(-angle)

        # 회전 후 새로운 크기 계산 (외곽 상자의 크기)
        cos = abs(rotation_matrix[0, 0])
        sin = abs(rotation_matrix[0, 1])
        new_width = int((h * sin) + (w * cos))
        new_height = int((h * cos) + (w * sin))

        # 회전 행렬에 중심 이동 반영
        rotation_matrix[0, 2] += (new_width / 2) - center[0]
        rotation_matrix[1, 2] += (new_height / 2) - center[1]

        # warpAffine 함수를 사용한 회전 적용
        rotated_img = cv2.warpAffine(img, rotation_matrix, (new_width, new_height))

        # 사용자 Resize 여부에 따라 리사이즈 적용
        if self.was_resized:
            # Resize 상태인 경우, 리사이즈하지 않고 원래 크기 유지
            return rotated_img
        else:
            # Resize 상태가 아닌 경우 캔버스 크기에 맞게 리사이즈
            return self.resize_to_canvas(rotated_img, 800, 450)

    @staticmethod
    def get_input(entry):
        try:
            return int(entry.get())
        except ValueError:
            messagebox.showerror("오류", "유효하지 않은 입력입니다")
            return None

    def flip_horizontal(self):
        if not hasattr(self, 'operation_stack'):
            self.operation_stack = []

        if any(op['type'] == 'flip_horizontal' for op in self.operation_stack):
            # 좌우 반전 해제
            self.operation_stack = [op for op in self.operation_stack if op['type'] != 'flip_horizontal']
        else:
            # 좌우 반전 추가
            self.operation_stack.append({'type': 'flip_horizontal'})

        self.apply_operations()

    def flip_vertical(self):
        if not hasattr(self, 'operation_stack'):
            self.operation_stack = []

        if any(op['type'] == 'flip_vertical' for op in self.operation_stack):
            # 상하 반전 해제
            self.operation_stack = [op for op in self.operation_stack if op['type'] != 'flip_vertical']
        else:
            # 상하 반전 추가
            self.operation_stack.append({'type': 'flip_vertical'})

        self.apply_operations()

    def rotate_right(self):
        if not hasattr(self, 'operation_stack'):
            self.operation_stack = []

        # 오른쪽 회전 추가
        self.operation_stack.append({'type': 'rotate_right'})
        self.apply_operations()

    def rotate_left(self):
        if not hasattr(self, 'operation_stack'):
            self.operation_stack = []

        # 왼쪽 회전 추가
        self.operation_stack.append({'type': 'rotate_left'})
        self.apply_operations()

    def reset(self):
        """
        작업 초기화 및 원본 상태로 복원
        """
        if self.original_image is not None:
            self.current_image = self.original_image.copy()
            self.operation_stack = []  # 모든 작업 초기화
            self.was_resized = False  # Resize 여부 초기화
            self.update_canvas_image()
        else:
            messagebox.showerror("Error", "No image to reset!")

    def save_result(self):
        """
        현재 상태의 이미지를 저장
        """
        if self.current_image is not None:
            save_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                     filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")])
            if save_path:
                save_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
                Image.fromarray(save_image).save(save_path)
                messagebox.showinfo("Saved", f"Image saved to {save_path}")
        else:
            messagebox.showerror("Error", "No image to save!")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageVideoProcessor(root)
    root.mainloop()
