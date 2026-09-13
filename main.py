from src.screen_handler import ScreenHandler
from src.ocr import OCRHandler
from src.mod_matcher import ModMatcher
from datetime import datetime
import time
import msvcrt
import logging
import yaml
from pynput import keyboard

PAUSE = False

def on_press(key):
    global PAUSE
    if key in (keyboard.Key.pause, keyboard.Key.f12):
        PAUSE = not PAUSE
        print("Paused" if PAUSE else "Resumed")

listener = keyboard.Listener(on_press=on_press)
listener.start()

with open("mod_list.yaml", "r") as f:
    mod_list = yaml.safe_load(f)
    
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
    
)

if __name__ == "__main__":
    handler = ScreenHandler("Soul's Remnant", capture_time=0.02)
    ocr = OCRHandler()
    mod_matcher = ModMatcher(mod_list)  # Replace with actual mods
    start_time = datetime.now()
    logging.info("Camera started:\nPress 'q' to quit the stream.")
    logging.info("Start time: %s", start_time)
    
    for frame in handler.get_frame():
        if msvcrt.kbhit() and msvcrt.getch() in (b'q', b'Q', b'\x1b'):
            break
        if PAUSE:
            continue
        equipped_echos, unequipped_echos, ocr_result = ocr(frame)
        if not any(set("invent").issubset(d["set"]) for d in ocr_result):
            PAUSE = True
            print("Inventory not detected, pausing.")
        
        for echo_pool in unequipped_echos:
            matched_mods_unequipped = mod_matcher(echo_pool)
            if matched_mods_unequipped:
                logging.info("Matched Mods Unequipped: %s", matched_mods_unequipped)
                
                # handler.window.close()
                PAUSE = True
                print("Paused")

        if not PAUSE and unequipped_echos:
            handler.do_click()
        logging.info("Unequipped echos: %s", unequipped_echos)

    end_time = datetime.now()
    logging.info("End time: %s", end_time)
    
