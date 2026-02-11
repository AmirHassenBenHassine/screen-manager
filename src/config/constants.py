"""Application constants and configuration"""

# Hardware pins
RST, DC, BL, TP_INT = 6, 25, 22, 9

# Menu states
MENU_MAIN = 0
MENU_MQTT = 1
MENU_METRICS = 3
MENU_WIFI = 2
MENU_CONFIRM_SHUTDOWN = 4
MENU_CONFIRM_NETWORK = 5

# MQTT Settings
LOCAL_BROKER = "localhost"
PUBLIC_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_USER = "orion_device"
MQTT_PASS = "123456789"
TOPIC_ENERGY = "energy/metrics"

# File paths
LOG_FILE = "../logs/mqtt_data_log.txt"
DB_PATH = "../logs/energy_data.db"

# Performance settings
STANDBY_TIMEOUT = 60
GESTURE_DEBOUNCE = 0.25
SCROLL_SPEED = 0.05
RENDER_THROTTLE = 0.02
SSID_CACHE_DURATION = 60

# Display settings
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 240

# UI Settings
MAX_DISPLAY_CHARS = 18
MAX_WRAP_WIDTH = 180

# Gesture codes
GESTURE_UP = 0x01
GESTURE_DOWN = 0x02
GESTURE_LEFT = 0x04
GESTURE_TAP = 0x05
GESTURE_LONG_PRESS = 0x0C