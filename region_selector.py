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
        self.offset_x = 0
        self.offset_y = 0
        self.title = ""
    
    def select_region(
        self, 
        parent: tk.Tk,
        callback: Callable[[Optional[Region]], None],
        title: str = "Select Region",
        monitor_geometry: Optional[dict] = None
    ) -> None:
        """Open transparent overlay for region selection on specific monitor."""
        self.callback = callback
        self.title = title
        
        # Create fullscreen transparent window
        self.root = tk.Toplevel(parent)
        self.root.title("Select Region")
        
        # Determine geometry
        if monitor_geometry:
            x = monitor_geometry["left"]
            y = monitor_geometry["top"]
            w = monitor_geometry["width"]
            h = monitor_geometry["height"]
        else:
            # Fallback to primary
            w = self.root.winfo_screenwidth()
            h = self.root.winfo_screenheight()
            x = 0
            y = 0
            
        self.screen_width = w
        self.screen_height = h
        
        # Setup window - transparent background
        # Note: on Windows, negative coords (secondary monitor to the left) work fine
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.3)  # Semi-transparent!
        self.root.configure(bg="black")
        
        # Store offsets for absolute coordinate calculation later
        self.offset_x = x
        self.offset_y = y
        
        # Canvas for drawing selection
        self.canvas = tk.Canvas(
            self.root,
            width=w,
            height=h,
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
        
        # Create region with RELATIVE coordinates for now (needed for OCR visual test)
        # But for the final result, we should probably check if the user expects absolute.
        # The bot logic in main.py usually expects coordinates relative to the monitor it captures.
        # However, mss.grab() expects absolute screen coordinates if we provide a dict.
        # If main.py does sct.grab(sct.monitors[1]), that's absolute coordinates internally.
        
        # CRITICAL FIX: Region object should store absolute coordinates if we want consistent behavior
        # But wait, main.py uses `img = self._capture_screen()` -> `sct.grab(monitor)`.
        # `monitor` is `sct.monitors[1]`.
        # `reader.read_status(img)` -> crops relative to that image.
        # So we need coordinates RELATIVE TO THE MONITOR (image), not absolute screen coords?
        
        # No, wait. 
        # _capture_screen captures the whole specific monitor. The image is 1920x1080 (for example).
        # The region coordinates must be relative to that image (0,0 to 1920,1080).
        # Since our overlay `canvas` covers exactly that monitor (width x height),
        # `event.x` and `event.y` ARE ALREADY relative to that monitor's top-left!
        
        # So: region x/y are correct relative to monitor.
        # We just needed absolute for the immediate OCR test below (because mss needs absolute).
        
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
            # Note: region.x/y are relative to the overlay window
            # If overlay is on secondary monitor (e.g. at x=1920), we need to add that offset
            
            # Find which monitor this region belongs to (simplified)
            with mss.mss() as sct:
                # We need global coordinates
                # Since we don't easily have the monitor offset here without passing it,
                # let's assume the region coordinates are relative to the window provided.
                # However, modifying _test_region strictly might be complex without the offset.
                # simpler approach: capture the specific monitor using mss and crop.
                pass 
                
                # REVERTED STRATEGY: We captured `region` from mouse events on the canvas.
                # If the canvas was at +1920, the event.x might be relative to 1920 or 0 depending on Tkinter.
                # Standard Tkinter event.x is relative to the widget.
                # So if we placed window at 1920,0, event.x=10 means absolute x=1930.
                
                # To fix this properly, we need to know the window position.
                # But `select_region` is async (callback).
                # Let's rely on the passed callback to handle coordinate translation if needed,
                # OR (better) just capture relative to the monitor we are on.
                
                # For now, let's trust that mss.grab(monitor) works with the dictionary provided below.
                # If we pass explicit layout to mss:
                
                # Calculate absolute screen coordinates
                abs_x = self.offset_x + region.x
                abs_y = self.offset_y + region.y
                
                monitor = {
                    "left": abs_x,
                    "top": abs_y,
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
