"""
Windify Bot - HP/Mana Reader
Reads HP and Mana values from user-defined screen regions.
Format: "current/max" (e.g., "1301/1301")
"""

import re
import cv2
import numpy as np
from PIL import Image
from dataclasses import dataclass
from typing import Optional, Tuple
import pytesseract
from config import DEBUG_MODE


@dataclass
class StatusReading:
    """Current HP and Mana status."""
    hp_current: Optional[int] = None
    hp_max: Optional[int] = None
    mana_current: Optional[int] = None
    mana_max: Optional[int] = None
    
    @property
    def hp(self) -> Optional[int]:
        """Alias for hp_current for backward compatibility."""
        return self.hp_current
    
    @property
    def mana(self) -> Optional[int]:
        """Alias for mana_current for backward compatibility."""
        return self.mana_current
    
    def __str__(self):
        hp_str = f"{self.hp_current}/{self.hp_max}" if self.hp_current else "?"
        mana_str = f"{self.mana_current}/{self.mana_max}" if self.mana_current else "?"
        return f"HP: {hp_str} | Mana: {mana_str}"


class HPManaReader:
    """
    Reads HP and Mana from user-defined screen regions.
    Uses OCR to parse "current/max" format (e.g., "1301/1301").
    """
    
    def __init__(self):
        # User-defined regions (x, y, width, height)
        self.hp_region: Optional[Tuple[int, int, int, int]] = None
        self.mana_region: Optional[Tuple[int, int, int, int]] = None
        
        # Cache last valid readings
        self.last_hp_current: Optional[int] = None
        self.last_hp_max: Optional[int] = None
        self.last_mana_current: Optional[int] = None
        self.last_mana_max: Optional[int] = None
        
        # Retina display scale factor
        self._scale = self._detect_scale()
    
    def _detect_scale(self) -> float:
        """Detect Retina display scaling."""
        try:
            import Quartz
            main = Quartz.CGMainDisplayID()
            mode = Quartz.CGDisplayCopyDisplayMode(main)
            if mode:
                logical = Quartz.CGDisplayModeGetWidth(mode)
                pixel = Quartz.CGDisplayModeGetPixelWidth(mode)
                if logical > 0:
                    return pixel / logical
        except:
            pass
        return 1.0
    
    def set_regions(
        self, 
        hp_region: Optional[Tuple[int, int, int, int]] = None,
        mana_region: Optional[Tuple[int, int, int, int]] = None
    ) -> None:
        """Set the screen regions for HP and Mana reading."""
        if hp_region:
            self.hp_region = hp_region
            print(f"📍 HP region set: {hp_region}")
        if mana_region:
            self.mana_region = mana_region
            print(f"📍 Mana region set: {mana_region}")
    
    def is_configured(self) -> bool:
        """Check if both regions are configured."""
        return self.hp_region is not None and self.mana_region is not None
    
    def _scale_region(self, region: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        """Scale region coordinates for Retina displays."""
        x, y, w, h = region
        return (
            int(x * self._scale),
            int(y * self._scale),
            int(w * self._scale),
            int(h * self._scale)
        )
    
    def _crop_region(self, image: Image.Image, region: Tuple[int, int, int, int]) -> Image.Image:
        """Crop image to specified region."""
        x, y, w, h = region
        return image.crop((x, y, x + w, y + h))
    
    def _parse_current_max(self, text: str) -> Optional[Tuple[int, int]]:
        """
        Parse "current/max" format from OCR text.
        Examples: "1301/1301", "945/1301"
        Returns: (current, max) or None
        """
        # Clean text - remove spaces, commas, and common OCR errors
        text = text.strip().replace(" ", "").replace(",", "")
        
        # Match pattern: digits / digits
        match = re.match(r'(\d+)[/|](\d+)', text)
        if match:
            current = int(match.group(1))
            max_val = int(match.group(2))
            
            # CRITICAL: current can NEVER be greater than max!
            # If OCR misreads "1391" as "13991", this catches it
            if current > max_val:
                print(f"⚠️ OCR error: current ({current}) > max ({max_val}), rejecting")
                return None
            
            # Validate reasonable values (typical Tibia HP/Mana range)
            if 1 <= current <= 99999 and 1 <= max_val <= 99999:
                return (current, max_val)
        
        return None
    
    def _ocr_region(self, img: Image.Image) -> str:
        """Perform OCR on a region image. Optimized for speed."""
        import time
        start_time = time.perf_counter()
        
        # Convert to grayscale numpy array
        arr = np.array(img.convert('L'))
        
        # WINDOWS SPEED: Only 2 thresholds for maximum speed
        # These values work well for Tibia's text contrast
        best_thresholds = [120, 160]
        
        for thresh in best_thresholds:
            _, binary = cv2.threshold(arr, thresh, 255, cv2.THRESH_BINARY)
            
            # Scale up for better OCR - 2x is faster than 3x with similar accuracy
            scaled = cv2.resize(binary, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
            
            # Add minimal padding
            padded = cv2.copyMakeBorder(scaled, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=255)
            
            try:
                # OEM 1 = LSTM engine (faster), PSM 7 = single line
                text = pytesseract.image_to_string(
                    padded,
                    config='--psm 7 --oem 1 -c tessedit_char_whitelist=0123456789/'
                ).strip()
                
                # Debug raw OCR for analysis
                if DEBUG_MODE:
                    print(f"DEBUG OCR (thresh={thresh}): '{text}'")
                
                if text and '/' in text:
                    elapsed = (time.perf_counter() - start_time) * 1000
                    print(f"⏱️ OCR: {elapsed:.1f}ms | Result: '{text}'")
                    return text  # Return immediately if we get a valid result
            except:
                pass
        
        # Fallback: try inverted (light text on dark background)
        _, binary = cv2.threshold(arr, 120, 255, cv2.THRESH_BINARY_INV)
        scaled = cv2.resize(binary, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
        padded = cv2.copyMakeBorder(scaled, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=255)
        
        try:
            text = pytesseract.image_to_string(
                padded,
                config='--psm 7 --oem 1 -c tessedit_char_whitelist=0123456789/'
            ).strip()
            if text and '/' in text:
                elapsed = (time.perf_counter() - start_time) * 1000
                print(f"⏱️ OCR (fallback): {elapsed:.1f}ms | Result: '{text}'")
                return text
        except:
            pass
        
        elapsed = (time.perf_counter() - start_time) * 1000
        print(f"⏱️ OCR FAILED: {elapsed:.1f}ms | No valid result")
        return ""
    
    def read_hp(self, screenshot: Image.Image) -> Optional[Tuple[int, int]]:
        """
        Read HP from screenshot.
        Returns: (current, max) or None
        """
        if not self.hp_region:
            return None
        
        try:
            # Scale region for Retina
            scaled_region = self._scale_region(self.hp_region)
            
            # Crop HP region
            hp_img = self._crop_region(screenshot, scaled_region)
            
            # OCR
            text = self._ocr_region(hp_img)
            
            # Parse
            result = self._parse_current_max(text)
            
            if result:
                self.last_hp_current, self.last_hp_max = result
                return result
            
        except Exception as e:
            print(f"⚠️ HP read error: {e}")
        
        return None
    
    def read_mana(self, screenshot: Image.Image) -> Optional[Tuple[int, int]]:
        """
        Read Mana from screenshot.
        Returns: (current, max) or None
        """
        if not self.mana_region:
            return None
        
        try:
            # Scale region for Retina
            scaled_region = self._scale_region(self.mana_region)
            
            # Crop Mana region
            mana_img = self._crop_region(screenshot, scaled_region)
            
            # OCR
            text = self._ocr_region(mana_img)
            
            # Parse
            result = self._parse_current_max(text)
            
            if result:
                self.last_mana_current, self.last_mana_max = result
                return result
            
        except Exception as e:
            print(f"⚠️ Mana read error: {e}")
        
        return None
    
    def read_status(self, screenshot: Image.Image) -> StatusReading:
        """
        Read both HP and Mana from screenshot.
        Returns StatusReading with current values or cached values if read fails.
        """
        hp_result = self.read_hp(screenshot)
        mana_result = self.read_mana(screenshot)
        
        return StatusReading(
            hp_current=hp_result[0] if hp_result else self.last_hp_current,
            hp_max=hp_result[1] if hp_result else self.last_hp_max,
            mana_current=mana_result[0] if mana_result else self.last_mana_current,
            mana_max=mana_result[1] if mana_result else self.last_mana_max,
        )
    
    def reset(self):
        """Reset cached values (call on window change)."""
        self.last_hp_current = None
        self.last_hp_max = None
        self.last_mana_current = None
        self.last_mana_max = None


# Test
if __name__ == "__main__":
    reader = HPManaReader()
    
    # Test parsing
    assert reader._parse_current_max("1301/1301") == (1301, 1301)
    assert reader._parse_current_max("945/1301") == (945, 1301)
    assert reader._parse_current_max("435/435") == (435, 435)
    
    print("✅ Parser tests passed")
