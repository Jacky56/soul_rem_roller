import os
import sys
cuda_path = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.2\bin\x64"
cudnn_path = r"C:\Program Files\NVIDIA\CUDNN\v9.26\bin\13.4\x64"

if sys.platform == "win32":
    if os.path.exists(cuda_path):
        os.add_dll_directory(cuda_path)
    if os.path.exists(cudnn_path):
        os.add_dll_directory(cudnn_path)
    
from rapidocr_onnxruntime import RapidOCR
from typing import List
import dataclasses



@dataclasses.dataclass
class EchoGroup:
    bbox: List[List[int]]

@dataclasses.dataclass
class Grouping:
    equipped: List[EchoGroup]
    unequipped: List[EchoGroup]


class OCRHandler:
    def __init__(self):
        self.reader = RapidOCR(
            det_use_cuda=True,
            cls_use_cuda=True,
            rec_use_cuda=True,
        )

    def __call__(self, image, score_threshold=0.75):
        """
        method that extracts landmarks, finds echo groups, and identifies equipped items from the given image.
        """
        result = self.read_frame(image, score_threshold=score_threshold)
        echo_groups = self.get_echo_landmarks(result)
        grouping = self.find_equipped_landmarks(result, echo_groups)
        equipped_echos = self.get_echoes(result, grouping.equipped)
        unequipped_echos = self.get_echoes(result, grouping.unequipped)
        return equipped_echos, unequipped_echos

    def read_frame(self, image, score_threshold=0.8):
        result = self.reader(image)[0]
        
        return [
            {
                "bbox": bbox, # [top-left [x, y], top-right [x, y], bottom-right [x, y], bottom-left [x, y]]
                "text": text.lower(),
                "set": set(text.lower()),
                "length": len(text),
                "score": confidence
            }
        for bbox, text, confidence in result if confidence >= score_threshold]
        

    def get_echo_landmarks(self, result: List[dict]) -> List[EchoGroup]:
        """used to find all group of echos on the screen.
        e.g if there are 10 items, you will get 10 EchoGroup instances, each representing the bounding box of an echo group.
        """
        echo_landmarks = []
        upgrade_slot_landmarks = []
        echo = set("echo")
        upgrade = set("upgrade")
        
        for d in result:
            bbox, text, score, text_set, text_length = d["bbox"], d["text"], d["score"], d["set"], d["length"]
            if echo.issubset(text_set) and 3 <= text_length and "ech" in text:
                echo_landmarks.append(d)
            if upgrade.issubset(text_set) and 6 <= text_length and "upgrad" in text:
                upgrade_slot_landmarks.append(d)

        groups: List[EchoGroup] = []
        for e in echo_landmarks:
            avg_x = (e["bbox"][0][0] + e["bbox"][-1][0]) / 2
            closest_u = None
            for u in upgrade_slot_landmarks:
                avg_u_x = (u["bbox"][0][0] + u["bbox"][-1][0]) / 2
                if closest_u is None or abs(avg_x - avg_u_x) < abs(avg_x - (closest_u["bbox"][0][0] + closest_u["bbox"][-1][0]) / 2):
                    closest_u = u
            if closest_u:
                landmark = [
                    [min(e["bbox"][3][0], closest_u["bbox"][3][0]), min(e["bbox"][3][1], closest_u["bbox"][3][1]) + 5],
                    [max(e["bbox"][2][0], closest_u["bbox"][2][0]), min(e["bbox"][2][1], closest_u["bbox"][2][1]) + 5],
                    [max(e["bbox"][1][0], closest_u["bbox"][1][0]), max(e["bbox"][1][1], closest_u["bbox"][1][1]) -10],
                    [min(e["bbox"][1][0], closest_u["bbox"][0][0]), max(e["bbox"][1][1], closest_u["bbox"][0][1]) -10]
                ]
                groups.append(
                    EchoGroup(bbox=landmark),
                )
        return groups

    
    
    def find_equipped_landmarks(self, result: List[dict], landmarks: List[EchoGroup])-> Grouping:
        """
        Identify and group equipped landmarks relative to existing echo groups.
        Splits between unequipped and equipped groups based on proximity to echo groups.
        """
        
        groups = landmarks
        equipped_landmarks: List[dict] = []
        equipped = set("(equip)")
        for r in result:
            bbox, text, score, text_set, text_length = r["bbox"], r["text"], r["score"], r["set"], r["length"]
            if equipped.issubset(text_set) and 4 <= text_length:
                equipped_landmarks.append(r)
                
        d: dict[str, List[EchoGroup]] = {}
        
        paired = set()
        for g in groups:
            avg_x = (g.bbox[0][0] + g.bbox[-1][0]) / 2
            avg_y = (g.bbox[0][1] + g.bbox[-1][1]) / 2
            closest_group = None
            for i, eq in enumerate(equipped_landmarks):
                bbox = eq["bbox"]
                avg_eq_x = (bbox[0][0] + bbox[-1][0]) / 2
                avg_eq_y = (bbox[0][1] + bbox[-1][1]) / 2
                if ((closest_group is None or abs(avg_x - avg_eq_x) < abs(avg_x - (closest_group.bbox[0][0] + closest_group.bbox[-1][0]) / 2))
                    and abs(avg_x - avg_eq_x) <= 50
                    and (avg_eq_y - 25) <= avg_y
                    and i not in paired
                ):
                    closest_group = g
                    paired.add(i)
            if closest_group:
                if "equipped" not in d:
                    d["equipped"] = []
                d["equipped"].append(closest_group)
            else:
                if "unequipped" not in d:
                    d["unequipped"] = []
                d["unequipped"].append(g)

        return Grouping(
            equipped=d.get("equipped", []),
            unequipped=d.get("unequipped", [])
        )
        
        
    
    def get_echoes(self, result: List[dict], landmarks: List[EchoGroup]) -> List[List[str]]:
        """
        Identify and group echoes relative to existing landmarks.
        Returns a list of echo groups, each corresponding to a landmark.
        """

        echo_groups = []
        for landmark in landmarks:
            # any bbox roughly in the match landmark
            echos = []
            for d in result:
                bbox = d["bbox"]
                avg_x = (bbox[0][0] + bbox[-1][0]) / 2
                landmark_avg_x = (landmark.bbox[0][0] + landmark.bbox[-1][0]) / 2
                if abs(avg_x - landmark_avg_x) <= 50 and (landmark.bbox[0][1] - 5) <= bbox[0][1] <= (landmark.bbox[-1][1] + 5):
                    echos.append(d["text"])
            if echos:
                echo_groups.append(echos)
        return echo_groups
