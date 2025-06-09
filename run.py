import os, sys, random, math, time, json, datetime, threading
import ctypes
import subprocess
import psutil
from set_all_packages import set_all_packages
from spotify_controls import get_spotify_status, play_pause_spotfy
import pygame.gfxdraw
import json
# Ensure required modules are available
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"


def load_theme_json():
    root_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of this script
    theme_path = os.path.join(root_dir, "themes.json")

    if not os.path.exists(theme_path):
        raise FileNotFoundError(f"themes.json not found at: {theme_path}")

    with open(theme_path, "r") as f:
        themes = json.load(f)

    return themes


def load_menu_json():
    root_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of this script
    theme_path = os.path.join(root_dir, "menu_options.json")

    if not os.path.exists(theme_path):
        raise FileNotFoundError(f"menu_options.json not found at: {theme_path}")

    with open(theme_path, "r") as f:
        themes = json.load(f)

    return themes


def focus_window_by_pid(target_pid):
    def enum_handler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid == target_pid:
                # Restore window if minimized
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                # Bring to foreground
                win32gui.SetForegroundWindow(hwnd)
                return False  # Stop enumeration
            return None
        return None

    win32gui.EnumWindows(enum_handler, None)


def move_mouse_bottom_left():
    screen_width = ctypes.windll.user32.GetSystemMetrics(0)  # Get screen width
    screen_height = ctypes.windll.user32.GetSystemMetrics(1)  # Get screen height
    
    # Move mouse to (0, screen_height - 1) (bottom-left corner)
    ctypes.windll.user32.SetCursorPos(0, screen_height - 1)

# Hide Pygame support prompt
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'


def get_pid_by_exe_name(exe_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] and proc.info['name'].lower() == exe_name.lower():
            return proc.info['pid']
    return None


def get_shortcut_target(path):
    if path.endswith('.url'): #if the shortcut is a steam game then return steam ... to later kill steam and its children processes
        return "steam.exe"  # Returning steam.exe for simplicity
    else:
        pass
        #print(path + " is tha path")

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(path)
    #print(shortcut.Targetpath)
    return shortcut.Targetpath


def displayAlert(message,time):
    # Display alert
    font = pygame.font.SysFont(None, 24)
    alert_text = font.render(message, True, (255, 255, 255))
    alert_bg = pygame.Surface((alert_text.get_width() + 20, alert_text.get_height() + 20))
    alert_bg.fill((0, 0, 0))
    alert_bg.set_alpha(200)

    alert_rect = alert_bg.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 100))
    screen.blit(alert_bg, alert_rect)
    screen.blit(alert_text, alert_text.get_rect(center=alert_rect.center))
    pygame.display.flip()
    pygame.time.wait(time * 1000)  # Show message for 2 seconds


def is_another_instance_running(script_name):
    current_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Check if the process is different and the script is in the command line arguments
            if proc.info['pid'] != current_pid and proc.info['cmdline']:
                if script_name in proc.info['cmdline']:
                    print(script_name)
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False



# Helper to get theme by name
def get_theme_by_name(name, themes):
    for theme in themes:
        if theme.get("name") == name:
            return theme
    return themes[0]  # fallback to default if not found


def create_gradient_surface(width, height, start_color, end_color):
    """Create a diagonal gradient surface."""
    gradient_surface = pygame.Surface((width, height))
    for x in range(width):
        for y in range(height):
            # Interpolate colors based on the reversed diagonal position
            t = (x / width + (height - y) / height) / 2  # Reverse the vertical gradient direction
            r = int(start_color[0] + (end_color[0] - start_color[0]) * t)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * t)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * t)
            gradient_surface.set_at((x, y), (r, g, b))
    return gradient_surface


def show_color_modal(screen, settings_file, current_theme, themes):
    pygame.joystick.init()
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

    FONT = pygame.font.SysFont('Arial', 24)
    BLACK = (0, 0, 0)
    GRAY = (150, 150, 150)
    GRAY_BORDER = (150, 150, 150, 115)
    MODAL_BG = (255, 255, 255, 160)

    COLOR_OPTIONS = [theme["name"] for theme in themes]

    def draw_text(surface, text, pos, color=BLACK):
        label = FONT.render(text, True, color)
        surface.blit(label, pos)

    def blur_surface(surface, scale_factor=0.015):
        size = surface.get_size()
        small = pygame.transform.smoothscale(surface, (int(size[0]*scale_factor), int(size[1]*scale_factor)))
        return pygame.transform.smoothscale(small, size)

    clock = pygame.time.Clock()
    screen_width, screen_height = screen.get_size()
    modal_width = int(screen_width * 0.6)
    modal_height = int(screen_height * 0.45)
    modal_x = (screen_width - modal_width) // 2
    modal_y = (screen_height - modal_height) // 2

    modal_rect = pygame.Rect(modal_x, modal_y, modal_width, modal_height)
    selected_color_index = COLOR_OPTIONS.index(current_theme["name"])

    label_pos = (modal_x + 30, modal_y + 30)
    dropdown_rect = pygame.Rect(label_pos[0] + 150, label_pos[1], 180, 35)
    apply_btn = pygame.Rect(dropdown_rect.right + 20, label_pos[1], 100, 35)
    close_btn = pygame.Rect(apply_btn.right + 20, label_pos[1], 100, 35)

    dropdown_open = False
    focus_index = 0  # 0: dropdown, 1: apply, 2: close
    dropdown_option_focus = selected_color_index

    snapshot = screen.copy()
    blurred_bg = blur_surface(snapshot)

    running = True
    dpad_cooldown = 0

    while running:
        clock.tick(60)
        if dpad_cooldown > 0:
            dpad_cooldown -= 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.JOYBUTTONDOWN:
                # A button
                if event.button == 0:
                    if focus_index == 0:  # Dropdown
                        if dropdown_open:
                            selected_color_index = dropdown_option_focus
                            dropdown_open = False
                        else:
                            dropdown_open = True
                            dropdown_option_focus = selected_color_index
                    elif focus_index == 1:  # Apply
                        selected_name = COLOR_OPTIONS[selected_color_index]
                        current_theme = get_theme_by_name(selected_name, themes)
                        with open(settings_file, "r") as f:
                            settings = json.load(f)
                        settings["saved_theme"] = selected_name
                        with open(settings_file, "w") as f:
                            json.dump(settings, f, indent=2)
                        print(f"Saved theme {selected_name}")
                    elif focus_index == 2:  # Close
                        running = False

            elif event.type == pygame.JOYHATMOTION:
                if dpad_cooldown == 0:
                    hat_x, hat_y = event.value
                    if dropdown_open:
                        if hat_y == 1:  # Up
                            dropdown_option_focus = (dropdown_option_focus - 1) % len(COLOR_OPTIONS)
                        elif hat_y == -1:  # Down
                            dropdown_option_focus = (dropdown_option_focus + 1) % len(COLOR_OPTIONS)
                    else:
                        if hat_x == 1:  # Right
                            focus_index = (focus_index + 1) % 3
                        elif hat_x == -1:  # Left
                            focus_index = (focus_index - 1) % 3
                    dpad_cooldown = 10  # debounce

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if close_btn.collidepoint(event.pos):
                    running = False
                elif dropdown_rect.collidepoint(event.pos):
                    dropdown_open = not dropdown_open
                elif dropdown_open:
                    for i, option in enumerate(COLOR_OPTIONS):
                        option_rect = pygame.Rect(dropdown_rect.x, dropdown_rect.y + 40 + i * 30, dropdown_rect.width, 30)
                        if option_rect.collidepoint(event.pos):
                            selected_color_index = i
                            dropdown_open = False
                elif apply_btn.collidepoint(event.pos):
                    selected_name = COLOR_OPTIONS[selected_color_index]
                    current_theme = get_theme_by_name(selected_name, themes)
                    with open(settings_file, "r") as f:
                        settings = json.load(f)
                    settings["saved_theme"] = selected_name
                    with open(settings_file, "w") as f:
                        json.dump(settings, f, indent=2)
                    print(f"Saved theme {selected_name}")

        # Draw blurred background
        screen.blit(blurred_bg, (0, 0))

        # Modal box
        modal_surface = pygame.Surface((modal_width, modal_height), pygame.SRCALPHA)
        modal_surface.fill(MODAL_BG)
        pygame.draw.rect(modal_surface, GRAY_BORDER, modal_surface.get_rect(), width=4, border_radius=20)
        screen.blit(modal_surface, (modal_x, modal_y))

        draw_text(screen, "Choose color", label_pos)

        # Dropdown
        pygame.draw.rect(screen, (200, 255, 200) if focus_index == 0 else (255, 255, 255), dropdown_rect)
        pygame.draw.rect(screen, BLACK, dropdown_rect, 2)
        draw_text(screen, COLOR_OPTIONS[selected_color_index], (dropdown_rect.x + 5, dropdown_rect.y + 5))

        if dropdown_open:
            for i, option in enumerate(COLOR_OPTIONS):
                option_rect = pygame.Rect(dropdown_rect.x, dropdown_rect.y + 40 + i * 30, dropdown_rect.width, 30)
                color = (200, 200, 255) if i == dropdown_option_focus else (255, 255, 255)
                pygame.draw.rect(screen, color, option_rect)
                pygame.draw.rect(screen, BLACK, option_rect, 1)
                draw_text(screen, option, (option_rect.x + 5, option_rect.y + 5))

        # Apply button
        pygame.draw.rect(screen, (200, 255, 200) if focus_index == 1 else GRAY, apply_btn)
        pygame.draw.rect(screen, BLACK, apply_btn, 2)
        draw_text(screen, "Apply", (apply_btn.x + 15, apply_btn.y + 5))

        # Close button
        pygame.draw.rect(screen, (255, 200, 200) if focus_index == 2 else GRAY, close_btn)
        pygame.draw.rect(screen, BLACK, close_btn, 2)
        draw_text(screen, "Close", (close_btn.x + 15, close_btn.y + 5))

        pygame.display.update()


def kill_processes(running_processes,pid_running_processes):

    if not running_processes and not pid_running_processes:
        print("No processes to kill.")
        return
    for key, process in running_processes.items():
        try:
            print(f"Killing process: {key} with PID {process.pid}")
            process.kill()  # Directly kill the process
            # Alternatively, you can use: os.kill(process.pid, signal.SIGTERM) for a gentler approach
        except Exception as e:
            print(f"Error killing process {key}: {e}")
    running_processes.clear()

    print("killing pids")
    for process in pid_running_processes:
        pid = pid_running_processes[process]
        try:
            print(f"Killing PID: {pid} exe: {process}")
            p = psutil.Process(pid)
            p.terminate()  # Or p.kill() to force
            p.wait(timeout=3)
            print(f"Process {pid} terminated.")
        except psutil.NoSuchProcess:
            print("No such process.")
        except psutil.AccessDenied:
            print("Access denied.")
        except psutil.TimeoutExpired:
            print("Timeout while waiting for process to terminate.")
    pid_running_processes.clear()
    print(f"running_processes: {running_processes} | pid_running_processes: {pid_running_processes}")

def launch_rom(platform_name, running_processes, pid_running_processes, setting_files, menu_options, current_theme, selected_rom=None):#Selecting an item from the menu

    #Does selected rom exist in pid_running_processes or running_processes, if so focus the window and return. otherwise continue. this is to avoid games closing and relaunching
    #currently works for everything except xbox/pc games because pid_running_processes doesnt store the .lnk in the title to check against.
    print(running_processes)
    print(pid_running_processes)
    if selected_rom in running_processes:
        print(f"{selected_rom} Already exists in running_processes...")
        last_process = list(running_processes.keys())[-1]
        pid = running_processes[last_process].pid
        print(pid)
        focus_window_by_pid(pid)
        print(f"Focusing {last_process} ({pid})...")
        return
    else:
        print(f"{selected_rom} doesnt exist in running_processes: {running_processes}")
        #launches game since it isnt running.


    def run_command(cmd):
        if(platform_name == "XBOX"):
            starter = 'start "EMULATED_XBOX" ' #XBOX Roms use .lnk 's
            shell = True            
        else:
            starter = "cmd /c"
            shell = False
        try:
            cmd_command = f'{starter} "{cmd}"'
            process = subprocess.Popen(cmd, shell=shell)
            print(f'Launching with PID: {process.pid} {cmd_command}')
            kill_processes(running_processes,pid_running_processes)#close any other emulators running before opening new ROM
            
            if(platform_name == "XBOX"):
                displayAlert("Loading...",3)
                exe = get_shortcut_target(cmd)
                #print(exe)

                if exe == "steam.exe":
                    exe_name = "steam.exe"
                else:
                    exe_name = os.path.basename(exe)


                #print("exe is "+exe_name)
                pid = get_pid_by_exe_name(exe_name)

                if pid:
                    print(f"{exe_name} is running with PID {pid}")
                    pid_running_processes[exe_name] = pid  # Add to dictionary, to be able to kill later
                    #detect children to kill children processes, e.g. if we open a steam game steam opens the exe
                    parent = psutil.Process(process.pid)
                    i = 0
                    while i<=1000:
                        time.sleep(0.01)
                        i+=1

                    children = parent.children(recursive=True)
                    for child in children:
                        print(f"Child Process Name: {child.name()}, PID: {child.pid}")
                        pid_running_processes[child.name()] = child.pid

                else:
                    print(f"{exe_name} is not running")
            else:
                running_processes[selected_rom] = process  # Add to dictionary
            # #----MOVE MOUSE CURSOR OUT OF THE WAY-----#
            move_mouse_bottom_left()
            #print("Command launched, exiting Python script.")
            #sys.exit()
        except Exception as e:
            print(f"Couldn not launch. {e}")
        print("Process Info:")
        print(f"running_processes: {running_processes}")
        print(f"pid_running_processes: {pid_running_processes}")

    print(f"Running: {platform_name} - {selected_rom}")

    if(platform_name == "Desktop"):
        if selected_rom == "Exit.eo":
            print("Exiting to desktop")
            sys.exit()
        elif selected_rom == "Settings.eo":
            show_color_modal(screen, setting_files, current_theme, themes)
            print("Settings...")
        elif selected_rom == "Return to game.eo":
            try:
                last_process = list(running_processes.keys())[-1]
                print(last_process)
                pid = running_processes[last_process].pid
                print(pid)
                focus_window_by_pid(pid)
                print(f"Focusing {last_process} ({pid})...")
            except Exception as e:
                print(e)
            try:
                last_process = list(pid_running_processes.keys())[-1]
                print(last_process)
                pid = get_pid_by_exe_name(last_process)
                focus_window_by_pid(pid)
                print(f"Focusing {last_process} ({pid})...")
            except Exception as e:
                print(e)
        elif selected_rom == "Sleep.eo":
            subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
            print("Settings...")
        elif selected_rom == "Spotify.eo":
            print(play_pause_spotfy())
        elif selected_rom == "Close All Games.eo":
            print(f"Closing {running_processes}")
            kill_processes(running_processes,pid_running_processes)#close any other emulators running before opening new ROM
    if platform_name == "PS2" and selected_rom:
        rom_directory = next(item["folder"] for item in menu_options if item["name"] == platform_name)
        cmd = f'"emulators\\PCSX2\\pcsx2-qt.exe" -fullscreen -batch -- "{rom_directory}\\{selected_rom}"'#Change this so it checks for configs
        run_command(cmd)
    if platform_name == "PS3" and selected_rom:
        rom_directory = next(item["folder"] for item in menu_options if item["name"] == platform_name)
        cmd = f'"emulators\\rpcs3\\rpcs3.exe" "{rom_directory}\\{selected_rom}"\\PS3_GAME\\USRDIR\\EBOOT.BIN'#Change this so it checks for configs
        run_command(cmd)
    if platform_name == "GameBoy" and selected_rom:
        rom_directory = next(item["folder"] for item in menu_options if item["name"] == platform_name)
        cmd = f'emulators\\mGBA\\mGBA.exe --fullscreen "{rom_directory}\\{selected_rom}'
        run_command(cmd)
    if (platform_name == "GameCube" or platform_name == "Wii") and selected_rom:
        rom_directory = next(item["folder"] for item in menu_options if item["name"] == platform_name)
        cmd = f'"emulators\\DolphinEmu\\Dolphin.exe" --config "Dolphin.Display.Fullscreen=True" -b -e "{rom_directory}\\{selected_rom}'
        run_command(cmd)
    if platform_name == "N64" and selected_rom:
        rom_directory = next(item["folder"] for item in menu_options if item["name"] == platform_name)
        cmd = f'"emulators\\Project64 3.0\\Project64.exe" --fullscreen -fullscreen "{rom_directory}\\{selected_rom}'
        run_command(cmd)
    if platform_name == "PSP" and selected_rom:
        rom_directory = next(item["folder"] for item in menu_options if item["name"] == platform_name)
        cmd = f'"emulators\\PPSSPP\\PPSSPPWindows64.exe" --fullscreen "{rom_directory}\\{selected_rom}'
        run_command(cmd)

    if platform_name == "PS1" and selected_rom:
        rom_directory = next(item["folder"] for item in menu_options if item["name"] == platform_name)
        cmd = f'"emulators\\pcsx-redux\\pcsx-redux.exe" -fullscreen -f -run -iso "\\ROMs\\PS1Roms\\{selected_rom}"'
        run_command(cmd)
    if platform_name == "DS" and selected_rom:
        rom_directory = next(item["folder"] for item in menu_options if item["name"] == platform_name)
        cmd = f'"emulators\\melonDS\\melonDS.exe" -f {os.getcwd()}"\\ROMS\\DSRoms\\{selected_rom}"'

        run_command(cmd)  
    if platform_name == "XBOX" and selected_rom:
        rom_directory = next(item["folder"] for item in menu_options if item["name"] == platform_name)
        cmd = f'ROMS\\XBOXRoms\\{selected_rom}' #no exe needed, as we're pointing directly to a shortcut

        run_command(cmd)    





def remove_extension(filename):
    """Remove the extension from a filename using the whitelist."""
    whitelist = load_whitelist('whitelisted_rom_extensions.txt')
    for ext in whitelist:
        if filename.lower().endswith(ext):
            return filename[: -len(ext)]  # Remove the extension
    return filename  # Return unchanged if no matching extension

    
def generate_sparkles(num=50):
    global sparkles
    sparkles = [{"size": random.uniform(0.01, 2),"x": random.randint(0, WIDTH), "y": random.randint(0, HEIGHT), "speed": random.randint(1, 4)} for _ in range(num)]

def move_sparkles():
    global sparkles
    for sparkle in sparkles:
        sparkle["y"] -= sparkle["speed"]
        if sparkle["y"] < 0:
            sparkle["y"] = HEIGHT
            sparkle["x"] = random.randint(0, WIDTH)

def load_whitelist(filename):
    """Load whitelist extensions from a file."""
    if not os.path.exists(filename):
        return set()
    with open(filename, 'r') as f:
        return set(line.strip().lower() for line in f)
def get_roms(folder):
    """Get ROMs from folder using a whitelist stored in a file. Also include folders."""
    whitelist = load_whitelist('whitelisted_rom_extensions.txt')
    
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    roms_and_folders = []

    for item in os.listdir(folder):
        full_path = os.path.join(folder, item)
        if os.path.isfile(full_path):
            if any(item.lower().endswith(ext) for ext in whitelist):
                roms_and_folders.append(item)
        elif os.path.isdir(full_path):
            roms_and_folders.append(item)  # Append folder names too
    
    return roms_and_folders

def apply_opacity(image, opacity):
    """Apply the given opacity to an image."""
    # Create a copy of the image
    new_image = image.copy()
    new_image.fill((255, 255, 255, opacity), special_flags=pygame.BLEND_RGBA_MULT)
    return new_image

def draw_menu(selected_index, roms, selected_rom_index, WHITE, menu_options, HIDDEN, font, controller_images, small_font, disk_image, GRAY, roms_icons):
    global horizontal_scroll_offset, vertical_scroll_offset

    # Horizontal scrolling logic for consoles
    target_offset = -selected_index * (WIDTH // 10)  # Space between each console
    scroll_speed = 2  # Speed of horizontal scroll
    if horizontal_scroll_offset != target_offset:
        step = (target_offset - horizontal_scroll_offset) // scroll_speed
        horizontal_scroll_offset += step

    # Calculate max vertical scroll offset for ROMs
    if roms:
        max_scroll_offset = max(0, (len(roms) - 1) * (HEIGHT // 15))
        vertical_scroll_offset = min(max(0, selected_rom_index * (HEIGHT // 15)), max_scroll_offset)

    # Draw sparkles
    move_sparkles()
    for sparkle in sparkles:
        pygame.draw.circle(screen, WHITE, (sparkle["x"], sparkle["y"]), sparkle["size"]) #default is 2

    # Dynamic scaling based on resolution
    console_img_size = (WIDTH // 12, WIDTH // 12)  # Console images scale to 8.3% of screen width
    rom_img_size = (WIDTH // 20, WIDTH // 20)  # Disk images scale to 5% of screen width
    total_width = len(menu_options) * (WIDTH // 13)  # Total width of all menu options combined
    start_x = (WIDTH - total_width) // 2  # Center the entire menu horizontally
    y_start = HEIGHT // 2.5 - (HEIGHT // 4)  # Adjusted to start higher for better positioning
    spacing = WIDTH // 8  # Spacing between each console title

    for i, option in enumerate(menu_options):
        color = WHITE if i == selected_index else HIDDEN
        text_surface = font.render(option["name"], True, color)
        if color == HIDDEN:
            text_surface.set_alpha(0)

        # Load and apply opacity to the controller image
        controller_img = controller_images[option["name"]]
        opacity = 150 if i == selected_index else 80
        controller_img = apply_opacity(controller_img, opacity)
        controller_img = pygame.transform.smoothscale(controller_img, console_img_size)
        controller_rect = pygame.Rect(
            start_x + i * spacing + horizontal_scroll_offset,
            y_start,
            *console_img_size,
        )
        screen.blit(controller_img, controller_rect.topleft)

        # Draw the Console Name centered below the image
        text_rect = text_surface.get_rect(center=(controller_rect.centerx, controller_rect.bottom + 20))
        screen.blit(text_surface, text_rect)

        # Draw ROMs below the console name
        rom_text_y = text_rect.bottom + 20
        if selected_index == i:  # Draw ROMs for the selected console
            if roms:  # If ROMs are found, display them
                for j, rom in enumerate(roms):
                    # Position of each ROM item based on vertical_scroll_offset
                    rom_y_position = rom_text_y + j * (HEIGHT // 15) - vertical_scroll_offset
                    if 0 <= rom_y_position <= HEIGHT:  # Draw only if visible
                        # Calculate disk opacity based on position relative to the selected ROM
                        relative_position = j - selected_rom_index
                        if relative_position == 0:
                            alpha = 255  # Fully visible
                        elif relative_position == -1 or relative_position > 0:
                            alpha = 35  # Slightly visible
                        elif relative_position == -2:
                            alpha = 15  # Almost invisible
                        else:
                            alpha = 0  # Fully transparent

                        color = WHITE if j == selected_rom_index else GRAY
                        romName = remove_extension(rom) # removes extension .iso etc
                        rom_text = small_font.render(romName, True, color) #rom text displayed
                        rom_text.set_alpha(alpha if alpha > 0 else 0)


                        #Load custom disk image if named in list, otherwise load default image
                        for item in roms_icons:
                            if(romName == item["romName"]):
                                rom_name = item["romName"]
                                image = item["image"]
                                disk_resized = pygame.transform.smoothscale(pygame.image.load(f"assets/{image}"), rom_img_size)
                                disk_resized = apply_opacity(disk_resized, alpha)
                                break
                            else:#load default
                                disk_resized = pygame.transform.smoothscale(disk_image, rom_img_size)
                                disk_resized = apply_opacity(disk_resized, alpha)

                        disk_rect = disk_resized.get_rect(midleft=(controller_rect.left + WIDTH // 100, rom_y_position))
                        rom_text_rect = rom_text.get_rect(midleft=(disk_rect.right + 10, disk_rect.centery))

                        # Only draw the disk and ROM text if they are within the visible range
                        if alpha > 0:  # Only draw if alpha is greater than 0
                            screen.blit(disk_resized, disk_rect.topleft)
                            screen.blit(rom_text, rom_text_rect.topleft)

            else:  # If no ROMs are found, display disk image and "No ROMs found"
                no_rom_text = small_font.render("No ROMs found", True, WHITE)
                disk_resized = pygame.transform.smoothscale(disk_image, rom_img_size)
                disk_rect = disk_resized.get_rect(midleft=(controller_rect.left + WIDTH // 20, rom_text_y))
                no_rom_text_rect = no_rom_text.get_rect(midleft=(disk_rect.right + 10, disk_rect.centery))
                screen.blit(disk_resized, disk_rect.topleft)
                screen.blit(no_rom_text, no_rom_text_rect.topleft)






def draw_glowing_text(surface, text, font, color, position, pulse_speed=5, glow_color=(255, 255, 255)):
    # Calculate the current pulse intensity using sine wave
    pulse_intensity = math.sin(pygame.time.get_ticks() / 1000.0 * pulse_speed) * 100 + 155  # Oscillates between 55 and 255
    pulse_intensity = int(pulse_intensity)  # Get integer value for color intensity
    
    # Render the glowing effect (shadow or glow around the text)
    glow_text = font.render(text, True, glow_color)
    glow_rect = glow_text.get_rect(topleft=position)
    
    # Adjust the glow intensity by modifying the color alpha
    glow_surface = glow_text.copy()
    glow_surface.fill((pulse_intensity, pulse_intensity, pulse_intensity), special_flags=pygame.BLEND_RGB_ADD)

    # Draw glow
    surface.blit(glow_surface, glow_rect.topleft)
    
    # Render the actual text with regular color
    regular_text = font.render(text, True, color)
    surface.blit(regular_text, glow_rect.topleft)

def draw_wave(surface, time_offset, wave_color, VERTICAL_AMPLITUDE, VERTICAL_WAVE_SPEED, BASE_AMPLITUDE, FREQUENCY, wave_index, ):
    """Draw a single wave and return its points."""
    points = []
    start_x = 0
    end_x = WIDTH

    # Dynamic vertical offset for start and end points
    vertical_shift = VERTICAL_AMPLITUDE * math.sin(time_offset * VERTICAL_WAVE_SPEED)
    start_offset = 50 * math.sin((wave_index + 1) * 0.5 + time_offset)
    end_offset = 50 * math.sin((wave_index + 1) * 0.5 - time_offset)

    for x in range(start_x, end_x):
        amplitude = BASE_AMPLITUDE * (1 + 0.5 * math.sin(x * 0.005 + wave_index))
        y = (
            HEIGHT // 2
            + vertical_shift
            + amplitude * math.sin((x * FREQUENCY) + time_offset)
        )
        if x == start_x:  # Adjust the first point
            y += start_offset
        elif x == end_x - 1:  # Adjust the last point
            y += end_offset

        points.append((x, int(y)))

    # Draw anti-aliased lines for smooth visuals
    for i in range(len(points) - 1):
        pygame.gfxdraw.line(
            surface,
            points[i][0],
            points[i][1],
            points[i + 1][0],
            points[i + 1][1],
            wave_color,
        )

    return points

def draw_shading(surface, wave1, wave2, current_theme):
    """Draw a shaded area between two consecutive waves."""
    if len(wave1) != len(wave2):
        return

    for i in range(len(wave1) - 1):
        quad_points = [
            wave1[i],
            wave1[i + 1],
            wave2[i + 1],
            wave2[i],
        ]
        pygame.gfxdraw.filled_polygon(surface, quad_points, current_theme["shade_color"])


def displayTopRightHeader():
    joystickCount = len(joysticks)
    screen_width, screen_height = WIDTH, HEIGHT  # Use global WIDTH and HEIGHT
    rect_height = 40
    padding = 5
    spacing = 20  # Increased spacing between joystick count and date

    # Colors and font
    white = (255, 255, 255)
    border_alpha = int(255 * 0.35)
    font = pygame.font.SysFont("Helvetica", 18)

    # Load images
    xbox_icon = pygame.image.load("assets/xboxone.png").convert_alpha()
    clock_icon = pygame.image.load("assets/clock.png").convert_alpha()

    # Define icon sizes
    icon_size = 20
    xbox_icon = pygame.transform.smoothscale(xbox_icon, (icon_size, icon_size))

    # Scale clock icon by 3.5x
    clock_icon = pygame.transform.smoothscale(clock_icon, (int(icon_size * 3.5), int(icon_size * 3.5)))
    clock_width, clock_height = clock_icon.get_size()

    # Get current date string
    now = datetime.datetime.now()
    date_str = now.strftime("%d/%m %I:%M%p")

    # Render text
    joystick_text = font.render(f"x {str(joystickCount)}", True, white)
    date_text = font.render(date_str, True, white)

    # Calculate minimum required width
    min_required_width = (
        padding * 4
        + icon_size
        + joystick_text.get_width()
        + spacing
        + date_text.get_width()
        + clock_width
    )

    rect_width = max(int(screen_width * 0.15), min_required_width)
    rect_x = screen_width - rect_width - 10  # 10px padding from right
    rect_y = 10  # 10px padding from top

        # Create transparent surface for the border
    border_surface = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
    pygame.draw.rect(
        border_surface,
        (255, 255, 255, border_alpha),
        border_surface.get_rect(),
        width=1,
        border_radius=5  # Rounded corners
    )
    screen.blit(border_surface, (rect_x, rect_y))


    # Calculate positions
    # Position the clock icon at the far right, shifted down by 5 pixels
    clock_x = rect_x + rect_width - padding - clock_width // 1.5
    clock_y = rect_y + (rect_height - clock_height) // 2.4  # Shift down by 2.4 pixels

    # Position the date text to the left of the clock icon
    date_text_x = clock_x - padding - date_text.get_width() // 1.2
    date_text_y = rect_y + (rect_height - date_text.get_height()) // 2

    # Position the joystick text to the left of the date text
    text1_x = rect_x + padding + icon_size + padding
    text1_y = rect_y + (rect_height - joystick_text.get_height()) // 2

    # Position the Xbox icon to the left of the joystick text
    xbox_x = rect_x + padding
    xbox_y = rect_y + (rect_height - icon_size) // 2

    # Blit to screen
    screen.blit(xbox_icon, (xbox_x, xbox_y))
    screen.blit(joystick_text, (text1_x, text1_y))
    screen.blit(date_text, (date_text_x, date_text_y))
    screen.blit(clock_icon, (clock_x, clock_y))

def displaySpotifyStatus():
    # Initialize persistent attributes
    if not hasattr(displaySpotifyStatus, "music_bars"):
        displaySpotifyStatus.music_bars = [10, 20, 15, 25, 18]
        displaySpotifyStatus.last_update = 0

    # Update animation every 100ms
    if time.time() - displaySpotifyStatus.last_update > 0.1:
        displaySpotifyStatus.music_bars = [random.randint(5, 25) for _ in displaySpotifyStatus.music_bars]
        displaySpotifyStatus.last_update = time.time()

    text_str = get_spotify_status()

    # If the status is "Spotify Not Running", don't display text or the background rectangle
    if text_str == "Spotify Not Running":
        return  # Skip displaying anything if Spotify is not running

    font = pygame.font.SysFont("Segoe UI Emoji", 20)
    text_surface = font.render(text_str, True, (255, 255, 255, 178))  # 70% opacity for text

    # Text rectangle
    text_rect = text_surface.get_rect()
    padding = 15
    extra_margin = 5
    bar_width = 4
    bar_spacing = 3
    num_bars = len(displaySpotifyStatus.music_bars)
    bars_width_total = num_bars * (bar_width + bar_spacing) + 5  # Add 5px extra space at the end of the bars

    # Adjust position
    text_rect.bottomright = (
        screen.get_width() - padding - extra_margin,
        screen.get_height() - padding - extra_margin
    )

    # Background rectangle
    bg_rect = pygame.Rect(
        text_rect.left - padding - bars_width_total,
        text_rect.top - padding,
        text_rect.width + 2 * padding + bars_width_total,
        text_rect.height + 2 * padding
    )

    # Background surface with alpha
    box_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(box_surface, (180, 180, 180, 100), box_surface.get_rect(), border_radius=5)

    # Check if the Spotify status is "Paused"
    if text_str == "Spotify - Paused":
        barheight = 25
        barwidth = 5
        y = 15
        bar_rect = pygame.Rect(37, y, barwidth, barheight)#x, y , width, height
        pygame.draw.rect(box_surface, (255, 255, 255, 178), bar_rect)

        bar_rect = pygame.Rect(25, y, barwidth, barheight)#x, y , width, height
        pygame.draw.rect(box_surface, (255, 255, 255, 178), bar_rect)
    else:
        # Draw animated music bars
        for i, bar_height in enumerate(displaySpotifyStatus.music_bars):
            x = padding + i * (bar_width + bar_spacing)
            y = (box_surface.get_height() - bar_height) // 2
            bar_rect = pygame.Rect(x, y, bar_width, bar_height)
            pygame.draw.rect(box_surface, (255, 255, 255, 178), bar_rect)

    # Blit to screen
    screen.blit(box_surface, (bg_rect.left, bg_rect.top))
    screen.blit(text_surface, text_rect)


def displayWave(time_offset, NUM_WAVES, WAVE_SPACING, VERTICAL_AMPLITUDE, VERTICAL_WAVE_SPEED, BASE_AMPLITUDE, FREQUENCY, current_theme):
    global WIDTH,HEIGHT
    # Create a transparent surface for the waves
    wave_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    # Draw waves and shaded areas
    previous_wave = None
    for i in range(NUM_WAVES):
        wave_offset = i * WAVE_SPACING
        opacity = int(255 * (1 - (i / NUM_WAVES)))  # Opacity decreases for higher waves
        wave_color = (*current_theme["wave_color_base"], opacity)  # Add alpha value
        current_wave = draw_wave(wave_surface, time_offset + wave_offset, wave_color, VERTICAL_AMPLITUDE, VERTICAL_WAVE_SPEED, BASE_AMPLITUDE, FREQUENCY, i)

        # Add shading between consecutive waves
        if previous_wave:
            draw_shading(wave_surface, previous_wave, current_wave, current_theme)

        previous_wave = current_wave

    # Overlay the wave surface on the main screen

    return screen.blit(wave_surface, (0, 0))


#check keyboard controller input
def checkInput(menu_options,selected_index,selected_rom_index,roms_dict,roms,event, sounds, running_processes, pid_running_processes, settings_file, current_theme):

    # Get ROMs for selected option from the preloaded dictionary

    # HANDLE KEYBOARD + CONTROLLER INPUT
    if event.type == pygame.JOYBUTTONDOWN:
        if(event.button == "10" or event.button == 10):
            print("Home Button Pressed")
        #print(f"Button {event.button} pressed!")  # Prints all button IDs
    if event.type == pygame.KEYDOWN or event.type == pygame.JOYHATMOTION or event.type == pygame.JOYBUTTONDOWN:
        #print(f"EVENT: {event} {event.type}")
        if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
            selected_index = max(0, selected_index - 1)
            selected_rom_index = 0  # Reset ROM selection
            pygame.mixer.Sound(sounds["cursor"]).play()
        elif event.type == pygame.JOYHATMOTION and event.value == (-1, 0):  # D-pad Left
            selected_index = max(0, selected_index - 1)
            selected_rom_index = 0  # Reset ROM selection
            pygame.mixer.Sound(sounds["cursor"]).play()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
            selected_index = min(len(menu_options) - 1, selected_index + 1)
            selected_rom_index = 0  # Reset ROM selection
            pygame.mixer.Sound(sounds["cursor"]).play()
        elif event.type == pygame.JOYHATMOTION and event.value == (1, 0):  # D-pad Right
            selected_index = min(len(menu_options) - 1, selected_index + 1)
            selected_rom_index = 0  # Reset ROM selection
            pygame.mixer.Sound(sounds["cursor"]).play()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
            if roms:
                selected_rom_index = max(0, selected_rom_index - 1)
                pygame.mixer.Sound(sounds["cursor"]).play()
        elif event.type == pygame.JOYHATMOTION and event.value == (0, 1):  # D-pad Up
            if roms:
                selected_rom_index = max(0, selected_rom_index - 1)
                pygame.mixer.Sound(sounds["cursor"]).play()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
            if roms:
                selected_rom_index = min(len(roms) - 1, selected_rom_index + 1)
                pygame.mixer.Sound(sounds["cursor"]).play()
        elif event.type == pygame.JOYHATMOTION and event.value == (0, -1):  # D-pad Down
            if roms:
                selected_rom_index = min(len(roms) - 1, selected_rom_index + 1)
                pygame.mixer.Sound(sounds["cursor"]).play()
        elif (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN) or (
            event.type == pygame.JOYBUTTONDOWN and event.button == 0
            
        ):  # Enter key or "A" button

            if roms:
                #launch_game(menu_options[selected_index]["cmd"], roms[selected_rom_index])
                #print(roms[selected_rom_index])
                #print(menu_options[selected_index])
                launch_rom(menu_options[selected_index]["name"], running_processes, pid_running_processes, settings_file, menu_options, current_theme, roms[selected_rom_index])
    return True, selected_index, selected_rom_index  # Return updated values and continue


def main():
    set_all_packages(global_scope=globals())
    themes = load_theme_json()
    # move mouse of the way for a clean display
    move_mouse_bottom_left()
    # Initialize Pygame

    pygame.init()
    # Load the icon image

    icon = pygame.image.load('config/icon.png')

    # Set the window icon
    pygame.display.set_icon(icon)
    pygame.joystick.init()
    print("saad was here :P <3")
    print(f"Joysticks connected: {pygame.joystick.get_count()}")
    # Screen Dimensions (fits the window size)

    script_name = os.path.basename(__file__)

    running_processes = {}
    pid_running_processes = {}

    if is_another_instance_running(script_name):
        print("Another instance of this script is already running. Exiting.")
        sys.exit(1)

    pygame.display.set_caption("XMBEmulator")

    # Colors
    BLACK = (0, 0, 0)
    HIDDEN = (0, 0, 0, 0)
    WHITE = (255, 255, 255)
    HIGHLIGHT = (200, 200, 255)
    GRAY = (200, 200, 255)

    # FONTS
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)

    settings_file = "config/settings.json"
    with open(settings_file, "r") as f:
        settings = json.load(f)

    saved_theme_name = settings.get("saved_theme", "Dark Blue")  # fallback default
    hide_wii = settings.get("hide_wii", False)
    hide_xbox = settings.get("hide_xbox", False)
    hide_spotify = settings.get("hide_spotify", False)

    roms_icons = "config/rom_icons.json"
    with open(roms_icons, "r") as f:
        roms_icons = json.load(f)

    global horizontal_scroll_offset,vertical_scroll_offset, screen,gradient_background, WIDTH, HEIGHT,joysticks
    WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h  # Dynamically fit the screen size
    # WIDTH,HEIGHT=1024,524
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    time_offset = 0  # For animating waves

    current_theme = get_theme_by_name(saved_theme_name, themes)  # get saved theme by settings.json
    # Wave parameters
    NUM_WAVES = 8
    FREQUENCY = 0.005
    BASE_AMPLITUDE = 25
    HORIZONTAL_SPEED = 0.005
    VERTICAL_WAVE_SPEED = 0.001
    VERTICAL_AMPLITUDE = 20
    WAVE_SPACING = 50

    menu_options = load_menu_json()

    if settings.get("hide_xbox", True):
        menu_options = [option for option in menu_options if option["name"] != "XBOX"]
    if settings.get("hide_wii", True):
        menu_options = [option for option in menu_options if option["name"] != "Wii"]

    sounds = {}  # Creating an empty dictionary
    sounds["cursor"] = "assets/cursor.mp3"  # Setting a value for the "cursor" key

    gradient_background = create_gradient_surface(
        WIDTH,
        HEIGHT,
        current_theme["gradient_start"],
        current_theme["gradient_end"],
    )

    # Load Resources
    background_image = pygame.Surface((WIDTH, HEIGHT))
    background_image.fill((0, 0, 100))  # Gradient will be handled manually now

    controller_images = {option["name"]: pygame.image.load(option["image"]) for option in menu_options}
    disk_image = pygame.image.load("assets/disk.png")  # Disk image for ROMs

    # Sparkle Generation
    sparkles = []

    selected_index = 0
    selected_rom_index = 0
    horizontal_scroll_offset = 0
    vertical_scroll_offset = 0
    clock = pygame.time.Clock()
    running = True
    # Xbox Controller Initialization
    joystick = None
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
    # Preload ROMs into a dictionary for each console
    roms_dict = {option["name"]: get_roms(option["folder"]) for option in menu_options}
    #print(roms_dict)
    # Generate sparkles
    generate_sparkles()
    roms = roms_dict[menu_options[selected_index]["name"]]
    joysticks = {}  # Dictionary to track connected joysticks
    while running:
        # === Detect and Initialize Newly Connected Joysticks ===
        for i in range(pygame.joystick.get_count()):  
            if i not in joysticks:  # If joystick is not already initialized
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                joysticks[i] = joystick  # Store initialized joystick
                print(f"🎮 Joystick {i} connected: {joystick.get_name()}")  # ✅ CONNECTED

        # === Detect and Remove Disconnected Joysticks ===
        connected_ids = set(range(pygame.joystick.get_count()))  
        for j_id in list(joysticks.keys()):  
            if j_id not in connected_ids:  # If joystick is no longer connected
                print(f"❌ Joystick {j_id} disconnected: {joysticks[j_id].get_name()}")  # ✅ DISCONNECTED
                del joysticks[j_id]  # Remove from tracking
        #BACKGROUND GRADIENT
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                # Get the new width and height when the window is resized
                new_width, new_height = event.size
                print(f"New Window Size: {new_width}x{new_height}")
                WIDTH, HEIGHT = event.size
                # Create a new gradient background with the new size
                gradient_background = create_gradient_surface(
                    new_width,
                    new_height,
                    current_theme["gradient_start"],
                    current_theme["gradient_end"],
                )
                # Set the new gradient background
                screen.blit(gradient_background, (0, 0))

            running, selected_index, selected_rom_index = checkInput(menu_options, selected_index, selected_rom_index, roms_dict, roms,event, sounds,
                           running_processes, pid_running_processes, settings_file, current_theme)


        
        screen.blit(gradient_background, (0, 0))

        displayTopRightHeader()
        if not hide_spotify:
            displaySpotifyStatus()
        displayWave(time_offset, NUM_WAVES, WAVE_SPACING, VERTICAL_AMPLITUDE, VERTICAL_WAVE_SPEED, BASE_AMPLITUDE, FREQUENCY,current_theme)

        # Update the screen

        # Increment time offset
        time_offset += HORIZONTAL_SPEED
        roms = roms_dict[menu_options[selected_index]["name"]]

        

        # Draw Menu with the selected ROMs for the chosen platform
        draw_menu(selected_index, roms, selected_rom_index, WHITE, menu_options, HIDDEN, font, controller_images, small_font, disk_image, GRAY, roms_icons)

        pygame.display.flip()
        clock.tick(120)

    pygame.quit()

if __name__ == "__main__":

    main()
