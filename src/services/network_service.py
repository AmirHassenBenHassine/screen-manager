"""Network pairing and configuration service"""
import subprocess
import logging
import time
import requests

class NetworkService:
    def __init__(self, renderer):
        self.renderer = renderer

    def _check_wifi_interface(self):
        """Check if WiFi interface is available and load if needed"""
        try:
            # Check if WiFi interface exists
            result = subprocess.run(['nmcli', 'device', 'status'],
                                  capture_output=True, text=True, timeout=5)
            
            if 'wifi' not in result.stdout:
                logging.warning("WiFi interface not found, attempting to load...")
                self.renderer.render_message("Loading WiFi\ninterface...")
                
                # Try to reload WiFi module (adjust module name if needed)
                subprocess.run(['sudo', 'modprobe','-r', 'rtw89_8852be'], 
                             capture_output=True, timeout=10)
                time.sleep(2)

                subprocess.run(['sudo', 'modprobe', 'rtw89_8852be'], 
                             capture_output=True, timeout=10)
                time.sleep(2)
                # Restart NetworkManager
                subprocess.run(['sudo', 'systemctl', 'restart', 'NetworkManager'],
                             capture_output=True, timeout=10)
                time.sleep(3)
                
                # Check again
                result = subprocess.run(['nmcli', 'device', 'status'],
                                      capture_output=True, text=True, timeout=5)
                
                if 'wifi' not in result.stdout:
                    return False
            
            return True
        except Exception as e:
            logging.error(f"Error checking WiFi interface: {e}")
            return False

    def ensure_orion_connection(self):
        """Connect to OrionSetup and wait for credentials"""
        try:
            # Check WiFi interface first
            if not self._check_wifi_interface():
                return (False, "WiFi interface not available")
            
            # Phase 1: Connect to OrionSetup (with retry logic)
            max_retries = 2
            connected = False
            
            for attempt in range(max_retries):
                if attempt > 0:
                    self.renderer.render_message(f"Retrying...\n(Attempt {attempt + 1}/{max_retries})")
                    time.sleep(2)
                
                self.renderer.render_message("Checking connection...")
                
                try:
                    result = subprocess.run(['nmcli', '-t', '-f', 'active,ssid', 'dev', 'wifi'],
                                          capture_output=True, text=True, timeout=5)
                    
                    already_connected = False
                    for line in result.stdout.split('\n'):
                        if line.startswith('yes:') and 'OrionSetup' in line:
                            already_connected = True
                            break
                    
                    if already_connected:
                        connected = True
                        break
                    
                    # Scan for networks
                    self.renderer.render_message("Scanning networks...")
                    subprocess.run(['sudo', 'nmcli', 'device', 'wifi', 'rescan'],
                                 timeout=30, stderr=subprocess.DEVNULL)
                    time.sleep(3)  # Give scan time to complete
                    
                    # List networks
                    result = subprocess.run(['nmcli', '-t', '-f', 'ssid', 'dev', 'wifi'],
                                          capture_output=True, text=True, timeout=5)
                    
                    if 'OrionSetup' not in result.stdout:
                        logging.warning(f"OrionSetup not found in scan (attempt {attempt + 1})")
                        if attempt == max_retries - 1:
                            return (False, "Energy Meter not found")
                        continue
                    
                    # Try to connect
                    self.renderer.render_message("Connecting to\nOrionSetup...")
                    
                    # Disconnect from current network first
                    subprocess.run(['sudo', 'nmcli', 'device', 'disconnect', 'wlan0'],
                                 capture_output=True, timeout=10)
                    time.sleep(1)
                    
                    connect_result = subprocess.run([
                        'sudo', 'nmcli', 'dev', 'wifi', 'connect', 'OrionSetup',
                        'password', 'Orion2025'
                    ], capture_output=True, text=True, timeout=60)
                    
                    if connect_result.returncode == 0:
                        connected = True
                        self.renderer.render_message("Connected to\nOrionSetup!")
                        time.sleep(2)
                        break
                    else:
                        logging.error(f"Connection failed (attempt {attempt + 1}): {connect_result.stderr}")
                        if attempt == max_retries - 1:
                            return (False, "Connection failed")
                
                except subprocess.TimeoutExpired:
                    logging.error(f"Network command timeout (attempt {attempt + 1})")
                    if attempt == max_retries - 1:
                        return (False, "Connection timeout")
            
            if not connected:
                return (False, "Could not connect to OrionSetup")
            
            # Phase 2: Wait for credentials with better timeout handling
            logging.info("Waiting for credentials from ESP32")
            poll_interval = 3
            poll_count = 0
            max_polls = 200  # 10 minutes max (200 * 3 seconds)
            
            while poll_count < max_polls:
                try:
                    # Check connection status (with shorter timeout to avoid blocking)
                    check_result = subprocess.run(
                        ['nmcli', '-t', '-f', 'active,ssid', 'dev', 'wifi'],
                        capture_output=True, text=True, timeout=2  # Reduced from 5
                    )
                    
                    still_connected = False
                    for line in check_result.stdout.split('\n'):
                        if line.startswith('yes:') and 'OrionSetup' in line:
                            still_connected = True
                            break
                    
                    if not still_connected:
                        logging.warning("Disconnected from OrionSetup")
                        return (False, "Lost connection to OrionSetup")
                    
                    # Poll for credentials
                    response = requests.get('http://192.168.4.1:8080/credentials', timeout=3)
                    
                    if response.status_code == 200:
                        data = response.json()
                        ssid = data.get('ssid')
                        password = data.get('password')
                        validated = data.get('validated', False)
                        
                        if ssid and validated:
                            logging.info(f"Received credentials: {ssid}")
                            self.renderer.render_message(f"Received:\n{ssid}\n\nConnecting...")
                            time.sleep(1)
                            
                            # Phase 3: Connect to new WiFi
                            # Delete old connection
                            subprocess.run(['sudo', 'nmcli', 'connection', 'delete', ssid],
                                         capture_output=True, check=False)
                            time.sleep(0.5)
                            
                            connect_result = subprocess.run([
                                'sudo', 'nmcli', 'dev', 'wifi', 'connect', ssid,
                                'password', password
                            ], capture_output=True, text=True, timeout=60)
                            
                            if connect_result.returncode == 0:
                                self.renderer.render_message(f"Connected to\n{ssid}!")
                                time.sleep(2)
                                return (True, "✅ Pairing complete!")
                            else:
                                logging.error(f"Connection failed: {connect_result.stderr}")
                                # Reconnect to OrionSetup
                                subprocess.run(['sudo', 'nmcli', 'dev', 'wifi', 'connect',
                                              'OrionSetup', 'password', 'Orion2025'],
                                             capture_output=True, timeout=30)
                                return (False, "Connection failed")
                
                except subprocess.TimeoutExpired:
                    # Log but don't spam - this is expected during waiting
                    if poll_count % 20 == 0:  # Log every minute
                        logging.debug(f"Still waiting for credentials ({poll_count * poll_interval}s elapsed)")
                except requests.exceptions.Timeout:
                    pass  # Expected - ESP32 hasn't served credentials yet
                except requests.exceptions.ConnectionError:
                    pass  # Expected - HTTP server not ready yet
                except Exception as e:
                    logging.error(f"Poll error: {e}")
                
                # Update UI periodically
                poll_count += 1
                if poll_count % 5 == 0:  # Every 15 seconds
                    elapsed_mins = (poll_count * poll_interval) // 60
                    # Optional: show waiting message
                    # self.renderer.render_message(f"Waiting...\n{elapsed_mins} min")
                
                time.sleep(poll_interval)
            
            return (False, "Timeout waiting for credentials")
        
        except Exception as e:
            logging.error(f"Error: {e}", exc_info=True)
            return (False, "Unexpected error")
        """Connect to OrionSetup and wait for credentials"""
        try:
            # Check WiFi interface first
            if not self._check_wifi_interface():
                return (False, "WiFi interface not available")
            
            # Phase 1: Connect to OrionSetup (with retry logic)
            max_retries = 2
            connected = False
            
            for attempt in range(max_retries):
                if attempt > 0:
                    self.renderer.render_message(f"Retrying...\n(Attempt {attempt + 1}/{max_retries})")
                    time.sleep(2)

            self.renderer.render_message("Checking connection...")
            result = subprocess.run(['nmcli', '-t', '-f', 'active,ssid', 'dev', 'wifi'],
                                  capture_output=True, text=True, timeout=5)
            
            already_connected = False
            for line in result.stdout.split('\n'):
                if line.startswith('yes:') and 'OrionSetup' in line:
                    already_connected = True
                    break
            
            if not already_connected:
                self.renderer.render_message("Scanning networks...")
                subprocess.run(['sudo', 'nmcli', 'device', 'wifi', 'rescan'],
                             timeout=30, stderr=subprocess.DEVNULL)
                time.sleep(2)
                
                result = subprocess.run(['nmcli', '-t', '-f', 'ssid', 'dev', 'wifi'],
                                      capture_output=True, text=True, timeout=5)
                
                if 'OrionSetup' not in result.stdout:
                    return (False, "Energy Meter not found")
                
                self.renderer.render_message("Connecting to\nOrionSetup...")
                connect_result = subprocess.run([
                    'sudo', 'nmcli', 'dev', 'wifi', 'connect', 'OrionSetup',
                    'password', 'Orion2025'
                ], capture_output=True, text=True, timeout=60)
                
                if connect_result.returncode != 0:
                    return (False, "Connection failed")
                
                self.renderer.render_message("Connected to\nOrionSetup!")
                time.sleep(2)
            
            # Phase 2: Wait for credentials
            logging.info("Waiting for credentials from ESP32")
            poll_interval = 3
            poll_count = 0
            
            while True:
                try:
                    # Verify still connected
                    check_result = subprocess.run(
                        ['nmcli', '-t', '-f', 'active,ssid', 'dev', 'wifi'],
                        capture_output=True, text=True, timeout=5
                    )
                    
                    still_connected = False
                    for line in check_result.stdout.split('\n'):
                        if line.startswith('yes:') and 'OrionSetup' in line:
                            still_connected = True
                            break
                    
                    if not still_connected:
                        return (False, "Lost connection to OrionSetup")
                    
                    # Poll for credentials
                    response = requests.get('http://192.168.4.1:8080/credentials', timeout=3)
                    
                    if response.status_code == 200:
                        data = response.json()
                        ssid = data.get('ssid')
                        password = data.get('password')
                        validated = data.get('validated', False)
                        
                        if ssid and validated:
                            logging.info(f"Received credentials: {ssid}")
                            self.renderer.render_message(f"Received:\n{ssid}\n\nConnecting...")
                            time.sleep(1)
                            
                            # Phase 3: Connect to new WiFi
                            subprocess.run(['sudo', 'nmcli', 'connection', 'delete', ssid],
                                         capture_output=True, check=False)
                            time.sleep(0.5)
                            
                            connect_result = subprocess.run([
                                'sudo', 'nmcli', 'dev', 'wifi', 'connect', ssid,
                                'password', password
                            ], capture_output=True, text=True, timeout=60)
                            
                            if connect_result.returncode == 0:
                                self.renderer.render_message(f"Connected to\n{ssid}!")
                                time.sleep(2)
                                return (True, "✅ Pairing complete!")
                            else:
                                logging.error(f"Connection failed: {connect_result.stderr}")
                                subprocess.run(['sudo', 'nmcli', 'dev', 'wifi', 'connect',
                                              'OrionSetup', 'password', 'Orion2025'],
                                             capture_output=True, timeout=30)
                                return (False, "Connection failed")
                
                except requests.exceptions.Timeout:
                    pass
                except requests.exceptions.ConnectionError:
                    pass
                except Exception as e:
                    logging.error(f"Poll error: {e}")
                
                poll_count += 1
                time.sleep(poll_interval)
        
        except Exception as e:
            logging.error(f"Error: {e}", exc_info=True)
            return (False, "Unexpected error")