import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import os


class VideoFrameProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Frame Processor")
        self.root.geometry("300x300")  # 창 크기 설정
        self.file_path = None
        self.output_dir = None

        # GUI 구성
        self.setup_gui()

    def setup_gui(self):
        # 동영상 선택 버튼
        self.select_button = tk.Button(self.root, text="Select Video", command=self.select_video)
        self.select_button.pack(pady=10)

        # FPS 입력 필드
        self.fps_label = tk.Label(self.root, text="Enter FPS:")
        self.fps_label.pack()

        self.fps_entry = tk.Entry(self.root)
        self.fps_entry.pack(pady=5)

        # 변환 및 저장 버튼
        self.process_button = tk.Button(self.root, text="Process and Save", command=self.process_video)
        self.process_button.pack(pady=10)

    def select_video(self):
        # 사용자로부터 동영상 파일 선택
        self.file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov")])
        if not self.file_path:
            messagebox.showerror("Error", "No video file selected!")
        else:
            messagebox.showinfo("Selected File", f"Selected video: {self.file_path}")

    def process_video(self):
        if not self.file_path:
            messagebox.showerror("Error", "No video file selected!")
            return

        # FPS 입력 확인
        fps_input = self.fps_entry.get()
        if not fps_input.isdigit() or int(fps_input) <= 0:
            messagebox.showerror("Error", "Invalid FPS value! Please enter a positive integer.")
            return

        fps = int(fps_input)

        # 프레임 분리 및 저장
        self.divide_and_save_frames(fps)

    def divide_and_save_frames(self, fps):
        # 동영상 열기
        vid = cv2.VideoCapture(self.file_path)
        original_fps = int(vid.get(cv2.CAP_PROP_FPS))

        # 출력 디렉터리 생성
        self.output_dir = os.path.splitext(self.file_path)[0]
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        frame_count = 0
        saved_count = 0

        while vid.isOpened():
            ret, frame = vid.read()
            if not ret:
                break

            # FPS 기준으로 프레임 저장
            if frame_count % (original_fps // fps) == 0:
                frame_path = os.path.join(self.output_dir, f"frame{saved_count:04d}.jpg")
                cv2.imwrite(frame_path, frame)
                saved_count += 1

            frame_count += 1

        vid.release()
        messagebox.showinfo("Success", f"Frames saved to: {self.output_dir}")

        # 저장된 이미지로 동영상 생성
        self.create_video_from_frames(fps)

    def create_video_from_frames(self, fps):
        # 저장된 이미지 파일 정렬
        frame_files = sorted(
            [os.path.join(self.output_dir, f) for f in os.listdir(self.output_dir) if f.endswith(".jpg")]
        )

        if not frame_files:
            messagebox.showerror("Error", "No frames found to create video.")
            return

        # 첫 번째 프레임으로 영상 크기 결정
        first_frame = cv2.imread(frame_files[0])
        height, width, layers = first_frame.shape
        size = (width, height)

        # 출력 영상 파일 경로
        output_video_path = os.path.join(self.output_dir, "output_video.mp4")

        # 동영상 작성
        out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'avc1'), fps, size)  # H.264 코덱 사용

        for frame_file in frame_files:
            frame = cv2.imread(frame_file)
            resized_frame = cv2.resize(frame, (width, height))  # 해상도 유지
            out.write(resized_frame)

        out.release()
        messagebox.showinfo("Success", f"Video saved as: {output_video_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoFrameProcessor(root)
    root.mainloop()

