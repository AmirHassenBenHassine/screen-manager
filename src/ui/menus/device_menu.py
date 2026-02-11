"""Device metrics menu"""
from PIL import ImageDraw
from ui.renderer import BaseRenderer
from config.constants import *

class DeviceMenu(BaseRenderer):
    def __init__(self, display, state):
        super().__init__(display, state)
    
    def render(self):
        """Render device metrics"""
        if not self.state.device_metrics_pages:
            self.render_message("Loading device metrics...")
            return
        
        image = self.get_background()
        draw = ImageDraw.Draw(image)
        
        text = self.state.device_metrics_pages[self.state.current_page % len(self.state.device_metrics_pages)]
        lines = self.wrap_text(text, self.get_font(), max_width=220)
        y = 80
        for line in lines:
            draw.text((20, y), line, fill=self.get_text_color(), font=self.get_font())
            y += 30
        
        # Centered scroll arrows
        arrow_x = SCREEN_WIDTH // 2 - 10
        draw.text((arrow_x, 10), "▲", fill=self.get_selected_color(), font=self.get_font())
        draw.text((arrow_x, SCREEN_HEIGHT - 30), "▼", fill=self.get_selected_color(), font=self.get_font())
        
        self.display.show_image(image)
        del draw
        del image
    
    def handle_gesture(self, gesture):
        """Handle device menu gestures"""
        if not self.state.device_metrics_pages:
            if gesture in [GESTURE_LEFT, GESTURE_LONG_PRESS]:
                return MENU_MAIN
            return None
        
        if gesture == GESTURE_UP:
            self.state.current_page = (self.state.current_page - 1) % len(self.state.device_metrics_pages)
            self.render()
        elif gesture == GESTURE_DOWN:
            self.state.current_page = (self.state.current_page + 1) % len(self.state.device_metrics_pages)
            self.render()
        elif gesture in [GESTURE_LEFT, GESTURE_LONG_PRESS]:
            self.state.current_page = 0
            return MENU_MAIN
        
        return None