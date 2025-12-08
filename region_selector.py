"""
Windify Bot - Region Selector
Transparent overlay for selecting screen regions.
After selection, immediately tests OCR on that region.
"""

import tkinter as tk
from typing import Callable, Optional, Tuple
from dataclasses import dataclass
import mss
from PIL import Image
import re


@dataclass
class Region:
    """Represents a screen region."""
    x: int
    y: int
    width: int
    height: int
    
    def as_tuple(self) -> Tuple[int, int, int, int]:
        return (self.x, self.y, self.width, self.height)
    
    def is_valid(self) -> bool:
        return self.width > 10 and self.height > 5


@dataclass 
class RegionResult:
    """Result of region selection with OCR test."""
    region: Region
    detected_text: Optional[str] = None
    current_value: Optional[int] = None
    max_value: Optional[int] = None
    
    @property
    def success(self) -> bool:
        return self.current_value is not None and self.max_value is not None


class RegionSelector:
    """
    Transparent fullscreen overlay for selecting screen regions.
    Tests OCR immediately after selection.
    """
    
    SELECTION_COLOR = "#00ff00"
    SELECTION_WIDTH = 2
    
    def __init__(self):
        self.root: Optional[tk.Toplevel] = None
        self.canvas: Optional[tk.Canvas] = None
        self.callback: Optional[Callable[[Optional[Region]], None]] = None
        
        # Drag state
        self.start_x = 0
        self.start_y = 0
        self.rect_id = None
        self.selecting = False
        
        self.screen_width = 0
        self.screen_height = 0
        self.title = ""
    
    def select_region(
        self, 
        parent: tk.Tk,
        callback: Callable[[Optional[Region]], None],
        title: str = "Select Region"
    ) -> None:
        """Open transparent overlay for region selection."""
        self.callback = callback
        self.title = title
        
        # Create fullscreen transparent window
        self.root = tk.Toplevel(parent)
        self.root.title("Select Region")
        
        # Get screen size
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Setup window - transparent background
        self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.3)  # Semi-transparent!
        self.root.configure(bg="black")
        
        # Canvas for drawing selection
        self.canvas = tk.Canvas(
            self.root,
            width=self.screen_width,
            height=self.screen_height,
            highlightthickness=0,
            cursor="crosshair",
            bg="black"
        )
        self.canvas.pack()
        
        # Instructions
        self.canvas.create_rectangle(
            self.screen_width // 2 - 280, 30,
            self.screen_width // 2 + 280, 80,
            fill="black",
            outline="#00ff00",
            width=2
        )
        self.canvas.create_text(
            self.screen_width // 2, 55,
            text=f"🎯 {title} - Drag to select, ESC to cancel",
            fill="white",
            font=("Helvetica", 18, "bold")
        )
        
        # Bind events
        self.canvas.bind("<Button-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
        self.root.bind("<Escape>", self._on_cancel)
        
        self.root.focus_force()
    
    def _on_mouse_down(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.selecting = True
        
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y,
            self.start_x, self.start_y,
            outline=self.SELECTION_COLOR,
            width=self.SELECTION_WIDTH
        )
    
    def _on_mouse_drag(self, event):
        if self.selecting and self.rect_id:
            self.canvas.coords(
                self.rect_id,
                self.start_x, self.start_y,
                event.x, event.y
            )
    
    def _on_mouse_up(self, event):
        if not self.selecting:
            return
        
        self.selecting = False
        
        x1, x2 = sorted([self.start_x, event.x])
        y1, y2 = sorted([self.start_y, event.y])
        
        region = Region(x=x1, y=y1, width=x2 - x1, height=y2 - y1)
        
        self._close()
        
        if region.is_valid() and self.callback:
            # Test OCR on this region immediately
            result = self._test_region(region)
            if result.success:
                print(f"✅ {self.title}: Detected {result.current_value}/{result.max_value}")
            else:
                print(f"⚠️ {self.title}: Could not detect values (region saved anyway)")
            
            self.callback(region)
        elif self.callback:
            self.callback(None)
    
    def _test_region(self, region: Region) -> RegionResult:
        """Test OCR on the selected region."""
        try:
            import pytesseract
            import cv2
            import numpy as np
            
            # Capture the region from screen
            with mss.mss() as sct:
                monitor = {
                    "left": region.x,
                    "top": region.y,
                    "width": region.width,
                    "height": region.height
                }
                screenshot = sct.grab(monitor)
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            
            # Convert to grayscale
            arr = np.array(img.convert('L'))
            
            # Try OCR with different thresholds
            for thresh in [80, 100, 120, 140]:
                _, binary = cv2.threshold(arr, thresh, 255, cv2.THRESH_BINARY)
                scaled = cv2.resize(binary, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
                padded = cv2.copyMakeBorder(scaled, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=255)
                
                text = pytesseract.image_to_string(
                    padded,
                    config='--psm 7 -c tessedit_char_whitelist=0123456789/'
                ).strip()
                
                # Parse "current/max" format
                match = re.match(r'(\d+)[/|](\d+)', text.replace(" ", ""))
                if match:
                    current = int(match.group(1))
                    max_val = int(match.group(2))
                    return RegionResult(
                        region=region,
                        detected_text=text,
                        current_value=current,
                        max_value=max_val
                    )
            
            return RegionResult(region=region, detected_text=text if text else None)
            
        except Exception as e:
            print(f"OCR test error: {e}")
            return RegionResult(region=region)
    
    def _on_cancel(self, event=None):
        self._close()
        if self.callback:
            self.callback(None)
    
    def _close(self):
        if self.root:
            self.root.destroy()
            self.root = None


# Test
if __name__ == "__main__":
    def on_selected(region: Optional[Region]):
        if region:
            print(f"Region: {region.as_tuple()}")
        else:
            print("Cancelled")
        root.quit()
    
    root = tk.Tk()
    root.withdraw()
    
    selector = RegionSelector()
    root.after(100, lambda: selector.select_region(root, on_selected, "Test"))
    
    root.mainloop()
