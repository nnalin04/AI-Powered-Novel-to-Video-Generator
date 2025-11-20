import random
from typing import Tuple, Optional
try:
    from moviepy import ImageClip, VideoClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

class AnimationService:
    def __init__(self):
        pass

    def apply_ken_burns(self, image_path: str, duration: float, zoom_ratio: float = 0.15, direction: str = 'random') -> Optional[VideoClip]:
        """
        Applies a Ken Burns effect (zoom/pan) to an image.
        
        Args:
            image_path: Path to the image file.
            duration: Duration of the clip in seconds.
            zoom_ratio: How much to zoom/move (e.g., 0.15 = 15%).
            direction: 'in', 'out', 'left', 'right', 'up', 'down', or 'random'.
            
        Returns:
            A VideoClip with the effect applied, or None if MoviePy is not available.
        """
        if not MOVIEPY_AVAILABLE:
            return None
            
        try:
            # Load image
            clip = ImageClip(image_path).with_duration(duration)
            w, h = clip.size
            
            if direction == 'random':
                direction = random.choice(['in', 'out', 'left', 'right', 'up', 'down'])
            
            # Functions for effects
            
            if direction == 'in':
                # Zoom In: Scale up over time, keep center
                def resize_func(t):
                    return 1 + (zoom_ratio * t / duration)
                
                zoomed_clip = clip.resized(resize_func)
                final_clip = zoomed_clip.cropped(width=w, height=h, x_center=w/2, y_center=h/2)
                
            elif direction == 'out':
                # Zoom Out: Start scaled up, scale down to 1
                # To do this smoothly, we start at 1+zoom_ratio and go to 1
                def resize_func(t):
                    return 1 + (zoom_ratio * (1 - t / duration))
                
                zoomed_clip = clip.resized(resize_func)
                final_clip = zoomed_clip.cropped(width=w, height=h, x_center=w/2, y_center=h/2)
                
            elif direction in ['left', 'right', 'up', 'down']:
                # Panning requires the image to be larger than the frame initially
                # So we resize it up first (static resize)
                enlarged_clip = clip.resized(1 + zoom_ratio)
                ew, eh = enlarged_clip.size
                
                # Calculate max offsets
                max_x_offset = (ew - w) / 2
                max_y_offset = (eh - h) / 2
                
                # Manual panning implementation using with_updated_frame_function (MoviePy v2 replacement for fl)
                def make_frame(t):
                    frame = enlarged_clip.get_frame(t)
                    # frame is numpy array (H, W, C)
                    img_h, img_w = frame.shape[:2]
                    
                    progress = t / duration
                    
                    # Calculate center based on direction
                    if direction == 'left':
                        xc = (ew / 2) + (max_x_offset * (1 - 2 * progress))
                        yc = eh / 2
                    elif direction == 'right':
                        xc = (ew / 2) - (max_x_offset * (1 - 2 * progress))
                        yc = eh / 2
                    elif direction == 'up':
                        xc = ew / 2
                        yc = (eh / 2) + (max_y_offset * (1 - 2 * progress))
                    elif direction == 'down':
                        xc = ew / 2
                        yc = (eh / 2) - (max_y_offset * (1 - 2 * progress))
                    else:
                        xc, yc = ew/2, eh/2
                        
                    # Calculate top-left corner
                    x1 = int(xc - w/2)
                    y1 = int(yc - h/2)
                    
                    # Clamp to ensure we don't go out of bounds
                    x1 = max(0, min(x1, img_w - w))
                    y1 = max(0, min(y1, img_h - h))
                    
                    return frame[y1:y1+h, x1:x1+w]

                final_clip = enlarged_clip.with_updated_frame_function(make_frame)
                final_clip.size = (w, h)
            
            else:
                # Default to Zoom In if unknown
                return self.apply_ken_burns(image_path, duration, zoom_ratio, 'in')

            return final_clip
            
        except Exception as e:
            print(f"Error applying Ken Burns effect ({direction}): {e}")
            # Fallback to static image
            return ImageClip(image_path).with_duration(duration)
