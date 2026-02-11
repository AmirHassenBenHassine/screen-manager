"""Utility helper functions"""
import time
import psutil
import os
import subprocess

def get_device_metrics():
    """Get device performance metrics"""
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory().percent
    mem_total_gb = psutil.virtual_memory().total / (1024**3)
    uptime = time.time() - psutil.boot_time()
    
    # CPU Temperature
    try:
        temp_file = "/sys/class/thermal/thermal_zone0/temp"
        if os.path.exists(temp_file):
            with open(temp_file, 'r') as f:
                temp = int(f.read().strip()) / 1000
        else:
            temp = "N/A"
    except:
        temp = "N/A"
    
    # IP Address
    try:
        ip_addr = os.popen("hostname -I").read().strip().split()[0]
    except:
        ip_addr = "N/A"
    
    # WiFi SSID and Status
    try:
        result = subprocess.run(['nmcli', '-t', '-f', 'active,ssid', 'dev', 'wifi'],
                              capture_output=True, text=True, timeout=2)
        wifi_connected = False
        ssid = "N/A"
        for line in result.stdout.split('\n'):
            if line.startswith('yes:'):
                wifi_connected = True
                ssid = line.split(':', 1)[1].strip()
                break
        
        if wifi_connected:
            wifi_status = f"Connected: {ssid}"
        else:
            wifi_status = "Disconnected"
    except:
        wifi_status = "Unknown"
    
    # Disk Usage
    try:
        disk = psutil.disk_usage('/')
        disk_used_gb = disk.used / (1024**3)
        disk_total_gb = disk.total / (1024**3)
        disk_percent = disk.percent
    except:
        disk_used_gb = 0
        disk_total_gb = 0
        disk_percent = 0
    
    # System Load (1 minute average)
    try:
        load = os.getloadavg()[0]
        cpu_count = psutil.cpu_count()
        load_percent = (load / cpu_count) * 100
    except:
        load_percent = 0
    
    # Format uptime
    uptime_str = time.strftime('%d days %H:%M', time.gmtime(uptime))
    
    return [
        f"System load: {load_percent:.0f}%",
        f"Uptime: {uptime_str}",
        f"Memory: {mem:.0f}% of {mem_total_gb:.1f}G",
        f"IP: {ip_addr}",
        f"CPU temp: {temp}°C" if isinstance(temp, (int, float)) else f"CPU temp: {temp}",
        f"Disk: {disk_percent:.0f}% of {disk_total_gb:.0f}G",
        f"WiFi: {wifi_status}"
    ]

def update_device_metrics_loop(state):
    """Background loop to update device metrics"""
    while True:
        if not state.is_standby:
            state.device_metrics_pages = get_device_metrics()
        time.sleep(5)