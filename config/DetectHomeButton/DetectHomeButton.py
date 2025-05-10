import pygame
import threading
import time
import pygetwindow as gw
import win32gui
import win32con
import os
import pyautogui
import ctypes


def move_mouse_bottom_left():
    screen_width = ctypes.windll.user32.GetSystemMetrics(0)  # Get screen width
    screen_height = ctypes.windll.user32.GetSystemMetrics(1)  # Get screen height
    
    # Move mouse to (0, screen_height - 1) (bottom-left corner)
    ctypes.windll.user32.SetCursorPos(0, screen_height - 1)


# Hide Pygame support prompt
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
#ignore mouse corner warning
pyautogui.FAILSAFE = False
move_mouse_bottom_left()

def bring_window_to_front(window_title):
    try:
        pyautogui.hotkey('win', 'd')  # Press Windows + D to show desktop
        window = gw.getWindowsWithTitle(window_title)[0]
        hwnd = window._hWnd

        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # Restore if minimized
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)  
        win32gui.SetForegroundWindow(hwnd)  # Bring to front
        move_mouse_bottom_left()

        print(f"Window '{window_title}' brought to focus.")
    except IndexError:
        print(f"No window found with the title '{window_title}'")
        print("Launching emulator...")
        # Get the directory of the currently running script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bat_file = f"{script_dir}\\Emulator.lnk"
        os.system(f'start "" {bat_file}')
        move_mouse_bottom_left()
    except Exception as e:
        print(e)

def joystick_listener():
    pygame.init()
    pygame.joystick.init()

    joysticks = {}  # Dictionary to track connected joysticks

    while True:
        # Detect new joysticks
        for i in range(pygame.joystick.get_count()):
            if i not in joysticks:  # Only initialize if it's a new joystick
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                joysticks[i] = joystick
                print(f"Joystick {i} connected: {joystick.get_name()}")

        # Remove disconnected joysticks
        connected_ids = set(range(pygame.joystick.get_count()))
        for j_id in list(joysticks.keys()):
            if j_id not in connected_ids:
                print(f"Joystick {j_id} disconnected: {joysticks[j_id].get_name()}")
                del joysticks[j_id]

        # Process joystick events
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                print(f"Button {event.button} pressed on Joystick {event.joy}")
                if event.button == 10:  # Xbox Guide Button
                    print("Guide Button pressed")
                    #if window focused != "XMBEMulator" go through processes dictionary and try to focus the last opened process
                    bring_window_to_front("XMBEmulator")

        time.sleep(1)  # Reduce CPU usage

def start_listener():
    listener_thread = threading.Thread(target=joystick_listener, daemon=True)
    listener_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    start_listener()
