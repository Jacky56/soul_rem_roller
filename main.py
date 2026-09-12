from src.screen_handler import ScreenHandler
from src.ocr import OCRHandler
from src.mod_matcher import ModMatcher
from datetime import datetime
import time
import msvcrt
import logging
import yaml

with open("mod_list.yaml", "r") as f:
    mod_list = yaml.safe_load(f)
    
logging.basicConfig(level=logging.DEBUG)



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
                
        equipped_echos, unequipped_echos = ocr(frame)
        
        # if not equipped_echos and not unequipped_echos:
        #     continue
        
        flag = False
        for echo_pool in unequipped_echos:
            matched_mods_unequipped = mod_matcher(echo_pool)
            if matched_mods_unequipped:
                logging.info("Matched Mods Unequipped: %s", matched_mods_unequipped)
                flag = True
                handler.window.close()
                exit(0)

        if not flag and unequipped_echos:
            handler.do_click()

    end_time = datetime.now()
    logging.info("End time: %s", end_time)
    