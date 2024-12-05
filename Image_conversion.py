import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk


class ImageVideoProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("이미지 및 비디오 처리기")
        self.root.geometry("1000x600")  # 창 크기 설정
        self.filepath = None
        self.cap = None
        self.video_playing = False

        # Create a frame to contain the buttons and the image/video display
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas for scrolling
        self.canvas = tk.Canvas(self.main_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a vertical scrollbar
        self.scrollbar = tk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.config(yscrollcommand=self.scrollbar.set)

        # Create a frame within the canvas to hold the image/video
        self.canvas_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.canvas_frame, anchor=tk.NW)

        # Create buttons and place them on the left
        self.button_frame = tk.Frame(self.canvas_frame)
        self.button_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        self.load_button = tk.Button(self.button_frame, text="이미지/비디오 불러오기", command=self.load_file)
        self.load_button.grid(row=0, column=0, padx=10, pady=10)

        self.show_button = tk.Button(self.button_frame, text="이미지/비디오 보기", command=self.show_file)
        self.show_button.grid(row=1, column=0, padx=10, pady=10)

        self.resize_button = tk.Button(self.button_frame, text="이미지 크기 조정", command=self.resize)
        self.resize_button.grid(row=2, column=0, padx=10, pady=10)

        # Resize input fields
        self.resize_width_label = tk.Label(self.button_frame, text="너비:")
        self.resize_width_label.grid(row=3, column=0, padx=10, pady=5)
        self.resize_width_entry = tk.Entry(self.button_frame)
        self.resize_width_entry.grid(row=3, column=1, padx=10, pady=5)

        self.resize_height_label = tk.Label(self.button_frame, text="높이:")
        self.resize_height_label.grid(row=4, column=0, padx=10, pady=5)
        self.resize_height_entry = tk.Entry(self.button_frame)
        self.resize_height_entry.grid(row=4, column=1, padx=10, pady=5)

        self.flip_button = tk.Button(self.button_frame, text="이미지/비디오 뒤집기", command=self.flip)
        self.flip_button.grid(row=5, column=0, padx=10, pady=10)

        # Flip input field with simplified explanation
        self.flip_type_label = tk.Label(self.button_frame, text="뒤집기 타입 (0=상하대칭, 1=좌우대칭):")
        self.flip_type_label.grid(row=6, column=0, padx=10, pady=5)
        self.flip_type_entry = tk.Entry(self.button_frame)
        self.flip_type_entry.grid(row=6, column=1, padx=10, pady=5)

        self.rotate_button = tk.Button(self.button_frame, text="이미지/비디오 회전", command=self.rotate)
        self.rotate_button.grid(row=7, column=0, padx=10, pady=10)

        # Rotate input field with simplified explanation
        self.rotate_type_label = tk.Label(self.button_frame, text="회전 타입 (1=90°, 2=180°, 3=-90°):")
        self.rotate_type_label.grid(row=8, column=0, padx=10, pady=5)
        self.rotate_type_entry = tk.Entry(self.button_frame)
        self.rotate_type_entry.grid(row=8, column=1, padx=10, pady=5)

        self.grayscale_button = tk.Button(self.button_frame, text="흑백 처리", command=self.grayscale)
        self.grayscale_button.grid(row=9, column=0, padx=10, pady=10)

        self.blur_button = tk.Button(self.button_frame, text="블러 처리", command=self.blur)
        self.blur_button.grid(row=10, column=0, padx=10, pady=10)

        self.blur_slider_label = tk.Label(self.button_frame, text="블러 정도:")
        self.blur_slider_label.grid(row=11, column=0, padx=10, pady=5)

        self.blur_slider = tk.Scale(self.button_frame, from_=1, to=31, orient=tk.HORIZONTAL)
        self.blur_slider.set(15)  # 기본값 설정
        self.blur_slider.grid(row=11, column=1, padx=10, pady=5)

        self.quit_button = tk.Button(self.button_frame, text="종료", command=root.quit)
        self.quit_button.grid(row=12, column=0, padx=10, pady=10)

        self.image_label = tk.Label(self.canvas_frame)
        self.image_label.grid(row=0, column=1, rowspan=6)

    def load_file(self):
        # Open file dialog to select image (.jpg) or video (.mp4)
        self.filepath = filedialog.askopenfilename(filetypes=[("이미지 파일", "*.jpg"), ("비디오 파일", "*.mp4")])
        if not self.filepath:
            messagebox.showerror("오류", "파일을 선택하지 않았습니다")

    def show_file(self):
        if not self.filepath:
            messagebox.showerror("오류", "파일이 로드되지 않았습니다")
            return
        # If image file
        if self.filepath.lower().endswith('jpg'):
            img = cv2.imread(self.filepath)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            img_tk = ImageTk.PhotoImage(img_pil)
            self.display_image(img_tk)
        # If video file
        elif self.filepath.lower().endswith('mp4'):
            self.cap = cv2.VideoCapture(self.filepath)
            if not self.cap.isOpened():
                messagebox.showerror("오류", "비디오 파일을 열 수 없습니다")
                return
            self.video_playing = True
            self.play_video()

    def display_image(self, img_tk):
        self.image_label.config(image=img_tk)
        self.image_label.image = img_tk

    def play_video(self):
        if self.cap.isOpened() and self.video_playing:
            ret, frame = self.cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_pil = Image.fromarray(frame_rgb)
                frame_tk = ImageTk.PhotoImage(frame_pil)
                self.display_image(frame_tk)
                self.root.after(10, self.play_video)  # Continue video playback
            else:
                self.cap.release()

    def resize(self):
        if not self.filepath:
            messagebox.showerror("오류", "파일이 로드되지 않았습니다")
            return

        # 사용자 입력값 가져오기
        width = self.get_input(self.resize_width_entry)
        height = self.get_input(self.resize_height_entry)

        if not (width and height):
            return

        # 이미지 처리
        if self.filepath.lower().endswith('jpg'):
            if not hasattr(self, 'current_image') or self.current_image is None:
                self.current_image = cv2.imread(self.filepath)

            self.current_image = cv2.resize(self.current_image, (width, height))
            resized_img_rgb = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
            resized_img_pil = Image.fromarray(resized_img_rgb)
            resized_img_tk = ImageTk.PhotoImage(resized_img_pil)
            self.display_image(resized_img_tk)

        # 비디오 처리
        elif self.filepath.lower().endswith('mp4'):
            self.cap = cv2.VideoCapture(self.filepath)
            if not self.cap.isOpened():
                messagebox.showerror("오류", "비디오 파일을 열 수 없습니다")
                return

            while self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    break

                resized_frame = cv2.resize(frame, (width, height))
                resized_frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
                resized_frame_pil = Image.fromarray(resized_frame_rgb)
                resized_frame_tk = ImageTk.PhotoImage(resized_frame_pil)
                self.display_image(resized_frame_tk)

                if cv2.waitKey(1) == ord('q'):
                    break

            self.cap.release()

    def flip(self):
        if not self.filepath:
            messagebox.showerror("오류", "파일이 로드되지 않았습니다")
            return

        # 사용자 입력값 가져오기
        raw_flip_type = self.flip_type_entry.get()
        if not raw_flip_type.strip():
            messagebox.showerror("오류", "뒤집기 타입을 입력하세요 (0=상하대칭, 1=좌우대칭)")
            return

        try:
            flip_type = int(raw_flip_type)
            if flip_type not in [0, 1]:
                messagebox.showerror("오류", "유효한 뒤집기 타입을 입력하세요 (0 또는 1만 가능)")
                return
        except ValueError:
            messagebox.showerror("오류", "뒤집기 타입은 숫자로 입력해야 합니다")
            return

        # 이미지 처리
        if self.filepath.lower().endswith('jpg'):
            if not hasattr(self, 'current_image') or self.current_image is None:
                self.current_image = cv2.imread(self.filepath)

            self.current_image = cv2.flip(self.current_image, flip_type)
            flipped_img_rgb = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
            flipped_img_pil = Image.fromarray(flipped_img_rgb)
            flipped_img_tk = ImageTk.PhotoImage(flipped_img_pil)
            self.display_image(flipped_img_tk)

        # 비디오 처리
        elif self.filepath.lower().endswith('mp4'):
            self.cap = cv2.VideoCapture(self.filepath)
            if not self.cap.isOpened():
                messagebox.showerror("오류", "비디오 파일을 열 수 없습니다")
                return

            while self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    break

                flipped_frame = cv2.flip(frame, flip_type)
                flipped_frame_rgb = cv2.cvtColor(flipped_frame, cv2.COLOR_BGR2RGB)
                flipped_frame_pil = Image.fromarray(flipped_frame_rgb)
                flipped_frame_tk = ImageTk.PhotoImage(flipped_frame_pil)
                self.display_image(flipped_frame_tk)

                if cv2.waitKey(1) == ord('q'):
                    break

            self.cap.release()

    def rotate(self):
        if not self.filepath:
            messagebox.showerror("오류", "파일이 로드되지 않았습니다")
            return

        rotate_type = self.get_input(self.rotate_type_entry)
        if rotate_type not in [1, 2, 3]:
            messagebox.showerror("오류", "유효한 회전 타입을 입력하세요 (1=90°, 2=180°, 3=-90°)")
            return

        rotate_map = {
            1: cv2.ROTATE_90_CLOCKWISE,
            2: cv2.ROTATE_180,
            3: cv2.ROTATE_90_COUNTERCLOCKWISE
        }

        # 이미지 처리
        if self.filepath.lower().endswith('jpg'):
            if not hasattr(self, 'current_image') or self.current_image is None:
                self.current_image = cv2.imread(self.filepath)

            self.current_image = cv2.rotate(self.current_image, rotate_map[rotate_type])
            rotated_img_rgb = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
            rotated_img_pil = Image.fromarray(rotated_img_rgb)
            rotated_img_tk = ImageTk.PhotoImage(rotated_img_pil)
            self.display_image(rotated_img_tk)

        # 비디오 처리
        elif self.filepath.lower().endswith('mp4'):
            self.cap = cv2.VideoCapture(self.filepath)
            if not self.cap.isOpened():
                messagebox.showerror("오류", "비디오 파일을 열 수 없습니다")
                return

            while self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    break

                rotated_frame = cv2.rotate(frame, rotate_map[rotate_type])
                rotated_frame_rgb = cv2.cvtColor(rotated_frame, cv2.COLOR_BGR2RGB)
                rotated_frame_pil = Image.fromarray(rotated_frame_rgb)
                rotated_frame_tk = ImageTk.PhotoImage(rotated_frame_pil)
                self.display_image(rotated_frame_tk)

                if cv2.waitKey(1) == ord('q'):
                    break

            self.cap.release()

    def grayscale(self):
        if not self.filepath:
            messagebox.showerror("오류", "파일이 로드되지 않았습니다")
            return

        # 초기 상태 설정
        if not hasattr(self, 'is_grayscale'):
            self.is_grayscale = False  # 흑백 상태 초기화

        if not hasattr(self, 'current_image') or self.current_image is None:
            self.current_image = cv2.imread(self.filepath)  # 초기 이미지 로드

        if not hasattr(self, 'original_image') or self.original_image is None:
            # 흑백 처리 전의 이미지를 저장
            self.original_image = self.current_image.copy()

        # 흑백 처리 토글
        if self.is_grayscale:
            # 흑백 해제: 흑백 처리 이전 상태로 복원
            self.current_image = self.original_image.copy()
            self.is_grayscale = False
        else:
            # 현재 상태에서 흑백 변환
            gray_img = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
            self.current_image = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)
            self.is_grayscale = True

        # Tkinter 이미지 변환 및 표시
        img_rgb = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(img_pil)
        self.display_image(img_tk)

    def blur(self):
        if not self.filepath:
            messagebox.showerror("오류", "파일이 로드되지 않았습니다")
            return

        # 초기 상태 설정
        if not hasattr(self, 'is_blurred'):
            self.is_blurred = False  # 블러 상태 초기화

        if not hasattr(self, 'current_image') or self.current_image is None:
            self.current_image = cv2.imread(self.filepath)  # 초기 이미지 로드

        kernel_size = int(self.blur_slider.get())
        if kernel_size % 2 == 0:
            kernel_size += 1  # 홀수 커널 크기만 허용

        if not hasattr(self, 'original_image') or self.original_image is None:
            # 블러 처리 전의 이미지를 저장
            self.original_image = self.current_image.copy()

        # 블러 처리 토글
        if self.is_blurred:
            # 블러 해제: 블러 처리 이전 상태로 복원
            self.current_image = self.original_image.copy()
            self.is_blurred = False
        else:
            # 현재 상태에서 블러 적용
            blurred_image = cv2.GaussianBlur(self.current_image, (kernel_size, kernel_size), 0)
            self.current_image = blurred_image  # 블러 적용된 이미지를 저장
            self.is_blurred = True

        # Tkinter 이미지 변환 및 표시
        img_rgb = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(img_pil)
        self.display_image(img_tk)

    def get_input(self, entry):
        try:
            return int(entry.get())
        except ValueError:
            messagebox.showerror("오류", "유효하지 않은 입력입니다")
            return None


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageVideoProcessor(root)
    root.mainloop()
