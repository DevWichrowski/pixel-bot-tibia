"""
Tibia Pixel Bot - Screen Capture
Fast screen capture from Tibia window using mss.
"""

import mss
from PIL import Image


class ScreenCapture:
    """Fast screen capture with Retina display support."""
    
    def __init__(self):
        self.sct = mss.mss()
        self._scale = self._get_retina_scale()
    
    def _get_retina_scale(self):
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
    
    def capture_window(self, window_info):
        """Capture entire Tibia window, returns PIL Image."""
        if not window_info:
            return None
        
        s = self._scale
        monitor = {
            "left": int(window_info['x'] * s),
            "top": int(window_info['y'] * s),
            "width": int(window_info['width'] * s),
            "height": int(window_info['height'] * s),
        }
        
        shot = self.sct.grab(monitor)
        return Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
    
    def close(self):
        self.sct.close()
