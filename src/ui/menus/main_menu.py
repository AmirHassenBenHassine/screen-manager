"""Main menu rendering and handling"""
import time
from PIL import ImageDraw
from ui.renderer import BaseRenderer
from config.constants import *
from config.themes import TOGGLE_THEME_EMOJI, THEMES

class MainMenu(BaseRenderer):
    def __init__(self, display, state):
        super().__init__(display, state)
        self.items = ["Energy", "Device", "WiFi Setup", "Shutdown"]
    
    def render(self):
        """Render main menu"""
        image = self.get_background()
        draw = ImageDraw.Draw(image)
        
        # Update notification badge (if available)
        if self.state.update_available:
            badge_font = self.get_font(14)
            badge_text = "🔔 Update"
            badge_w = badge_font.getlength(badge_text)
            draw.text((SCREEN_WIDTH - badge_w - 10, 10), badge_text, 
                    fill="orange", font=badge_font)
        
        height = len(self.items) * 40
        y_start = (SCREEN_HEIGHT - height) // 2
        
        for i, item in enumerate(self.items):
            prefix = "➤ " if i == self.state.selected_option else "  "
            text = prefix + item
            color = self.get_selected_color() if i == self.state.selected_option else self.get_text_color()
            w = self.get_font().getlength(text)
            draw.text(((SCREEN_WIDTH - w) // 2, y_start + i * 40), text, fill=color, font=self.get_font())
        
        # Theme toggle
        emoji_w = self.get_font().getlength(TOGGLE_THEME_EMOJI)
        draw.text(((SCREEN_WIDTH - emoji_w) // 2, SCREEN_HEIGHT - 35), 
                TOGGLE_THEME_EMOJI, fill=self.get_selected_color(), font=self.get_font())
        
        self.display.show_image(image)
        del draw
        del image

    def handle_gesture(self, gesture, touch_device=None):
        """Handle main menu gestures"""
        if gesture == GESTURE_UP:
            self.state.selected_option = (self.state.selected_option - 1) % len(self.items)
            self.render()
        elif gesture == GESTURE_DOWN:
            self.state.selected_option = (self.state.selected_option + 1) % len(self.items)
            self.render()
        elif gesture == GESTURE_TAP:
            # Check if tapped on update notification
            if touch_device and self.state.update_available:
                touch_device.get_point()
                x, y = touch_device.X_point, touch_device.Y_point
                
                # Update badge area (top right)
                if x > SCREEN_WIDTH - 100 and y < 30:
                    return MENU_UPDATE
            
            return self._handle_selection(touch_device)
        
        return None

    def _handle_selection(self, touch_device):
        """Handle menu selection"""
        # Check for theme toggle (only if touch_device provided)
        if touch_device:
            touch_device.get_point()
            x, y = touch_device.X_point, touch_device.Y_point
            
            # Coordinates for toggle emoji
            emoji_y_range = (205, 235)
            emoji_w = self.get_font().getlength(TOGGLE_THEME_EMOJI)
            emoji_x_range = ((SCREEN_WIDTH - emoji_w) // 2 - 10, (SCREEN_WIDTH + emoji_w) // 2 + 10)

            if emoji_y_range[0] <= y <= emoji_y_range[1] and emoji_x_range[0] <= x <= emoji_x_range[1]:
                # Toggle theme
                self.state.active_theme = THEMES["light"] if self.state.active_theme.name == "dark" else THEMES["dark"]
                self.render()
                time.sleep(0.2)
                return None
        
        time.sleep(0.1)
        
        # Return next menu based on selection
        menu_map = {
            0: MENU_MQTT,
            1: MENU_METRICS,
            2: MENU_WIFI,
            3: MENU_CONFIRM_SHUTDOWN
        }
        
        return menu_map.get(self.state.selected_option)