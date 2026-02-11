"""Confirmation dialogs"""
from PIL import ImageDraw
import os
import time
from ui.renderer import BaseRenderer
from config.constants import *

class ConfirmationMenu(BaseRenderer):
    def __init__(self, display, state):
        super().__init__(display, state)
    
    def render_shutdown_confirmation(self):
        """Render shutdown confirmation"""
        image = self.get_background()
        draw = ImageDraw.Draw(image)
        
        # Message
        msg = "Shutdown?"
        w = self.get_font().getlength(msg)
        draw.text(((SCREEN_WIDTH - w) // 2, 50), msg, fill=self.get_text_color(), font=self.get_font())
        
        # Buttons
        self._draw_yes_no_buttons(draw)
        
        self.display.show_image(image)
        del draw
        del image
    
    def _draw_yes_no_buttons(self, draw):
        """Draw Yes/No buttons"""
        box_w, box_h = 90, 50
        box_y = 120
        spacing = 20
        total_width = 2 * box_w + spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        # NO box
        draw.rectangle([start_x, box_y, start_x + box_w, box_y + box_h], 
                      outline=self.get_selected_color(), width=2)
        no_text = "No"
        no_w = self.get_font().getlength(no_text)
        draw.text((start_x + (box_w - no_w) // 2, box_y + 10), no_text, 
                 fill=self.get_selected_color(), font=self.get_font())
        
        # YES box
        draw.rectangle([start_x + box_w + spacing, box_y, 
                       start_x + 2 * box_w + spacing, box_y + box_h], 
                      outline=self.get_text_color(), width=2)
        yes_text = "Yes"
        yes_w = self.get_font().getlength(yes_text)
        draw.text((start_x + box_w + spacing + (box_w - yes_w) // 2, box_y + 10), 
                 yes_text, fill=self.get_text_color(), font=self.get_font())
    
    def handle_shutdown_gesture(self, gesture, touch_device):
        """Handle shutdown confirmation gestures"""
        if gesture == GESTURE_LONG_PRESS:
            return MENU_MAIN
        
        if gesture == GESTURE_TAP:
            touch_device.get_point()
            x, y = touch_device.X_point, touch_device.Y_point
            
            box_w, box_h = 90, 50
            box_y = 120
            spacing = 20
            start_x = (SCREEN_WIDTH - (2 * box_w + spacing)) // 2
            
            # NO box
            if start_x <= x <= start_x + box_w and box_y <= y <= box_y + box_h:
                return MENU_MAIN
            # YES box
            elif start_x + box_w + spacing <= x <= start_x + 2 * box_w + spacing and \
                 box_y <= y <= box_y + box_h:
                self.render_message("Shutting down...")
                time.sleep(2)
                os.system("sudo shutdown now")
        
        return None