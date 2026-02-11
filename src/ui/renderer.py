"""Base rendering functions"""
from PIL import Image, ImageDraw, ImageFont
from config.constants import *

class BaseRenderer:
    def __init__(self, display, state):
        self.display = display
        self.state = state
    
    def get_background(self):
        """Get fresh background"""
        return self.display.get_background_copy(self.state.active_theme)
    
    def get_font(self, size=24):
        """Get font with specified size"""
        return ImageFont.truetype("../Font/DejaVuSans.ttf", size)
    
    def get_text_color(self):
        """Get theme text color"""
        return self.state.active_theme.text_color
    
    def get_selected_color(self):
        """Get theme selected color"""
        return self.state.active_theme.selected_color
    
    def wrap_text(self, text, font, max_width):
        """Wrap text to fit width"""
        lines = []
        words = text.split()
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines
    
    def render_message(self, message, font_size=24):
        """Render centered message"""
        image = self.get_background()
        draw = ImageDraw.Draw(image)
        
        # Adjust font for message length
        if len(message) > 50:
            font = self.get_font(18)
        elif len(message) > 30:
            font = self.get_font(20)
        else:
            font = self.get_font(font_size)
        
        lines = message.split('\n')
        all_lines = []
        
        for line in lines:
            if line.strip():
                wrapped = self.wrap_text(line, font, MAX_WRAP_WIDTH)
                all_lines.extend(wrapped)
            else:
                all_lines.append("")
        
        line_height = font_size + 4
        total_height = len(all_lines) * line_height
        y_start = max(30, (SCREEN_HEIGHT - total_height) // 2 - 10)
        
        for i, line in enumerate(all_lines):
            if line:
                line_w = font.getlength(line)
                x = (SCREEN_WIDTH - line_w) // 2
                y = y_start + (i * line_height)
                draw.text((x, y), line, fill=self.get_text_color(), font=font)
        
        self.display.show_image(image)
        del draw
        del image