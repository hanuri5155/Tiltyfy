import tkinter as tk
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
    # subprocess를 통해 프로그램 실행
    program_path = programs.get(program_name)
    if program_path:
        try:
            # Python 실행 경로를 포함하여 subprocess 실행
            subprocess.Popen(["python", program_path], shell=True)
        except Exception as e:
            print(f"Error executing {program_name}: {e}")
    else:
        print(f"Program {program_name} not found!")

# Tkinter GUI 설정
root = tk.Tk()
root.title("Main Page")
root.geometry("300x300")  # 창 크기 설정

# 버튼 생성
for program_name in programs.keys():
    button = tk.Button(root, text=program_name, command=lambda name=program_name: run_program(name))
    button.pack(pady=10)

# GUI 실행
root.mainloop()