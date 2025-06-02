import ctypes
import win32gui, win32process
import psutil

def play_pause_spotfy():
    ctypes.windll.user32.keybd_event(0xB3, 0, 0, 0)  # key down
    ctypes.windll.user32.keybd_event(0xB3, 0, 2, 0)
    # key up


def get_spotify_status():
    # This function will return a list of active window titles along with their corresponding process names
    def enum_handler(hwnd, result):
        title = win32gui.GetWindowText(hwnd)  # Get window title
        if title:  # Only consider windows with titles
            pid = win32process.GetWindowThreadProcessId(hwnd)[1]  # Get process ID from window handle
            try:
                # Use psutil to get the process name from PID
                proc = psutil.Process(pid)
                process_name = proc.name()
                result.append((title, process_name))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                result.append((title, "Access Denied"))

    windows = []
    win32gui.EnumWindows(enum_handler, windows)  # Enumerate all open windows and retrieve their process names

    # for title, process_name in windows:
    #     if(process_name == "Spotify.exe"):
    #         print(f"Window Title: {title} | Process Name: {process_name}")

    for title, process_name in windows:
        # print(f"Window Title: {title} | Process Name: {process_name}")
        if process_name.lower() == "spotify.exe":
            if "-" in title:
                return f"{title}"
            elif title == "Spotify" or title == "Spotify Premium":
                return "Spotify - Paused"
            elif title in ["GDI+ Window", "Default IME", "MSCTFIME UI", "GDI+", "Spotify.exe"]:
                continue
            else:
                continue
    return "Spotify Not Running"  # to do, launch spotify