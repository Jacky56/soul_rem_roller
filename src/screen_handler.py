from email.mime import text
import msvcrt
import random
import time
import pygetwindow as gw
from pygetwindow import Win32Window
import dxcam
import logging
import cv2
import pyautogui

class ScreenHandler:
    def __init__(self, title: str, fps: int = 60, capture_time: float = 0.1):
        self.title = title
        self.window = self._find_window()
        self.camera = dxcam.create()
        
        self.window_left = self.window.left
        self.window_top = self.window.top
        self.window_right = self.window.right
        self.window_bottom = self.window.bottom
        self.window_width = self.window_right - self.window_left
        self.window_height = self.window_bottom - self.window_top
        
        self.max_width = self.camera.width
        self.max_height = self.camera.height
        self.fps = fps
        self.capture_time = capture_time
        
        self._click_pos = []

    def _find_window(self) -> Win32Window:
        windows = gw.getWindowsWithTitle(self.title)
        if not windows:
            raise RuntimeError("EXE window not found")
        return windows[0]

    def start_camera(self):
        self.camera.stop()
        try:
            self.camera.start(
                target_fps=self.fps,
                region=(
                    self.window_left,
                    self.window_top,
                    self.window_right,
                    self.window_bottom
                ),
            )
        except Exception as e:
            logging.error(f"Failed to start camera: {e}")
            logging.error(f"Window region: {self.window_left}, {self.window_top}, {self.window_right}, {self.window_bottom}")
            self.camera.start(
                target_fps=self.fps,
                region=(
                    max(0, self.window_left),
                    max(0, self.window_top),
                    min(self.max_width, self.window_right),
                    min(self.max_height, self.window_bottom)
                ),
            )
        
    def readjust_window(self):
        if (self.window.left != self.window_left or
            self.window.top != self.window_top or
            self.window.right != self.window_right or
        self.window.bottom != self.window_bottom
        ) and not self.window.isMinimized:
            self.window_left = self.window.left
            self.window_top = self.window.top
            self.window_right = self.window.right
            self.window_bottom = self.window.bottom
            self.start_camera()

    def get_frame(self):
        self.window.activate()
        time.sleep(0.5)
        self.readjust_window()
        self.start_camera()
        while True:
            if msvcrt.kbhit() and msvcrt.getch() == b'q':
                break
            time.sleep(self.capture_time)
            if self.window.isMinimized:
                continue
            if not self.window.isActive:
                continue
            self.readjust_window()
            frame = self.camera.get_latest_frame_view()
            if frame is None:
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            yield gray

    def do_click(self, x: int=None, y: int=None, random_offset: bool = True):
        cx, cy = pyautogui.position()
        y = cy if y is None else y
        x = cx if x is None else x
        
        var_x = int(self.window_width * 0.002)
        var_y = int(self.window_height * 0.002)
        r_x = random.randint(-var_x, var_x)
        r_y = random.randint(-var_y, var_y)
        self._click_pos.append((r_x, r_y))
        if len(self._click_pos) > 5:
            self._click_pos = self._click_pos[1:]
            
        mean_var_x = round(sum(pos[0] for pos in self._click_pos) / len(self._click_pos))
        mean_var_y = round(sum(pos[1] for pos in self._click_pos) / len(self._click_pos))
        if random_offset:
            x += r_x - mean_var_x
            y += r_y - mean_var_y
        pyautogui.moveTo(x, y, duration=0.03)
        
        pyautogui.click()
        time.sleep(0.05)