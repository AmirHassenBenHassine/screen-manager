"""Energy/MQTT menu rendering and handling"""
from PIL import ImageDraw
from ui.renderer import BaseRenderer
from ui.components.charts import ChartRenderer
from config.constants import *

class EnergyMenu(BaseRenderer):
    def __init__(self, display, state):
        super().__init__(display, state)
        self.chart_renderer = ChartRenderer(display, state)
    
    def render(self):
        """Render energy data based on chart mode"""
        if self.state.chart_mode == 0:  # Scroll text
            self._render_text_mode()
        elif self.state.chart_mode == 1:  # Bar chart
            self.chart_renderer.draw_power_chart(self.state.energy_data.get("phases", []))
        elif self.state.chart_mode == 2:  # Line chart
            currents = [p.get("current", 0) for p in self.state.energy_data.get("phases", [])]
            self.chart_renderer.draw_line_chart(currents)
    
    def _render_text_mode(self):
        """Render scrolling text mode"""
        if not self.state.energy_metrics:
            self.render_message("No energy metrics to display")
            return
        
        index = self.state.current_page % len(self.state.energy_metrics)
        
        image = self.get_background()
        draw = ImageDraw.Draw(image)
        
        lines = self.wrap_text(self.state.energy_metrics[index], self.get_font(), 220)
        y = 80
        for line in lines:
            draw.text((20, y), line, fill=self.get_text_color(), font=self.get_font())
            y += 30
        
        # Arrows
        arrow_x = SCREEN_WIDTH // 2 - 10
        draw.text((arrow_x, 10), "▲", fill=self.get_selected_color(), font=self.get_font())
        draw.text((arrow_x, SCREEN_HEIGHT - 30), "▼", fill=self.get_selected_color(), font=self.get_font())
        
        self.display.show_image(image)
        del draw
        del image
    
    def handle_gesture(self, gesture):
        """Handle energy menu gestures"""
        if not self.state.energy_metrics:
            if gesture in [GESTURE_LEFT, GESTURE_LONG_PRESS]:
                return MENU_MAIN
            return None
        
        if gesture == GESTURE_UP:
            self.state.current_page = (self.state.current_page - 1) % len(self.state.energy_metrics)
            self.render()
        elif gesture == GESTURE_DOWN:
            self.state.current_page = (self.state.current_page + 1) % len(self.state.energy_metrics)
            self.render()
        elif gesture == GESTURE_TAP:
            self.state.chart_mode = (self.state.chart_mode + 1) % 3
            self.render()
        elif gesture in [GESTURE_LEFT, GESTURE_LONG_PRESS]:
            return MENU_MAIN
        
        return None