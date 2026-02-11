"""Chart rendering components"""
from PIL import ImageDraw
from ui.renderer import BaseRenderer

class ChartRenderer(BaseRenderer):
    def __init__(self, display, state):
        super().__init__(display, state)
    
    def draw_power_chart(self, phases):
        """Draw bar chart for power data"""
        if not phases:
            self.render_message("No phase data")
            return
        
        image = self.get_background()
        draw = ImageDraw.Draw(image)
        
        screen_width, screen_height = image.size
        bar_width = 30
        spacing = 20
        max_bar_height = 100
        origin_y = 180
        
        max_power = max([p.get("power", 0) for p in phases] + [1])
        total_width = len(phases) * (bar_width + spacing) - spacing
        start_x = (screen_width - total_width) // 2
        
        # Title
        draw.text((60, 10), "Power(W)", fill=self.get_text_color(), font=self.get_font())
        
        bar_colors = ["red", "green", "blue"]
        
        for i, phase in enumerate(phases):
            power = phase.get("power", 0)
            bar_height = int((power / max_power) * max_bar_height)
            
            x = start_x + i * (bar_width + spacing)
            y = origin_y - bar_height
            
            # Draw bar
            draw.rectangle([x, y, x + bar_width, origin_y], 
                          fill=bar_colors[i % len(bar_colors)])
            
            # Draw power value
            value_text = f"{int(power)}"
            value_w = self.get_font().getlength(value_text)
            draw.text((x + (bar_width - value_w) // 2, y - 18), value_text, 
                     fill=self.get_text_color(), font=self.get_font())
            
            # Phase label
            label = f"P{i+1}"
            label_w = self.get_font().getlength(label)
            draw.text((x + (bar_width - label_w) // 2, origin_y + 5), label, 
                     fill=self.get_text_color(), font=self.get_font())
        
        self.display.show_image(image)
        del draw
        del image
    
    def draw_line_chart(self, values):
        """Draw line chart for current data"""
        if not values or len(values) < 2:
            self.render_message("No data for line chart")
            return
        
        image = self.get_background()
        draw = ImageDraw.Draw(image)
        
        max_val = max(values)
        min_val = min(values)
        chart_height = 140
        chart_top = 40
        chart_bottom = chart_top + chart_height
        chart_width = 200
        chart_left = 20
        
        scale = chart_height / (max_val - min_val + 1e-3)
        
        # Title
        draw.text((60, 10), "Current per Phase", fill=self.get_text_color(), font=self.get_font())
        
        # Axes
        draw.line([(chart_left, chart_top), (chart_left, chart_bottom)], fill="gray")
        draw.line([(chart_left, chart_bottom), (chart_left + chart_width, chart_bottom)], fill="gray")
        
        colors = ["red", "green", "blue"]
        
        for i in range(1, len(values)):
            x1 = chart_left + (i - 1) * (chart_width // (len(values) - 1))
            y1 = chart_bottom - int((values[i - 1] - min_val) * scale)
            x2 = chart_left + i * (chart_width // (len(values) - 1))
            y2 = chart_bottom - int((values[i] - min_val) * scale)
            
            draw.line([x1, y1, x2, y2], fill=colors[i % len(colors)], width=2)
        
        self.display.show_image(image)
        del draw
        del image