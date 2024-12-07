import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import os
from PIL import Image, ImageTk


class Timelapse:
    def __init__(self, root):
        self.root = root
        self.root.title("Tiltypy Studio - Timelapse Converter")
        self.root.geometry("900x770")  # 창 크기 설정
        self.root.configure(bg="#f0f0f5")  # 배경 색상 설정
        self.save_button = None
        self.process_button = None
        self.fps_entry = None
        self.fps_label = None
        self.select_button = None
        self.canvas = None
        self.description_label = None
        self.header_label = None
        self.file_path = None
        self.output_dir = None
        self.video_capture = None
        self.transformed_video_path = None
        self.is_preview_active = False  # 미리보기 활성화 상태

        # 캔버스 크기 설정
        self.canvas_width = 800
        self.canvas_height = 450

        # GUI 구성
        self.setup_gui()

    def setup_gui(self):
        # 헤더 라벨
        header_font = ("Helvetica", 18, "bold")
        self.header_label = tk.Label(self.root, text="Tiltypy Studio", font=header_font, bg="#f0f0f5", fg="#333")
        self.header_label.pack(pady=20)

        # 설명 라벨
        description_font = ("Helvetica", 12)
        self.description_label = tk.Label(
            self.root, text="Convert videos into Timelapse videos effortlessly!", font=description_font,
            bg="#f0f0f5", fg="#555")
        self.description_label.pack(pady=10)

        # 캔버스: 비디오 미리보기
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="gray",
                                relief="ridge", bd=2)
        self.canvas.pack(pady=20)

        # 버튼 프레임
        button_frame = tk.Frame(self.root, bg="#f0f0f5")
        button_frame.pack(pady=20)

        # 동영상 선택 버튼
        button_font = ("Helvetica", 12)
        self.select_button = tk.Button(button_frame, text="Select Video", font=button_font,
                                       command=self.select_video, height=2, width=20)
        self.select_button.grid(row=0, column=0, padx=10)

        # FPS 입력 필드
        self.fps_label = tk.Label(button_frame, text="Enter FPS:", font=button_font, bg="#f0f0f5", fg="#555")
        self.fps_label.grid(row=0, column=1, padx=10)

        self.fps_entry = tk.Entry(button_frame, width=10)
        self.fps_entry.grid(row=0, column=2, padx=10)

        # 변환 버튼
        self.process_button = tk.Button(button_frame, text="Process Video", font=button_font,
                                        command=self.process_video, height=2, width=20)
        self.process_button.grid(row=0, column=3, padx=10)

        # 저장 버튼
        self.save_button = tk.Button(button_frame, text="Save Video", font=button_font,
                                     command=self.save_video, height=2, width=20, state=tk.DISABLED)
        self.save_button.grid(row=1, column=0, columnspan=4, pady=10)

    def select_video(self):
        # 사용자로부터 동영상 파일 선택
        self.file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov")])
        if not self.file_path:
            messagebox.showerror("Error", "No video file selected!")
        else:
            self.is_preview_active = True  # 미리보기 활성화
            self.display_video_preview(self.file_path)

    def display_video_preview(self, video_path):
        """
        비디오 파일을 캔버스에 미리보기로 표시하며 반복 재생
        """
        if self.video_capture is not None:
            self.video_capture.release()  # 기존 미리보기 중단

        self.video_capture = cv2.VideoCapture(video_path)
        if not self.video_capture.isOpened():
            messagebox.showerror("Error", "Cannot open video file!")
            return

        def show_frame():
            if not self.is_preview_active:
                return  # 미리보기 중단 시 종료

            ret, frame = self.video_capture.read()
            if ret:
                frame = self.resize_frame_to_canvas(frame)
                frame_image = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
                self.canvas.create_image(0, 0, anchor=tk.NW, image=frame_image)
                self.canvas.image = frame_image
                self.root.after(30, show_frame)
            else:
                self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 영상 반복 재생
                show_frame()

        show_frame()

    def resize_frame_to_canvas(self, frame):
        # 프레임을 캔버스 크기에 맞게 조정
        frame_height, frame_width = frame.shape[:2]
        scale = min(self.canvas_width / frame_width, self.canvas_height / frame_height)
        new_width = int(frame_width * scale)
        new_height = int(frame_height * scale)
        return cv2.resize(frame, (new_width, new_height))

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

        # 변환된 비디오 저장
        self.transformed_video_path = os.path.splitext(self.file_path)[0] + "_processed.mp4"
        self.divide_and_save_frames(fps)
        self.is_preview_active = True  # 미리보기 활성화
        self.display_video_preview(self.transformed_video_path)
        self.save_button.config(state=tk.NORMAL)  # 저장 버튼 활성화

    def divide_and_save_frames(self, fps):
        """
        입력된 FPS로 동영상을 프레임으로 분리하고 저장.
        """
        vid = cv2.VideoCapture(self.file_path)
        original_fps = int(vid.get(cv2.CAP_PROP_FPS))

        frame_count = 0
        saved_frames = []

        while vid.isOpened():
            ret, frame = vid.read()
            if not ret:
                break

            # FPS에 따라 프레임 저장
            if frame_count % (original_fps // fps) == 0:
                saved_frames.append(frame)

            frame_count += 1

        vid.release()

        # 저장된 프레임으로 새로운 비디오 생성
        if saved_frames:
            height, width, _ = saved_frames[0].shape
            self.transformed_video_path = os.path.splitext(self.file_path)[0] + "_processed.mp4"
            self.create_video_from_frames(saved_frames, fps, width, height)
        else:
            messagebox.showerror("Error", "No frames processed!")

    def create_video_from_frames(self, frames, fps, width, height):
        """
        저장된 프레임을 변환된 FPS로 새로운 비디오로 생성.
        """
        # 변환된 비디오 경로
        output_path = self.transformed_video_path
        out = cv2.VideoWriter(output_path, cv2.VideoWriter.fourcc(*'mp4v'), fps, (width, height))

        for frame in frames:
            out.write(frame)

        out.release()

    def save_video(self):
        """
        변환된 비디오를 저장
        """
        if not self.transformed_video_path or not os.path.exists(self.transformed_video_path):
            messagebox.showerror("Error", "No processed video to save!")
            return

        if self.video_capture is not None:
            self.video_capture.release()  # 미리보기 중단

        self.is_preview_active = False  # 미리보기 중단 상태 설정

        # 원본 이름에 "_Timelapse" 추가
        original_name = os.path.basename(self.file_path)
        base_name, _ = os.path.splitext(original_name)
        default_name = f"{base_name}_Timelapse.mp4"

        save_path = filedialog.asksaveasfilename(defaultextension=".mp4",
                                                 filetypes=[("MP4 Files", "*.mp4")],
                                                 initialfile=default_name)
        if save_path:
            try:
                # 파일 복사 후 원본 삭제
                with open(self.transformed_video_path, "rb") as src, open(save_path, "wb") as dst:
                    dst.write(src.read())
                os.remove(self.transformed_video_path)  # 원본 삭제
                messagebox.showinfo("Success", f"Video saved at: {save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save video: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = Timelapse(root)
    root.mainloop()
