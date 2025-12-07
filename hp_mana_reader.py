"""
Tibia Pixel Bot - HP/Mana Reader
Simple and working version.
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
        self.status_bar_location = None
        self.last_hp = None
        self.last_mana = None
        self._load_template()
    
    def _load_template(self):
        if self.template_path.exists():
            self.template = cv2.imread(str(self.template_path))
            if self.template is not None:
                print(f"✅ Template: {self.template.shape[1]}x{self.template.shape[0]}")
    
    def find_status_bar(self, screenshot_np: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Find status bar using template matching."""
        if self.template is None:
            return None
        
        best_match = None
        best_val = 0
        
        for scale in [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]:
            w = int(self.template.shape[1] * scale)
            h = int(self.template.shape[0] * scale)
            
            if w < 50 or h < 15 or w > screenshot_np.shape[1] or h > screenshot_np.shape[0]:
                continue
            
            resized = cv2.resize(self.template, (w, h))
            result = cv2.matchTemplate(screenshot_np, resized, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_val:
                best_val = max_val
                best_match = (max_loc[0], max_loc[1], w, h)
        
        if best_match and best_val > 0.6:
            print(f"📍 Match: {best_val:.1%} at ({best_match[0]}, {best_match[1]})")
            return best_match
        
        return None
    
    def read_numbers(self, image: Image.Image, region: Tuple[int, int, int, int]) -> Tuple[Optional[int], Optional[int]]:
        """Read HP and Mana numbers from the status bar region."""
        x, y, w, h = region
        cropped = image.crop((x, y, x + w, y + h))
        
        # Template is clean HP/Mana bars:
        # Top half = HP bar + number
        # Bottom half = Mana bar + number
        
        half_h = h // 2
        
        # HP: 4-digit number, start at 75%
        hp_img = cropped.crop((int(w * 0.75), 0, w, half_h))
        
        # Mana: 3-digit number, start at 68%
        mana_img = cropped.crop((int(w * 0.68), half_h, w, h))
        
        hp = self._read_number(hp_img)
        mana = self._read_number(mana_img)
        
        return hp, mana
    
    def _read_number(self, img: Image.Image) -> Optional[int]:
        """OCR a small region to get a number."""
        arr = np.array(img.convert('L'))  # Grayscale
        
        # Tibia numbers are bright (white/light) on dark background
        # Try threshold at 150 (bright pixels become white)
        _, binary = cv2.threshold(arr, 150, 255, cv2.THRESH_BINARY)
        
        # Scale up 4x for better OCR
        scaled = cv2.resize(binary, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
        
        # Add white padding
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
        """Main method: read HP and Mana from screenshot."""
        import time
        
        # Convert PIL to OpenCV BGR
        screenshot_np = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Find status bar if not cached
        if self.status_bar_location is None:
            self.status_bar_location = self.find_status_bar(screenshot_np)
        
        if self.status_bar_location is None:
            return StatusReading(hp=None, mana=None)
        
        # Read numbers
        hp, mana = self.read_numbers(image, self.status_bar_location)
        
        # Cache valid readings
        if hp: self.last_hp = hp
        if mana: self.last_mana = mana
        
        return StatusReading(
            hp=hp or self.last_hp,
            mana=mana or self.last_mana,
            timestamp=time.time()
        )
    
    def reset(self):
        self.status_bar_location = None


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
