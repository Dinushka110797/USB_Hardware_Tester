import os
import psutil
import cv2
import keyboard
import pygame
import time
from datetime import datetime
import PySimpleGUI as sg

# Initialize pygame safely
pygame.init()
pygame.display.quit()  # Proper initialization for later use

def test_hard_drive():
    results = {}
    partitions = psutil.disk_partitions()
    for i, partition in enumerate(partitions):
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            results[f"Disk {i}"] = f"{partition.device} {usage.percent}% used ({usage.free/(1024**3):.2f} GB free)"
        except Exception as e:
            results[f"Disk {i} Error"] = str(e)
    return results

def test_ram():
    try:
        vm = psutil.virtual_memory()
        return {
            "Total RAM": f"{vm.total/(1024**3):.2f} GB",
            "Available": f"{vm.available/(1024**3):.2f} GB",
            "Used Percent": f"{vm.percent}%"
        }
    except Exception as e:
        return {"RAM Test Error": str(e)}

def test_keyboard():
    try:
        return {"Keyboard Test": "Press keys in the test window"}
    except Exception as e:
        return {"Keyboard Test Error": str(e)}

def test_camera():
    try:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                return {"Camera Test": "Working - Camera detected"}
        return {"Camera Test": "Camera not functioning properly"}
    except Exception as e:
        return {"Camera Test Error": str(e)}

def test_display():
    try:
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 255, 255) # White
        ]
        for color in colors:
            screen.fill(color)
            pygame.display.flip()
            time.sleep(1)
        pygame.quit()
        return {"Display Test": "Color test completed successfully"}
    except Exception as e:
        return {"Display Test Error": str(e)}

def run_tests(values, window):
    tests = []
    if values["-DISK-"]: tests.append(("Hard Drive", test_hard_drive))
    if values["-RAM-"]: tests.append(("RAM", test_ram))
    if values["-KEYBOARD-"]: tests.append(("Keyboard", test_keyboard))
    if values["-CAMERA-"]: tests.append(("Camera", test_camera))
    if values["-DISPLAY-"]: tests.append(("Display", test_display))

    report = {"Test Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    for name, test_func in tests:
        window["-STATUS-"].update(f"Running {name} test...")
        window.refresh()
        try:
            result = test_func()
            report.update(result)
            print(f"=== {name} ===")
            for k, v in result.items():
                print(f"{k}: {v}")
            print()
        except Exception as e:
            report[f"{name} Error"] = str(e)
            print(f"{name} ERROR: {e}")
    
    # Save report
    if not os.path.exists("reports"):
        os.makedirs("reports")
    report_file = f"reports/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, "w") as f:
        for k, v in report.items():
            f.write(f"{k}: {v}\n")
    
    window["-STATUS-"].update(f"Tests completed! Report saved to {report_file}")

def main():
    # Create layout without theme (to avoid compatibility issues)
    layout = [
        [sg.Text(" D computers USB Hardware Tester", font=("Arial", 20))],
        [sg.Text("Select tests to run:")],
        [sg.Checkbox("Hard Drive", default=True, key="-DISK-")],
        [sg.Checkbox("RAM", default=True, key="-RAM-")],
        [sg.Checkbox("Keyboard", default=True, key="-KEYBOARD-")],
        [sg.Checkbox("Camera", default=True, key="-CAMERA-")],
        [sg.Checkbox("Display", default=True, key="-DISPLAY-")],
        [sg.Button("Run Tests"), sg.Button("Exit")],
        [sg.Output(size=(80, 15), key="-OUTPUT-")],
        [sg.Text("", key="-STATUS-", size=(70, 1))]
    ]

    window = sg.Window("Hardware Tester", layout, finalize=True)

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit"):
            break
        if event == "Run Tests":
            window["-OUTPUT-"].update("")
            run_tests(values, window)
    
    window.close()

if __name__ == "__main__":
    main()