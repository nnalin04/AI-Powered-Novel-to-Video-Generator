import os
from PIL import Image, ImageDraw, ImageFont
from typing import Optional
from ai_novel_to_video.services.image_generator import ImageGenerator

class ThumbnailGenerator:
    def __init__(self, image_generator: ImageGenerator):
        self.image_generator = image_generator

    def generate_thumbnail(self, title: str, prompt: str, output_path: str) -> Optional[str]:
        """
        Generates a thumbnail with the given title overlaid on an image generated from the prompt.
        """
        print(f"Generating thumbnail for title: '{title}' with prompt: '{prompt}'...")
        
        # 1. Generate Background Image
        # We'll use a temporary path for the raw image
        temp_bg_path = output_path.replace(".png", "_bg.png")
        bg_path = self.image_generator.generate_image(prompt, temp_bg_path)
        
        if not bg_path or not os.path.exists(bg_path):
            print("Error: Failed to generate background image for thumbnail.")
            return None

        try:
            # 2. Open Image
            with Image.open(bg_path) as img:
                # Convert to RGBA for transparency support if needed
                img = img.convert("RGBA")
                
                # 3. Overlay Text
                self._draw_text_overlay(img, title)
                
                # 4. Save Final Thumbnail
                # Convert back to RGB to save as PNG/JPG (PNG supports RGBA but let's be standard)
                final_img = img.convert("RGB")
                final_img.save(output_path)
                
            print(f"Thumbnail saved to {output_path}")
            
            # Clean up temp file
            if os.path.exists(temp_bg_path):
                os.remove(temp_bg_path)
                
            return output_path

        except Exception as e:
            print(f"Error creating thumbnail overlay: {e}")
            return None

    def _draw_text_overlay(self, img: Image.Image, text: str):
        """Draws centered text with a semi-transparent background."""
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # Try to load a nice font, fallback to default
        try:
            # Try to find a system font or use default
            # On Linux/Mac, usually at /usr/share/fonts or /System/Library/Fonts
            # For simplicity/robustness in this env, we might use default or try to load one.
            # Let's try a common one, or just default if fails.
            font_size = int(height / 8) # Dynamic font size
            font = ImageFont.truetype("Arial.ttf", font_size)
        except IOError:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(height/8))
            except IOError:
                print("Warning: Could not load custom font. Using default.")
                font = ImageFont.load_default()

        # Calculate text size
        # bbox = draw.textbbox((0, 0), text, font=font) # Pillow >= 8.0.0
        # text_width = bbox[2] - bbox[0]
        # text_height = bbox[3] - bbox[1]
        
        # Older Pillow compatibility or just robust way:
        text_width = draw.textlength(text, font=font)
        # Estimate height
        text_height = int(height / 8) 

        x = (width - text_width) / 2
        y = (height - text_height) / 2
        
        # Draw semi-transparent background box
        padding = 20
        box_coords = [x - padding, y - padding, x + text_width + padding, y + text_height + padding]
        
        # Create a separate overlay for transparency
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw_overlay = ImageDraw.Draw(overlay)
        draw_overlay.rectangle(box_coords, fill=(0, 0, 0, 160)) # Black with alpha
        
        img.alpha_composite(overlay)
        
        # Draw Text
        draw = ImageDraw.Draw(img) # Re-create draw object for composite image
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
