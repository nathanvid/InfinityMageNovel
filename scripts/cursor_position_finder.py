#!/usr/bin/env python3
"""
Cursor Position Finder for PyAutoGUI
Helps find exact mouse coordinates for automation scripts
"""

import pyautogui
import time
import sys
from datetime import datetime

class CursorPositionFinder:
    def __init__(self):
        # Disable pyautogui failsafe for this utility
        pyautogui.FAILSAFE = False
        self.positions = []
        
    def get_current_position(self):
        """Get current mouse position"""
        return pyautogui.position()
    
    def continuous_tracking(self, duration_seconds=10):
        """Track cursor position continuously"""
        print(f"🖱️ CONTINUOUS CURSOR TRACKING ({duration_seconds} seconds)")
        print("=" * 50)
        print("Move your mouse to different positions...")
        print("Press Ctrl+C to stop early")
        print("")
        
        start_time = time.time()
        last_position = None
        
        try:
            while time.time() - start_time < duration_seconds:
                current_pos = self.get_current_position()
                
                # Only print if position changed significantly
                if last_position is None or (
                    abs(current_pos.x - last_position.x) > 5 or 
                    abs(current_pos.y - last_position.y) > 5
                ):
                    elapsed = int(time.time() - start_time)
                    print(f"[{elapsed:2d}s] Position: ({current_pos.x:4d}, {current_pos.y:4d})")
                    last_position = current_pos
                
                time.sleep(0.1)  # Update 10 times per second
                
        except KeyboardInterrupt:
            print("\n⏹️ Tracking stopped by user")
    
    def click_to_capture(self, num_clicks=5):
        """Capture positions when user clicks"""
        print(f"🖱️ CLICK TO CAPTURE MODE ({num_clicks} clicks)")
        print("=" * 50)
        print("Click on different locations to capture their coordinates")
        print("Press Ctrl+C to stop early")
        print("")
        
        captured_positions = []
        
        try:
            for i in range(num_clicks):
                print(f"Click #{i+1}: Position your mouse and click anywhere...")
                
                # Wait for click
                while True:
                    if pyautogui.mouseDown():
                        # Wait for mouse button release
                        while pyautogui.mouseDown():
                            time.sleep(0.01)
                        
                        pos = self.get_current_position()
                        captured_positions.append(pos)
                        print(f"✅ Captured: ({pos.x}, {pos.y})")
                        break
                    
                    time.sleep(0.01)
                
                time.sleep(0.5)  # Brief pause between captures
                
        except KeyboardInterrupt:
            print("\n⏹️ Capture stopped by user")
        
        return captured_positions
    
    def countdown_capture(self, countdown_seconds=5, num_positions=3):
        """Capture position after countdown"""
        print(f"🖱️ COUNTDOWN CAPTURE MODE")
        print("=" * 50)
        print(f"Position your mouse, then wait for {countdown_seconds} second countdown")
        print(f"Will capture {num_positions} positions")
        print("")
        
        captured_positions = []
        
        try:
            for i in range(num_positions):
                print(f"\nPosition #{i+1}:")
                print("Position your mouse and wait...")
                
                for countdown in range(countdown_seconds, 0, -1):
                    print(f"⏰ Capturing in {countdown}...")
                    time.sleep(1)
                
                pos = self.get_current_position()
                captured_positions.append(pos)
                print(f"✅ Captured: ({pos.x}, {pos.y})")
                
                if i < num_positions - 1:
                    print("Move to next position...")
                    time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n⏹️ Capture stopped by user")
        
        return captured_positions
    
    def screen_info(self):
        """Display screen information"""
        screen_size = pyautogui.size()
        current_pos = self.get_current_position()
        
        print("🖥️ SCREEN INFORMATION")
        print("=" * 30)
        print(f"Screen Size: {screen_size.width} x {screen_size.height}")
        print(f"Current Mouse Position: ({current_pos.x}, {current_pos.y})")
        print(f"Screen Center: ({screen_size.width//2}, {screen_size.height//2})")
        print("")
        
        # Common positions
        print("📍 Common Positions:")
        print(f"Top Left: (0, 0)")
        print(f"Top Right: ({screen_size.width-1}, 0)")
        print(f"Bottom Left: (0, {screen_size.height-1})")
        print(f"Bottom Right: ({screen_size.width-1}, {screen_size.height-1})")
        print(f"Center: ({screen_size.width//2}, {screen_size.height//2})")
    
    def generate_pyautogui_code(self, positions, labels=None):
        """Generate PyAutoGUI code for captured positions"""
        if not positions:
            print("No positions to generate code for.")
            return
        
        print("\n🐍 GENERATED PYAUTOGUI CODE")
        print("=" * 40)
        print("# Copy this code into your automation script:")
        print("")
        
        for i, pos in enumerate(positions):
            label = labels[i] if labels and i < len(labels) else f"position_{i+1}"
            print(f"# {label}")
            print(f"pyautogui.click({pos.x}, {pos.y})")
            print("")
        
        # Also generate coordinate variables
        print("# Or use as variables:")
        for i, pos in enumerate(positions):
            label = labels[i] if labels and i < len(labels) else f"pos_{i+1}"
            var_name = label.lower().replace(' ', '_').replace('+', 'plus')
            print(f"{var_name}_x, {var_name}_y = {pos.x}, {pos.y}")
        
        print("")
    
    def save_positions_to_file(self, positions, filename="captured_positions.txt"):
        """Save captured positions to a file"""
        if not positions:
            return
        
        try:
            with open(filename, 'w') as f:
                f.write(f"# Cursor Positions Captured - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Screen Size: {pyautogui.size().width} x {pyautogui.size().height}\n\n")
                
                for i, pos in enumerate(positions, 1):
                    f.write(f"Position {i}: ({pos.x}, {pos.y})\n")
                
                f.write("\n# PyAutoGUI Code:\n")
                for i, pos in enumerate(positions, 1):
                    f.write(f"pyautogui.click({pos.x}, {pos.y})  # Position {i}\n")
            
            print(f"💾 Positions saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Error saving positions: {e}")

def main():
    """Main interface for cursor position finder"""
    finder = CursorPositionFinder()
    
    print("🖱️ CURSOR POSITION FINDER FOR PYAUTOGUI")
    print("=" * 60)
    
    # Show screen info first
    finder.screen_info()
    
    while True:
        print("\n📋 AVAILABLE MODES:")
        print("1. Continuous tracking (move mouse around)")
        print("2. Click to capture (click to save positions)")
        print("3. Countdown capture (position mouse, wait for countdown)")
        print("4. Show current position")
        print("5. Screen information")
        print("6. Exit")
        
        try:
            choice = input("\nSelect mode (1-6): ").strip()
            
            if choice == '1':
                duration = input("Duration in seconds (default 10): ").strip()
                duration = int(duration) if duration.isdigit() else 10
                finder.continuous_tracking(duration)
                
            elif choice == '2':
                num_clicks = input("Number of clicks to capture (default 5): ").strip()
                num_clicks = int(num_clicks) if num_clicks.isdigit() else 5
                positions = finder.click_to_capture(num_clicks)
                
                if positions:
                    # Ask for labels
                    labels = []
                    print("\n🏷️ Add labels for captured positions (optional):")
                    for i, pos in enumerate(positions):
                        label = input(f"Label for ({pos.x}, {pos.y}) [default: Position {i+1}]: ").strip()
                        labels.append(label if label else f"Position {i+1}")
                    
                    finder.generate_pyautogui_code(positions, labels)
                    
                    save = input("\n💾 Save positions to file? (y/n): ").strip().lower()
                    if save == 'y':
                        filename = input("Filename (default: captured_positions.txt): ").strip()
                        filename = filename if filename else "captured_positions.txt"
                        finder.save_positions_to_file(positions, filename)
                
            elif choice == '3':
                countdown = input("Countdown seconds (default 5): ").strip()
                countdown = int(countdown) if countdown.isdigit() else 5
                
                num_pos = input("Number of positions (default 3): ").strip()
                num_pos = int(num_pos) if num_pos.isdigit() else 3
                
                positions = finder.countdown_capture(countdown, num_pos)
                
                if positions:
                    finder.generate_pyautogui_code(positions)
                    
                    save = input("\n💾 Save positions to file? (y/n): ").strip().lower()
                    if save == 'y':
                        finder.save_positions_to_file(positions)
                
            elif choice == '4':
                pos = finder.get_current_position()
                print(f"\n📍 Current Position: ({pos.x}, {pos.y})")
                print(f"PyAutoGUI Code: pyautogui.click({pos.x}, {pos.y})")
                
            elif choice == '5':
                finder.screen_info()
                
            elif choice == '6':
                print("\n👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please select 1-6.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Exiting...")
            break
        except ValueError:
            print("❌ Please enter a valid number.")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Check if pyautogui is available
    try:
        import pyautogui
    except ImportError:
        print("❌ PyAutoGUI not found!")
        print("Install with: pip install pyautogui")
        sys.exit(1)
    
    main()