"""WiFi service for network operations"""
import subprocess
import logging
import time
from config.constants import SSID_CACHE_DURATION

class WiFiService:
    def __init__(self):
        self.cached_ssid = None
        self.last_check_time = 0
    
    def get_current_ssid(self):
        """Get currently connected SSID with caching"""
        current_time = time.time()
        
        # Return cached if recent
        if self.cached_ssid is not None and \
           (current_time - self.last_check_time) < SSID_CACHE_DURATION:
            return self.cached_ssid
        
        try:
            result = subprocess.run(['nmcli', '-t', '-f', 'active,ssid', 'dev', 'wifi'],
                                  capture_output=True, text=True, timeout=1)
            for line in result.stdout.split('\n'):
                if line.startswith('yes:'):
                    ssid = line.split(':', 1)[1].strip()
                    self.cached_ssid = ssid
                    self.last_check_time = current_time
                    return ssid
            
            self.cached_ssid = None
            self.last_check_time = current_time
            return None
        
        except subprocess.TimeoutExpired:
            logging.debug("SSID check timeout, using cached")
            return self.cached_ssid
        except Exception as e:
            logging.error(f"Error getting SSID: {e}")
            return self.cached_ssid
    
    def get_saved_networks(self):
        """Get list of saved WiFi networks"""
        try:
            result = subprocess.run(['nmcli', '-t', '-f', 'NAME', 'connection', 'show'],
                                  capture_output=True, text=True, timeout=5)
            networks = [line.strip() for line in result.stdout.split('\n') if line.strip()]
            
            # Filter WiFi connections
            wifi_networks = []
            for network in networks:
                check = subprocess.run(['nmcli', '-t', '-f', 'connection.type', 
                                      'connection', 'show', network],
                                     capture_output=True, text=True, timeout=2)
                if '802-11-wireless' in check.stdout:
                    wifi_networks.append(network)
            
            return wifi_networks
        
        except Exception as e:
            logging.error(f"Error getting saved networks: {e}")
            return []
    
    def connect_to_saved_network(self, network_name):
        """Connect to a saved network"""
        try:
            result = subprocess.run(['sudo', 'nmcli', 'connection', 'up', network_name],
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logging.info(f"Connected to {network_name}")
                # Invalidate cache
                self.cached_ssid = None
                return True
            else:
                logging.error(f"Connection failed: {result.stderr}")
                return False
        
        except Exception as e:
            logging.error(f"Error connecting: {e}")
            return False
    
    def disconnect_wifi(self):
        """Disconnect and remove current WiFi"""
        try:
            current = self.get_current_ssid()
            if current:
                subprocess.run(['sudo', 'nmcli', 'connection', 'delete', current], timeout=10)
                logging.info(f"Removed {current}")
                self.cached_ssid = None
                return True
        except Exception as e:
            logging.error(f"Error disconnecting: {e}")
        return False