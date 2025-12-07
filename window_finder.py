"""
Tibia Pixel Bot - Window Finder
Auto-detects Tibia client window on macOS.
"""

import Quartz


def get_all_windows():
    """Get list of all visible windows."""
    windows = []
    window_list = Quartz.CGWindowListCopyWindowInfo(
        Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements,
        Quartz.kCGNullWindowID
    )
    
    for window in window_list:
        bounds = window.get(Quartz.kCGWindowBounds, {})
        if bounds:
            windows.append({
                'id': window.get(Quartz.kCGWindowNumber, 0),
                'name': window.get(Quartz.kCGWindowName, '') or '',
                'owner': window.get(Quartz.kCGWindowOwnerName, '') or '',
                'x': int(bounds.get('X', 0)),
                'y': int(bounds.get('Y', 0)),
                'width': int(bounds.get('Width', 0)),
                'height': int(bounds.get('Height', 0)),
            })
    
    return windows


def find_tibia_window():
    """Find Tibia client window by owner name."""
    for window in get_all_windows():
        if window['owner'] == "Tibia" and window['width'] > 200:
            return window
    return None


class WindowTracker:
    """Tracks Tibia window position and size changes."""
    
    def __init__(self):
        self.last_window = None
        self.changed = False
    
    def update(self):
        """Update window info, returns current window or None."""
        window = find_tibia_window()
        
        if window and self.last_window:
            self.changed = (
                window['x'] != self.last_window['x'] or
                window['y'] != self.last_window['y'] or
                window['width'] != self.last_window['width'] or
                window['height'] != self.last_window['height']
            )
        else:
            self.changed = window is not None and self.last_window is None
        
        self.last_window = window
        return window
    
    def has_changed(self):
        return self.changed
