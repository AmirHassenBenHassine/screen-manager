"""Theme definitions"""
from PIL import ImageFont

class Theme:
    def __init__(self, name, background_path, font_path, font_size, text_color, selected_color):
        self.name = name
        self.background_path = background_path
        self.font = ImageFont.truetype(font_path, font_size)
        self.text_color = text_color
        self.selected_color = selected_color

THEMES = {
    "light": Theme("light", "../pic/bg_light.jpg", "../Font/DejaVuSans.ttf", 24, "black", "blue"),
    "dark": Theme("dark", "../pic/bg_dark.jpg", "../Font/DejaVuSans.ttf", 24, "white", "cyan"),
}

# Emojis
MENU_EMOJIS = {
    "Energy": "⚡",
    "Device": "📊",
    "WiFi Setup": "📶",
    "Shutdown": "⏻"
}

WIFI_MENU_EMOJIS = {
    "Pair Devices": "⇄",
    "Change WiFi": "↻",
    "Remove WiFi": "✗",
    "Saved Networks": "≡"
}

TOGGLE_THEME_EMOJI = "🌗"