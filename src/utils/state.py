"""Global application state"""
import time
from config.themes import THEMES

class AppState:
    def __init__(self):
        # Theme
        self.active_theme = THEMES["dark"]
        
        # Menu state
        self.current_menu = 0
        self.selected_option = 0
        self.current_page = 0
        
        # WiFi state
        self.wifi_selected = 0
        self.saved_networks_list = []
        self.saved_networks_selected = 0
        self.in_saved_networks_mode = False
        self.in_wifi_qr_mode = False
        self.network_to_connect = None
        
        # Energy data
        self.energy_metrics = []
        self.energy_data = {}
        self.chart_mode = 0
        
        # Device metrics
        self.device_metrics_pages = []
        
        # Touch/gesture state
        self.last_gesture = None
        self.last_gesture_time = 0
        self.last_activity_time = time.time()
        self.is_standby = False
        
        # Scrolling state
        self.scroll_offset = 0
        self.last_scroll_time = 0
        self.last_selected_network = None
        self.last_render_time = 0
        
        # Network cache
        self.cached_current_ssid = None
        self.last_ssid_check_time = 0

# Global instance
state = AppState()