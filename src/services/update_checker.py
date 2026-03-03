"""Update checker service"""
import subprocess
import logging
import threading
import time
import os

class UpdateChecker:
    def __init__(self, state, check_interval=3600):
        """
        Initialize update checker
        
        Args:
            state: Application state
            check_interval: Seconds between update checks (default: 1 hour)
        """
        self.state = state
        self.check_interval = check_interval
        self.current_version = self._get_current_version()
        self.latest_version = None
        self.update_available = False
        self.checking = False
        self.last_check_time = 0
        
        # Start background checker
        self.checker_thread = threading.Thread(target=self._check_loop, daemon=True)
        self.checker_thread.start()
    
    def _get_current_version(self):
        """Get current installed version"""
        version_file = "/home/orangepi/screen-manager2/.version"
        try:
            if os.path.exists(version_file):
                with open(version_file, 'r') as f:
                    return f.read().strip()
            else:
                # If no version file, try git
                result = subprocess.run(
                    ['git', '-C', '/home/orangepi/screen-manager2', 'rev-parse', '--short', 'HEAD'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    return result.stdout.strip()
        except Exception as e:
            logging.error(f"Error getting current version: {e}")
        
        return "unknown"
    
    def _get_remote_version(self):
        """Get latest version from remote repository"""
        try:
            # Fetch latest from remote without pulling
            result = subprocess.run(
                ['git', '-C', '/home/orangepi/screen-manager2', 'fetch', 'origin'],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode != 0:
                logging.warning(f"Git fetch failed: {result.stderr}")
                return None
            
            # Get remote HEAD hash
            result = subprocess.run(
                ['git', '-C', '/home/orangepi/screen-manager2', 'rev-parse', '--short', 'origin/main'],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
        
        except Exception as e:
            logging.error(f"Error getting remote version: {e}")
        
        return None
    
    def check_for_updates(self):
        """Check if updates are available"""
        if self.checking:
            return False
        
        self.checking = True
        logging.info("Checking for updates...")
        
        try:
            self.latest_version = self._get_remote_version()
            
            if self.latest_version and self.latest_version != self.current_version:
                self.update_available = True
                self.state.update_available = True
                logging.info(f"Update available: {self.current_version} -> {self.latest_version}")
                return True
            else:
                self.update_available = False
                self.state.update_available = False
                logging.info("No updates available")
                return False
        
        finally:
            self.checking = False
            self.last_check_time = time.time()
    
    def _check_loop(self):
        """Background loop to check for updates periodically"""
        # Wait 60 seconds before first check (let app initialize)
        time.sleep(60)
        
        while True:
            try:
                if not self.state.is_standby:
                    self.check_for_updates()
            except Exception as e:
                logging.error(f"Update check error: {e}")
            
            # Wait for next check
            time.sleep(self.check_interval)
    
    def perform_update(self):
        """Perform update using ansible-pull"""
        logging.info("Starting update process...")
        
        try:
            # Run ansible-pull
            # Adjust the playbook path and git URL to match your setup
            result = subprocess.run([
                'ansible-pull',
                '-U', ' https://github.com/ORION-DEVELOPMENT-DIONE/update-manager.git',  # Your ansible repo
                '-i', 'localhost,',
                'playbook.yml',
                '--tags', 'screen-manager'
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logging.info("Update completed successfully")
                # Update version file
                self.current_version = self._get_current_version()
                self.update_available = False
                self.state.update_available = False
                return (True, "Update successful!\nRestarting...")
            else:
                logging.error(f"Update failed: {result.stderr}")
                return (False, "Update failed")
        
        except subprocess.TimeoutExpired:
            logging.error("Update timed out")
            return (False, "Update timeout")
        except Exception as e:
            logging.error(f"Update error: {e}")
            return (False, f"Update error: {str(e)}")
    
    def get_update_info(self):
        """Get update information for display"""
        return {
            'current': self.current_version,
            'latest': self.latest_version,
            'available': self.update_available,
            'last_check': self.last_check_time
        }