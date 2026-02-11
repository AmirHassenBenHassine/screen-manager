"""WiFi menu rendering and handling"""
import time
import logging
from PIL import ImageDraw  
from ui.renderer import BaseRenderer
from config.constants import *
from config.themes import WIFI_MENU_EMOJIS

class WiFiMenu(BaseRenderer):
    def __init__(self, display, state, wifi_service):
        super().__init__(display, state)
        self.wifi_service = wifi_service
        self.options = ["Pair Devices", "Change WiFi", "Saved Networks", "Remove WiFi"]
    
    def render(self):
        """Render WiFi setup menu"""
        image = self.get_background()
        draw = ImageDraw.Draw(image)
        
        height = len(self.options) * 40
        y_start = (SCREEN_HEIGHT - height) // 2
        
        for i, item in enumerate(self.options):
            is_selected = (i == self.state.wifi_selected)
            color = self.get_selected_color() if is_selected else self.get_text_color()
            
            emoji = WIFI_MENU_EMOJIS.get(item, '')
            emoji_x = 40
            text_x = emoji_x + 30
            y_pos = y_start + i * 40
            
            # Draw emoji
            draw.text((emoji_x, y_pos), emoji, fill=color, font=self.get_font())
            # Draw text
            draw.text((text_x, y_pos), item, fill=color, font=self.get_font())
        
        self.display.show_image(image)
        del draw
        del image
    
    def render_saved_networks(self):
        """Render saved networks list with scrolling"""
        current_time = time.time()
        
        # Throttle rendering
        if current_time - self.state.last_render_time < RENDER_THROTTLE:
            return True
        
        self.state.last_render_time = current_time
        
        if not self.state.saved_networks_list:
            self.state.saved_networks_list = self.wifi_service.get_saved_networks()
            self.state.saved_networks_selected = 0
        
        if not self.state.saved_networks_list:
            self.render_message("No saved\nnetworks found")
            time.sleep(2)
            return False
        
        image = self.get_background()
        draw = ImageDraw.Draw(image)
        
        # Title
        title = "Saved Networks"
        title_font = self.get_font(18)
        title_w = title_font.getlength(title)
        draw.text(((SCREEN_WIDTH - title_w) // 2, 30), title, 
                 fill=self.get_selected_color(), font=title_font)
        
        # Get current SSID
        current = self.wifi_service.get_current_ssid()
        
        network_font = self.get_font(20)
        display_count = 4
        item_spacing = 32
        
        start_idx = max(0, self.state.saved_networks_selected - 1)
        end_idx = min(len(self.state.saved_networks_list), start_idx + display_count)
        
        y_start = 60
        current_y = y_start
        
        selected_network = self.state.saved_networks_list[self.state.saved_networks_selected]
        
        # Reset scroll if selection changed
        if selected_network != self.state.last_selected_network:
            self.state.scroll_offset = 0
            self.state.last_scroll_time = current_time
            self.state.last_selected_network = selected_network
        
        # Render networks
        for i in range(start_idx, end_idx):
            network = self.state.saved_networks_list[i]
            is_current = (current is not None and network == current)
            is_selected = (i == self.state.saved_networks_selected)
            
            color = self.get_selected_color() if is_selected else self.get_text_color()
            
            if is_selected:
                text = self._get_scrolling_text(network, is_current, current_time)
            else:
                prefix = "  "
                suffix = " ✓" if is_current else ""
                display_name = network[:17] if len(network) > 17 else network
                text = f"{prefix}{display_name}{suffix}"
            
            draw.text((10, current_y), text, fill=color, font=network_font)
            current_y += item_spacing
        
        # Scroll indicators
        if len(self.state.saved_networks_list) > display_count:
            scroll_font = self.get_font(14)
            scroll_text = "▲▼"
            scroll_w = scroll_font.getlength(scroll_text)
            draw.text(((SCREEN_WIDTH - scroll_w) // 2, 190), scroll_text, 
                     fill=self.get_selected_color(), font=scroll_font)
        
        # Instructions
        instruction_font = self.get_font(14)
        instruction_text = "Tap=Connect"
        instruction_w = instruction_font.getlength(instruction_text)
        draw.text(((SCREEN_WIDTH - instruction_w) // 2, 210), instruction_text, 
                 fill="gray", font=instruction_font)
        
        self.display.show_image(image)
        del draw
        del image
        return True
    
    def _get_scrolling_text(self, network, is_current, current_time):
        """Get scrolling text for selected network"""
        prefix = "➤ "
        suffix = " ✓" if is_current else ""
        max_chars = 18
        
        if len(network) > max_chars:
            # Scrolling text
            display_network = network + "  ...  " + network[:10]
            
            if current_time - self.state.last_scroll_time > SCROLL_SPEED:
                self.state.scroll_offset = (self.state.scroll_offset + 1) % (len(network) + 7)
                self.state.last_scroll_time = current_time
            
            visible_text = display_network[self.state.scroll_offset:self.state.scroll_offset + max_chars]
            return prefix + visible_text + suffix
        else:
            self.state.scroll_offset = 0
            return prefix + network + suffix
    
    def render_network_confirmation(self):
        """Render network connection confirmation dialog"""
        current_time = time.time()
        network_name = self.state.network_to_connect
        
        image = self.get_background()
        draw = ImageDraw.Draw(image)
        
        # Message
        msg_font = self.get_font(18)
        msg1 = "Connect to:"
        msg1_w = msg_font.getlength(msg1)
        draw.text(((SCREEN_WIDTH - msg1_w) // 2, 30), msg1, 
                 fill=self.get_text_color(), font=msg_font)
        
        # Network name with scrolling
        net_font = self.get_font(18)
        max_chars = 20
        
        # Reset scroll if new network
        if network_name != self.state.last_selected_network:
            self.state.scroll_offset = 0
            self.state.last_scroll_time = current_time
            self.state.last_selected_network = network_name
        
        if len(network_name) > max_chars:
            display_network = network_name + "  ...  " + network_name[:10]
            
            if current_time - self.state.last_scroll_time > SCROLL_SPEED:
                self.state.scroll_offset = (self.state.scroll_offset + 1) % (len(network_name) + 7)
                self.state.last_scroll_time = current_time
            
            network_display = display_network[self.state.scroll_offset:self.state.scroll_offset + max_chars]
        else:
            network_display = network_name
            self.state.scroll_offset = 0
        
        net_w = net_font.getlength(network_display)
        draw.text(((SCREEN_WIDTH - net_w) // 2, 55), network_display, 
                 fill=self.get_selected_color(), font=net_font)
        
        # Question mark
        msg2 = "?"
        msg2_w = msg_font.getlength(msg2)
        draw.text(((SCREEN_WIDTH - msg2_w) // 2, 80), msg2, 
                 fill=self.get_text_color(), font=msg_font)
        
        # Buttons
        self._draw_yes_no_buttons(draw)
        
        self.display.show_image(image)
        del draw
        del image
    
    def _draw_yes_no_buttons(self, draw):
        """Draw Yes/No confirmation buttons"""
        box_w, box_h = 90, 50
        box_y = 130
        spacing = 20
        total_width = 2 * box_w + spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        # NO box
        draw.rectangle([start_x, box_y, start_x + box_w, box_y + box_h], 
                      outline=self.get_text_color(), width=2)
        no_text = "No"
        no_w = self.get_font().getlength(no_text)
        draw.text((start_x + (box_w - no_w) // 2, box_y + 12), no_text, 
                 fill=self.get_text_color(), font=self.get_font())
        
        # YES box
        draw.rectangle([start_x + box_w + spacing, box_y, 
                       start_x + 2 * box_w + spacing, box_y + box_h], 
                      outline=self.get_selected_color(), width=2)
        yes_text = "Yes"
        yes_w = self.get_font().getlength(yes_text)
        draw.text((start_x + box_w + spacing + (box_w - yes_w) // 2, box_y + 12), 
                 yes_text, fill=self.get_selected_color(), font=self.get_font())
    
    def render_qr_code(self):
        """Render WiFi configuration QR code"""
        import qrcode
        
        url = "http://orion.local:3000"
        qr = qrcode.make(url)
        
        image = self.get_background()
        
        qr_size = 160
        qr_resized = qr.resize((qr_size, qr_size))
        qr_x = (SCREEN_WIDTH - qr_size) // 2
        qr_y = 20
        image.paste(qr_resized, (qr_x, qr_y))
        
        draw = ImageDraw.Draw(image)
        url_font = self.get_font(16)
        url_w = url_font.getlength(url)
        url_x = (SCREEN_WIDTH - url_w) // 2
        url_y = qr_y + qr_size + 10
        
        draw.text((url_x, url_y), url, fill=self.get_selected_color(), font=url_font)
        
        self.display.show_image(image)
        del draw
        del image
    
    def handle_gesture(self, gesture, touch_device=None):
        """Handle WiFi menu gestures"""
        # Handle saved networks mode
        if self.state.in_saved_networks_mode:
            return self._handle_saved_networks_gesture(gesture)
        
        # Handle QR code mode
        if self.state.in_wifi_qr_mode:
            return self._handle_qr_mode_gesture(gesture)
        
        # Normal WiFi menu navigation
        if gesture == GESTURE_UP:
            self.state.wifi_selected = (self.state.wifi_selected - 1) % len(self.options)
            self.render()
        elif gesture == GESTURE_DOWN:
            self.state.wifi_selected = (self.state.wifi_selected + 1) % len(self.options)
            self.render()
        elif gesture == GESTURE_TAP:
            return self._handle_wifi_selection()
        elif gesture in [GESTURE_LEFT, GESTURE_LONG_PRESS]:
            return MENU_MAIN
        
        return None
    
    def _handle_saved_networks_gesture(self, gesture):
        """Handle gestures in saved networks mode"""
        if gesture == 0:
            return None
        elif gesture == GESTURE_UP:
            self.state.saved_networks_selected = \
                (self.state.saved_networks_selected - 1) % len(self.state.saved_networks_list)
            self.render_saved_networks()
        elif gesture == GESTURE_DOWN:
            self.state.saved_networks_selected = \
                (self.state.saved_networks_selected + 1) % len(self.state.saved_networks_list)
            self.render_saved_networks()
        elif gesture == GESTURE_TAP:
            self.state.network_to_connect = self.state.saved_networks_list[self.state.saved_networks_selected]
            self.state.in_saved_networks_mode = False
            return MENU_CONFIRM_NETWORK
        elif gesture in [GESTURE_LEFT, GESTURE_LONG_PRESS]:
            self.state.in_saved_networks_mode = False
            self.state.saved_networks_list = []
            return MENU_WIFI
        
        return None
    
    def _handle_qr_mode_gesture(self, gesture):
        """Handle gestures in QR code mode"""
        if gesture == GESTURE_LEFT:
            self.state.in_wifi_qr_mode = False
            return MENU_WIFI
        return None
    
    def _handle_wifi_selection(self):
        """Handle WiFi menu selection"""
        time.sleep(0.1)
        
        if self.state.wifi_selected == 0:  # Pair Devices
            self._handle_pair_devices()
            return None
        elif self.state.wifi_selected == 1:  # Change WiFi
            self._handle_change_wifi()
            return None
        elif self.state.wifi_selected == 2:  # Saved Networks
            self.state.in_saved_networks_mode = True
            self.state.saved_networks_list = self.wifi_service.get_saved_networks()
            self.state.saved_networks_selected = 0
            if not self.render_saved_networks():
                self.state.in_saved_networks_mode = False
            time.sleep(0.2)
            return None
        elif self.state.wifi_selected == 3:  # Remove WiFi
            self._handle_remove_wifi()
            return None
    
    def _handle_pair_devices(self):
        """Handle device pairing"""
        from services.network_service import NetworkService
        
        self.render_loading_animation("Pairing", 2)
        network_service = NetworkService(self)
        success, message = network_service.ensure_orion_connection()
        self.render_message(message)
        time.sleep(2)
        self.render()
    
    def _handle_change_wifi(self):
        """Handle WiFi change"""
        from services.network_service import NetworkService
        
        self.render_message("Triggering\nAP mode...")
        self.render_loading_animation("Switching", 8)
        network_service = NetworkService(self)
        success, message = network_service.ensure_orion_connection()
        self.render_message(message)
        time.sleep(2)
        self.render()
    
    def _handle_remove_wifi(self):
        """Handle WiFi removal"""
        current = self.wifi_service.get_current_ssid()
        if current:
            self.render_message(f"Removing\n{current}...")
            if self.wifi_service.disconnect_wifi():
                self.render_message("✅ WiFi removed")
            else:
                self.render_message("❌ Failed to\nremove")
        else:
            self.render_message("No active\nconnection")
        time.sleep(2)
        self.render()
    
    def render_loading_animation(self, message, duration=3):
        """Show animated loading message"""
        start_time = time.time()
        dots = 0
        
        while time.time() - start_time < duration:
            dot_str = "." * (dots % 4)
            self.render_message(f"{message}{dot_str}")
            time.sleep(0.5)
            dots += 1
    
    def handle_confirmation_gesture(self, gesture, touch_device):
        """Handle network confirmation gestures"""
        if gesture == 0:
            return None
        
        if gesture == GESTURE_LONG_PRESS:
            self.state.in_saved_networks_mode = True
            return MENU_WIFI
        
        if gesture == GESTURE_TAP:
            touch_device.get_point()
            x, y = touch_device.X_point, touch_device.Y_point
            
            box_w, box_h = 90, 50
            box_y = 130
            spacing = 20
            start_x = (SCREEN_WIDTH - (2 * box_w + spacing)) // 2
            
            # NO box
            if start_x <= x <= start_x + box_w and box_y <= y <= box_y + box_h:
                self.state.in_saved_networks_mode = True
                time.sleep(0.2)
                return MENU_WIFI
            # YES box
            elif start_x + box_w + spacing <= x <= start_x + 2 * box_w + spacing and \
                 box_y <= y <= box_y + box_h:
                if self.wifi_service.connect_to_saved_network(self.state.network_to_connect):
                    self.render_message("✅ Connected")
                else:
                    self.render_message("❌ Failed")
                time.sleep(2)
                self.state.in_saved_networks_mode = False
                self.state.saved_networks_list = []
                return MENU_WIFI
        
        return None