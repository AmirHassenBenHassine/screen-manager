#!/usr/bin/env python3
"""Test update notification"""
import sys
import os

# Add parent to path
sys.path.insert(0, '/home/orangepi/screen-manager2/src')

from utils.state import state

# Force update notification
state.update_available = True
print("✅ Update notification enabled!")
print(f"State: {state.update_available}")
