"""Chart rendering components"""
from PIL import ImageDraw
from ui.renderer import BaseRenderer
from config.constants import SCREEN_WIDTH, SCREEN_HEIGHT

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
        
        bar_width = 30
        spacing = 20
        max_bar_height = 100
        origin_y = 180
        
        max_power = max([p.get("power", 0) for p in phases] + [1])
        total_width = len(phases) * (bar_width + spacing) - spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        
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
    
    def draw_trend_chart(self, draw, data, y_start, height, label):
        """Draw compact trend chart for historical data"""
        if not data or len(data) < 2:
            # Draw "No data" message on the draw object
            no_data_font = self.get_font(14)
            draw.text((20, y_start + 20), f"No {label} data yet", 
                     fill="gray", font=no_data_font)
            return
        
        # Extract power values
        powers = [d.get('totalPower', 0) for d in data]
        
        if not any(powers):  # All zeros
            no_data_font = self.get_font(14)
            draw.text((20, y_start + 20), f"All {label} values are zero", 
                     fill="gray", font=no_data_font)
            return
        
        max_power = max(powers)
        min_power = min([p for p in powers if p > 0] + [0])
        
        chart_width = 200
        chart_left = 20
        chart_right = chart_left + chart_width
        chart_bottom = y_start + height
        
        if max_power == min_power:
            scale = 1
        else:
            scale = height / (max_power - min_power)
        
        # Draw axes
        draw.line([(chart_left, y_start), (chart_left, chart_bottom)], fill="gray")
        draw.line([(chart_left, chart_bottom), (chart_right, chart_bottom)], fill="gray")
        
        # Draw trend line
        points = []
        for i, power in enumerate(powers):
            x = chart_left + (i * chart_width / (len(powers) - 1))
            y = chart_bottom - int((power - min_power) * scale)
            points.append((x, y))
        
        # Draw line segments
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]], fill=self.get_selected_color(), width=2)
        
        # Label
        label_font = self.get_font(12)
        draw.text((chart_left, y_start - 15), label, fill="gray", font=label_font)