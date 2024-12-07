import tkinter as tk
from tkinter.font import Font
import subprocess

# 각 프로그램의 이름과 경로를 설정
programs = {
    "TiltShift": "TiltShift.py",
    "CreateGIF": "CreateGIF.py",
    "ImageBackgroundEdge": "ImageBackgroundEdge.py",
    "Image_conversion": "Image_conversion.py",
    "Timelapse": "Timelapse.py",
}


# 프로그램 실행 함수
def run_program(program_name):
    program_path = programs.get(program_name)
    if program_path:
        try:
            subprocess.Popen(["python", program_path], shell=True)
        except Exception as e:
            print(f"Error executing {program_name}: {e}")
    else:
        print(f"Program {program_name} not found!")


# Tkinter GUI 설정
root = tk.Tk()
root.title("Tiltypy Studio")
root.geometry("400x500")  # 창 크기 설정
root.configure(bg="#f0f0f5")  # 배경색 설정

# 커스텀 폰트 설정
header_font = Font(family="Helvetica", size=16, weight="bold")
button_font = Font(family="Helvetica", size=12)

# 헤더 추가
header = tk.Label(root, text="Tiltypy Studio", font=header_font, bg="#f0f0f5", fg="#333")
header.pack(pady=20)

# 버튼 스타일링 및 레이아웃
button_frame = tk.Frame(root, bg="#f0f0f5")
button_frame.pack(pady=20)

for i, (program_name, _) in enumerate(programs.items()):
    button = tk.Button(
        button_frame,
        text=program_name,
        font=button_font,
        bg="#f0f0f5",
        command=lambda name=program_name: run_program(name),
    )
    button.grid(row=i, column=0, padx=20, pady=10, sticky="ew")

# 팀원 정보 라벨
Member = tk.Label(
    root,
    text=(
        "팀장: 20203019 윤한울\n"
        "팀원: 20203060 이진재\n"
        "팀원: 20203041 박정현\n"
        "팀원: 20210018 신유진\n"
        "팀원: 20203075 조수호"
    ),
    font=("Helvetica", 10),
    bg="#f0f0f5",
    fg="#888",
)
Member.pack(side="bottom", pady=5)

# 팀 정보 라벨
Team = tk.Label(root, text="디지털영상처리및실습 5팀", font=("Helvetica", 10, "bold"), bg="#f0f0f5", fg="#888")
Team.pack(side="bottom", pady=10)

# GUI 실행
root.mainloop()
