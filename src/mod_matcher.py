from typing import List, Dict


class ModMatcher:
    def __init__(self, list_of_mods: List[str]):
        self.list_of_mods = self._parse_mods(list_of_mods)
    

    def __call__(self, text: List[str]) -> List[str]:
        result = []
        for s in text:
            result.extend(self.match_mod(s))
        return result

    def _parse_mods(self, result: List[str]):
        curated = [
            {
                "text": r.lower(),
                "set": set(r.lower()),
                "len": len(r),
                "bigrams": self.get_bigrams(r),
            }
            for r in result
        ]
        return curated
        
    def _match_mod(self, text: str):
        text_lower = text.lower()
        text_set = set(text_lower)
        matches = []
        for mod in self.list_of_mods:
            if abs(len(text_set & mod["set"]) - mod["len"]) < max(2, int(mod["len"] * 0.3)):
                matches.append(mod["text"])
        return matches
    
    def get_bigrams(self, string: str) -> set:
        """Converts a string into a set of overlapping 2-character substrings."""
        clean_str = "".join(e for e in string.lower() if e.isalpha() or e == "%")
        return {clean_str[i:i+2] for i in range(len(clean_str) - 1)}

    def match_mod(self, text: str, threshold: float = 0.6): 
        """Calculates the similarity between two strings using set operations."""
        matches = []
        bigrams = self.get_bigrams(text)
        intersection_size = 0
        for mod in self.list_of_mods:
            intersection_size = len(bigrams.intersection(mod["bigrams"]))
            if (2.0 * intersection_size) / (len(bigrams) + len(mod["bigrams"])) > threshold:
                matches.append(mod["text"])
        return matches


