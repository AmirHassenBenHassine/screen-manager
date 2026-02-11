"""Display management"""
import logging
from PIL import Image
from config.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class DisplayManager:
    def __init__(self, disp):
        self.disp = disp
        self._background_cache = {}
        
    def init(self):
        """Initialize display with optimizations"""
        self.disp.Init()
        self._optimize_performance()
        self.disp.clear()
        
    def _optimize_performance(self):
        """Apply performance optimizations"""
        try:
            # Tearing effect sync
            self.disp.LCD_WriteReg(0x35)
            self.disp.LCD_WriteData_Byte(0x00)
            logging.info("Display optimizations applied")
        except Exception as e:
            logging.warning(f"Could not optimize display: {e}")
    
    def get_background_copy(self, theme):
        """Get fresh background copy"""
        try:
            with Image.open(theme.background_path) as img:
                new_img = Image.new("RGB", img.size)
                new_img.paste(img)
                return new_img
        except Exception as e:
            logging.error(f"Error loading background: {e}")
            color = (0, 0, 0) if theme.name == "dark" else (255, 255, 255)
            return Image.new("RGB", (SCREEN_WIDTH, SCREEN_HEIGHT), color=color)
    
    def show_image(self, image):
        """Display image"""
        try:
            self.disp.ShowImage(image)
        except Exception as e:
            logging.error(f"Display error: {e}")
    
    def clear(self):
        """Clear display"""
        self.disp.clear()
    
    def sleep(self):
        """Put display to sleep"""
        logging.info("Display sleep")
        self.disp.LCD_WriteReg(0x28)
        self.disp.LCD_WriteReg(0x10)
    
    def wake(self):
        """Wake display"""
        logging.info("Display wake")
        self.disp.LCD_WriteReg(0x11)
        import time
        time.sleep(0.12)
        self.disp.LCD_WriteReg(0x29)