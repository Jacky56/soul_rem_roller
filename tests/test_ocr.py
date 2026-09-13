# create test case for ocr handler
import unittest
from src.mod_matcher import ModMatcher
from src.ocr import OCRHandler
import cv2
import numpy as np
    

class TestOCRHandler(unittest.TestCase):
    def setUp(self):
        self.ocr_handler = OCRHandler()
        self.sample_frame = "tests/sample_frame.png"
        # self.sample_frame = "tests/image.png"


    def test_ocr_handler_initialization(self):
        self.assertIsInstance(self.ocr_handler, OCRHandler)
        
    def test_ocr_handler_callable(self):
        equipped_echos, unequipped_echos, _ = self.ocr_handler(self.sample_frame)
        
        equipped_echos_mods = ModMatcher([
            "jump",
            "skill range",
            "exp",
            "skill exp",
            "weapon smithing minigame rolls"
        ])
        for echos in equipped_echos:
            matched_equipped_echos = equipped_echos_mods(echos)
            assert len(equipped_echos_mods.list_of_mods) == len(matched_equipped_echos)
            assert len(echos) == len(equipped_echos_mods.list_of_mods)
            
        unequipped_echos_mods = ModMatcher([
            "weapon smithing level",
            "mining level",
            "artisan level",
            "light radius"
        ])
        for echos in unequipped_echos:
            matched_unequipped_echos = unequipped_echos_mods(echos)
            assert len(unequipped_echos_mods.list_of_mods) == len(matched_unequipped_echos)
            assert len(echos) == len(unequipped_echos_mods.list_of_mods)
            
    def test_generate_landmarks(self):
        frame = cv2.imread(self.sample_frame)
        
        frame_data = self.ocr_handler.read_frame(self.sample_frame)
        echo_landmarks = self.ocr_handler.get_echo_landmarks(frame_data)
        equipped_landmarks = self.ocr_handler.find_equipped_landmarks(frame_data, echo_landmarks)
        
        for e in equipped_landmarks.equipped:
            pts = np.array(e.bbox, dtype=np.int32)
            pts = pts.reshape((-1, 1, 2))     
            cv2.polylines(frame, [pts], isClosed=True, color=(0, 0, 255), thickness=2)

        for u in equipped_landmarks.unequipped:
            pts = np.array(u.bbox, dtype=np.int32)
            pts = pts.reshape((-1, 1, 2))     
            cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 0), thickness=2)

        cv2.imwrite("tests/sample_frame_with_landmarks.png", frame)

if __name__ == "__main__":
    unittest.main()
