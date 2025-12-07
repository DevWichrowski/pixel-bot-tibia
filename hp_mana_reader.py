"""
Tibia Pixel Bot - HP/Mana Reader
Uses template matching with Stop button as anchor.
Below Stop button: first line = HP, second line = Mana.
"""

import re
import cv2
import numpy as np
from PIL import Image
from dataclasses import dataclass
from typing import Optional, Tuple
from pathlib import Path
import pytesseract


@dataclass
class StatusReading:
    hp: Optional[int]
    mana: Optional[int]
    timestamp: float = 0.0
    
    def __str__(self):
        hp_str = str(self.hp) if self.hp else "?"
        mana_str = str(self.mana) if self.mana else "?"
        return f"HP: {hp_str} | Mana: {mana_str}"


class HPManaReader:
    def __init__(self):
        self.template_path = Path(__file__).parent / "templates" / "status_bar_template.png"
        self.template = None
        self.region = None  # (x, y, w, h) of status panel
        self.last_hp = None
        self.last_mana = None
        self._load_template()
    
    def _load_template(self):
        if self.template_path.exists():
            self.template = cv2.imread(str(self.template_path))
            if self.template is not None:
                print(f"✅ Template: {self.template.shape[1]}x{self.template.shape[0]}")
    
    def find_status_panel(self, screenshot: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Find status panel using template matching."""
        if self.template is None:
            return None
        
        best_match = None
        best_val = 0
        
        # Try different scales
        for scale in [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]:
            w = int(self.template.shape[1] * scale)
            h = int(self.template.shape[0] * scale)
            
            if w < 50 or h < 20 or w > screenshot.shape[1] or h > screenshot.shape[0]:
                continue
            
            resized = cv2.resize(self.template, (w, h))
            result = cv2.matchTemplate(screenshot, resized, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_val:
                best_val = max_val
                best_match = (max_loc[0], max_loc[1], w, h)
        
        if best_match and best_val > 0.6:
            print(f"📍 Match: {best_val:.1%} at ({best_match[0]}, {best_match[1]})")
            return best_match
        
        return None
    
    def read_numbers(self, image: Image.Image, region: Tuple[int, int, int, int]) -> Tuple[Optional[int], Optional[int]]:
        """Read HP and Mana from the status panel region."""
        x, y, w, h = region
        cropped = image.crop((x, y, x + w, y + h))
        
        # Extract right side of panel where numbers are
        num_region = cropped.crop((int(w * 0.55), int(h * 0.30), w, h))
        
        arr = np.array(num_region.convert('L'))
        
        # Try multiple thresholds (start low for light text on dark bg)
        for thresh_val in [80, 100, 120, 140]:
            _, binary = cv2.threshold(arr, thresh_val, 255, cv2.THRESH_BINARY)
            result = self._ocr_numbers(binary)
            if result[0] is not None and result[1] is not None:
                return result
        
        # Try OTSU as fallback
        _, binary = cv2.threshold(arr, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return self._ocr_numbers(binary)
    
    def _ocr_numbers(self, binary: np.ndarray) -> Tuple[Optional[int], Optional[int]]:
        """OCR binary image and extract HP/Mana numbers."""
        scaled = cv2.resize(binary, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
        padded = cv2.copyMakeBorder(scaled, 15, 15, 15, 15, cv2.BORDER_CONSTANT, value=255)
        
        try:
            # PSM 11 works best for sparse text with numbers
            text = pytesseract.image_to_string(
                padded,
                config='--psm 11 -c tessedit_char_whitelist=0123456789'
            ).strip()
            
            numbers = re.findall(r'\d{2,5}', text)
            
            if len(numbers) >= 2:
                return int(numbers[0]), int(numbers[1])
            elif len(numbers) == 1:
                return int(numbers[0]), None
        except:
            pass
        
        return None, None
    
    def _read_number(self, img: Image.Image) -> Optional[int]:
        """OCR a region to extract a number."""
        arr = np.array(img.convert('L'))
        
        _, binary = cv2.threshold(arr, 150, 255, cv2.THRESH_BINARY)
        scaled = cv2.resize(binary, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
        padded = cv2.copyMakeBorder(scaled, 15, 15, 15, 15, cv2.BORDER_CONSTANT, value=255)
        
        try:
            text = pytesseract.image_to_string(
                padded,
                config='--psm 7 -c tessedit_char_whitelist=0123456789'
            ).strip()
            
            if text and text.isdigit() and 2 <= len(text) <= 5:
                return int(text)
        except:
            pass
        
        return None
    
    def read_status(self, image: Image.Image) -> StatusReading:
        """Read HP and Mana from screenshot."""
        import time
        
        screenshot_np = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        if self.region is None:
            self.region = self.find_status_panel(screenshot_np)
        
        if self.region is None:
            return StatusReading(hp=self.last_hp, mana=self.last_mana)
        
        hp, mana = self.read_numbers(image, self.region)
        
        if hp: self.last_hp = hp
        if mana: self.last_mana = mana
        
        return StatusReading(
            hp=hp or self.last_hp,
            mana=mana or self.last_mana,
            timestamp=time.time()
        )
    
    def reset(self):
        self.region = None


if __name__ == "__main__":
    from window_finder import find_tibia_window
    from screen_capture import ScreenCapture
    
    window = find_tibia_window()
    if window:
        print(f"Window: {window['name']}")
        capture = ScreenCapture()
        img = capture.capture_window(window)
        
        if img:
            reader = HPManaReader()
            status = reader.read_status(img)
            print(f"\n{status}")
        
        capture.close()
    else:
        print("Tibia not found!")
