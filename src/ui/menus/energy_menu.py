"""Energy/MQTT menu rendering and handling"""
from PIL import ImageDraw
from ui.renderer import BaseRenderer
from ui.components.charts import ChartRenderer
from config.constants import *

class EnergyMenu(BaseRenderer):
    def __init__(self, display, state, energy_analyzer=None):
        super().__init__(display, state)
        self.chart_renderer = ChartRenderer(display, state)
        self.energy_analyzer = energy_analyzer
        self.view_mode = 0  # 0=current, 1=24h, 2=7d
    
    def render(self):
        """Render energy data based on view mode"""
        if self.view_mode == 0:
            self._render_current_data()
        elif self.view_mode == 1:
            self._render_24h_view()
        elif self.view_mode == 2:
            self._render_7d_view()
    
    def _render_current_data(self):
        """Render current real-time data"""
        if self.state.chart_mode == 0:  # Text mode
            self._render_text_with_status()
        elif self.state.chart_mode == 1:  # Bar chart
            self.chart_renderer.draw_power_chart(self.state.energy_data.get("phases", []))
        elif self.state.chart_mode == 2:  # Line chart
            currents = [p.get("current", 0) for p in self.state.energy_data.get("phases", [])]
            self.chart_renderer.draw_line_chart(currents)
    
    def _render_text_with_status(self):
        """Render scrolling text with status bar"""
        if not self.state.energy_metrics:
            self.render_message("No energy metrics")
            return
        
        index = self.state.current_page % len(self.state.energy_metrics)
        
        image = self.get_background()
        draw = ImageDraw.Draw(image)
        
        # Status bar at top
        self._draw_status_bar(draw)
        
        # Main content
        lines = self.wrap_text(self.state.energy_metrics[index], self.get_font(), 220)
        y = 50  # Lower to make room for status bar
        for line in lines:
            draw.text((20, y), line, fill=self.get_text_color(), font=self.get_font())
            y += 30
        
        # Navigation arrows
        arrow_x = SCREEN_WIDTH // 2 - 10
        draw.text((arrow_x, SCREEN_HEIGHT - 30), "▼", fill=self.get_selected_color(), font=self.get_font())
        
        # View mode indicator
        view_text = "Current"
        view_font = self.get_font(14)
        view_w = view_font.getlength(view_text)
        draw.text((SCREEN_WIDTH - view_w - 10, SCREEN_HEIGHT - 25), view_text, 
                 fill="gray", font=view_font)
        
        self.display.show_image(image)
        del draw
        del image
    
    def _draw_status_bar(self, draw):
        """Draw status bar with battery and time since last update"""
        status_font = self.get_font(14)
        
        # Battery
        battery = self.state.energy_data.get('battery', None)
        if battery is not None:
            battery_text = f"🔋 {battery:.0f}%"
            draw.text((25, 25), battery_text, fill=self.get_selected_color(), font=status_font)
        
        # Time since last data
        if self.energy_analyzer:
            time_text = self.energy_analyzer.get_time_since_last_data()
            time_w = status_font.getlength(time_text)
            draw.text((SCREEN_WIDTH - time_w - 10, 10), time_text, 
                     fill="gray", font=status_font)
    
    def _render_24h_view(self):
        """Render 24 hour analysis"""
        if not self.energy_analyzer:
            self.render_message("No analyzer\navailable")
            return
        
        stats = self.energy_analyzer.get_24h_stats()
        if not stats:
            self.render_message("No 24h data\nyet")
            return
        
        image = self.get_background()
        draw = ImageDraw.Draw(image)
        
        # Title
        title = "Last 24 Hours"
        title_font = self.get_font(20)
        title_w = title_font.getlength(title)
        draw.text(((SCREEN_WIDTH - title_w) // 2, 10), title, 
                 fill=self.get_selected_color(), font=title_font)
        
        # Stats
        stats_font = self.get_font(18)
        y = 40
        
        stats_text = [
            f"Avg Power: {stats['avg_power']:.1f} W",
            f"Max Power: {stats['max_power']:.1f} W",
            f"Min Power: {stats['min_power']:.1f} W",
            f"Energy: {stats['total_energy']:.2f} kWh",
            f"Samples: {stats['data_points']}"
        ]
        
        for text in stats_text:
            draw.text((20, y), text, fill=self.get_text_color(), font=stats_font)
            y += 28
        
        # Draw mini chart
        self.chart_renderer.draw_trend_chart(
            draw, self.energy_analyzer.get_chart_data_24h(), 
            y + 10, 80, "24h"
        )
        
        self.display.show_image(image)
        del draw
        del image
    
    def _render_7d_view(self):
        """Render 7 day analysis"""
        if not self.energy_analyzer:
            self.render_message("No analyzer\navailable")
            return
        
        stats = self.energy_analyzer.get_7d_stats()
        if not stats:
            self.render_message("No 7d data\nyet")
            return
        
        image = self.get_background()
        draw = ImageDraw.Draw(image)
        
        # Title
        title = "Last 7 Days"
        title_font = self.get_font(20)
        title_w = title_font.getlength(title)
        draw.text(((SCREEN_WIDTH - title_w) // 2, 10), title, 
                 fill=self.get_selected_color(), font=title_font)
        
        # Stats
        stats_font = self.get_font(18)
        y = 40
        
        stats_text = [
            f"Avg Power: {stats['avg_power']:.1f} W",
            f"Max Power: {stats['max_power']:.1f} W",
            f"Total Energy: {stats['total_energy']:.2f} kWh",
            f"Samples: {stats['data_points']}"
        ]
        
        for text in stats_text:
            draw.text((20, y), text, fill=self.get_text_color(), font=stats_font)
            y += 30
        
        # Draw mini chart
        self.chart_renderer.draw_trend_chart(
            draw, self.energy_analyzer.get_chart_data_7d(), 
            y + 10, 70, "7d"
        )
        
        self.display.show_image(image)
        del draw
        del image
    
    def handle_gesture(self, gesture, touch_device=None):  
        """Handle energy menu gestures"""
        if not self.state.energy_metrics and self.view_mode == 0:
            if gesture in [GESTURE_LEFT, GESTURE_LONG_PRESS]:
                return MENU_MAIN
            return None
        
        if gesture == GESTURE_UP:
            if self.view_mode == 0:
                self.state.current_page = (self.state.current_page - 1) % len(self.state.energy_metrics)
            self.render()
        elif gesture == GESTURE_DOWN:
            if self.view_mode == 0:
                self.state.current_page = (self.state.current_page + 1) % len(self.state.energy_metrics)
            self.render()
        elif gesture == GESTURE_TAP:
            # Cycle: current -> 24h -> 7d -> chart modes -> current
            if self.view_mode < 2:
                self.view_mode += 1
            elif self.view_mode == 2:
                self.view_mode = 0
                self.state.chart_mode = (self.state.chart_mode + 1) % 3
            self.render()
        elif gesture in [GESTURE_LEFT, GESTURE_LONG_PRESS]:
            self.view_mode = 0
            return MENU_MAIN
        
        return None