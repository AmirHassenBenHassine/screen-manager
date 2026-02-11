"""Data logging service"""
import json
import logging
from datetime import datetime
from config.constants import LOG_FILE

class DataLogger:
    def __init__(self):
        self.log_file = LOG_FILE
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        """Ensure log file and directory exist"""
        import os
        log_dir = os.path.dirname(self.log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    def log_data(self, data):
        """Log energy data to file"""
        try:
            with open(self.log_file, "a") as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"{timestamp} - {json.dumps(data)}\n")
        except Exception as e:
            logging.error(f"Error logging data: {e}")