import os
import subprocess
import sys

# Hide Pygame support prompt
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

# Function to install a package if it's missing
def install_and_import(package):
    try:
        __import__(package)
        #print(f"{package} is already imported.")
    except ImportError:
        #print(f"{package} not found, installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            #print(f"{package} has been installed successfully.")
        except subprocess.CalledProcessError as e:
            #print(f"Error installing {package}: {e}")
            return
        # Retry import after installation
        globals()[package] = __import__(package)  # This puts the package into the global namespace.
        #print(f"{package} has been imported successfully.")
    
    # Explicitly import the package
    globals()[package] = __import__(package)  # Ensure the package is available by name
    return globals()[package]


# Ensure required modules are available
install_and_import('pygame')
install_and_import('subprocess')
install_and_import('random')
install_and_import('math')
install_and_import('sys')
install_and_import('pygame.gfxdraw')
install_and_import('psutil')


# Initialize Pygame

pygame.init()

pygame.joystick.init()
print(f"Joysticks connected: {pygame.joystick.get_count()}")
# Screen Dimensions (fits the window size)

script_name = os.path.basename(__file__)


def is_another_instance_running(script_name):
    current_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Check if the process is different and the script is in the command line arguments
            if proc.info['pid'] != current_pid and proc.info['cmdline']:
                if script_name in proc.info['cmdline']:
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


if is_another_instance_running(script_name):
    print("Another instance of this script is already running. Exiting.")
    sys.exit(1)

WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h  # Dynamically fit the screen size
#WIDTH,HEIGHT=1024,524
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Emulator Launcher")

# Colors
BLACK = (0, 0, 0)
HIDDEN = (0, 0, 0, 0)
WHITE = (255, 255, 255)
HIGHLIGHT = (200, 200, 255)
GRAY = (200, 200, 255)

#FONTS
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)


themes = [
    {
        "gradient_start": (0, 0, 64),  # Dark blue
        "gradient_end": (0, 102, 255),  # Bright blue
        "wave_color_base": (0, 102, 255),
        "shade_color": (200, 200, 200, 105),
    },
    {
        "gradient_start": (64, 0, 64),  # Purple
        "gradient_end": (255, 0, 255),  # Magenta
        "wave_color_base": (255, 0, 255),
        "shade_color": (200, 200, 200, 105),
    },
]

# Select a theme
current_theme = themes[0]

# Wave parameters
NUM_WAVES = 8
FREQUENCY = 0.005
BASE_AMPLITUDE = 25
HORIZONTAL_SPEED = 0.005
VERTICAL_WAVE_SPEED = 0.001
VERTICAL_AMPLITUDE = 20
WAVE_SPACING = 50


# Platforms and Directories
menu_options = [
    {"name": "PS1", "folder": "ROMs\\PS1Roms", "image": "assets/ps1.png", "cmd": "ps1.exe"},
    {"name": "PS2", "folder": "ROMs\\PS2Roms", "image": "assets/ps2.png", "cmd": "ps2.exe"},
    {"name": "PSP", "folder": "ROMs\\PSPRoms", "image": "assets/psp.png", "cmd": "psp.exe"},
    {"name": "GameCube", "folder": "ROMs\\GameCubeRoms", "image": "assets/gamecube.png", "cmd": "gamecube.exe"},
    {"name": "N64", "folder": "ROMs\\N64Roms", "image": "assets/n64.png", "cmd": "n64.exe"},
    {"name": "GameBoy", "folder": "ROMs\\GameBoyRoms", "image": "assets/gameboy.png", "cmd": "gameboy.exe"},
    {"name": "DS", "folder": "ROMs\\DSRoms", "image": "assets/ds.png", "cmd": "ds.exe"},
    {"name": "Xbox", "folder": "ROMs\\XboxRoms", "image": "assets/xbox.png", "cmd": "xbox.exe"},
    {"name": "Desktop", "folder": "ROMs\\Desktop", "image": "assets/desktop2.png", "cmd": "exit"},
]
sounds = {}  # Creating an empty dictionary
sounds["cursor"] = "assets/cursor.mp3"  # Setting a value for the "cursor" key



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


# Create the gradient background
gradient_background = create_gradient_surface(
    WIDTH,
    HEIGHT,
    current_theme["gradient_start"],
    current_theme["gradient_end"],
)





def launch_rom(platform_name, selected_rom=None):#Selecting an item from the menu
    def run_command(cmd):
        try:
            cmd_command = f'cmd /c "{cmd}"'
            print(cmd_command)
            subprocess.Popen(cmd, shell=False)
            # Use os.system() to execute the command via cmd and immediately exit the Python script
            #os.system(cmd_command)            
            # Exit the Python script immediately after the command is executed
            print("Command launched, exiting Python script.")
            sys.exit()
        except Exception as e:
            print(f"Couldn't launch. {e}")
    print(f"Running: {platform_name} {selected_rom}")
    #input()
    if(platform_name == "Desktop"):
        if selected_rom == "Exit":
            print("Exiting to desktop")
            sys.exit()
        elif selected_rom == "Settings":
            print("Settings...")
    if platform_name == "PS2" and selected_rom:
        rom_directory = next(item["folder"] for item in menu_options if item["name"] == platform_name)
        cmd = f'"emulators\\PCSX2\\pcsx2-qt.exe" -fullscreen -batch -- "{rom_directory}\\{selected_rom}"'#Change this so it checks for configs
        run_command(cmd)
    if platform_name == "GameBoy" and selected_rom:
        rom_directory = next(item["folder"] for item in menu_options if item["name"] == platform_name)
        #cmd = f'"C:\\Program Files\\PCSX2\\pcsx2-qt.exe" -fullscreen -batch -- "{rom_directory}\\{selected_rom}"'#Change this so it checks for configs
        cmd = f'emulators\\mGBA\\mgba.exe --fullscreen "{rom_directory}\\{selected_rom}'
        run_command(cmd)
    if platform_name == "GameCube" and selected_rom:
        rom_directory = next(item["folder"] for item in menu_options if item["name"] == platform_name)
        #cmd = f'"C:\\Program Files\\PCSX2\\pcsx2-qt.exe" -fullscreen -batch -- "{rom_directory}\\{selected_rom}"'#Change this so it checks for configs
        cmd = f'"emulators\\DolphinEmu\\Dolphin.exe" --config "Dolphin.Display.Fullscreen=True" -b -e "{rom_directory}\\{selected_rom}'
        run_command(cmd)
    if platform_name == "N64" and selected_rom:
        rom_directory = next(item["folder"] for item in menu_options if item["name"] == platform_name)
        #cmd = f'"C:\\Program Files\\PCSX2\\pcsx2-qt.exe" -fullscreen -batch -- "{rom_directory}\\{selected_rom}"'#Change this so it checks for configs
        cmd = f'"emulators\\Project64 3.0\\Project64.exe" --fullscreen -fullscreen "{rom_directory}\\{selected_rom}'
        run_command(cmd)
    if platform_name == "PSP" and selected_rom:
        rom_directory = next(item["folder"] for item in menu_options if item["name"] == platform_name)
        #cmd = f'"C:\\Program Files\\PCSX2\\pcsx2-qt.exe" -fullscreen -batch -- "{rom_directory}\\{selected_rom}"'#Change this so it checks for configs
        cmd = f'"emulators\\PPSSPP\\PPSSPPWindows64.exe" --fullscreen "{rom_directory}\\{selected_rom}'
        run_command(cmd)

    if platform_name == "PS1" and selected_rom:
        rom_directory = next(item["folder"] for item in menu_options if item["name"] == platform_name)
        #cmd = f'"C:\\Program Files\\PCSX2\\pcsx2-qt.exe" -fullscreen -batch -- "{rom_directory}\\{selected_rom}"'#Change this so it checks for configs
        cmd = f'"emulators\\pcsx-redux\\pcsx-redux.exe" -fullscreen -f -run -iso "\\ROMs\\PS1Roms\\{selected_rom}"'
        run_command(cmd)
    if platform_name == "DS" and selected_rom:
        rom_directory = next(item["folder"] for item in menu_options if item["name"] == platform_name)
        #cmd = f'"C:\\Program Files\\PCSX2\\pcsx2-qt.exe" -fullscreen -batch -- "{rom_directory}\\{selected_rom}"'#Change this so it checks for configs
        cmd = f'"C:\\EmulatorOverlay\\emulators\\melonDS\\melonDS.exe" "\\ROMs\\DSRoms\\{selected_rom}"'
        run_command(cmd)    





# Load Resources
background_image = pygame.Surface((WIDTH, HEIGHT))
background_image.fill((0, 0, 100))  # Gradient will be handled manually now

controller_images = {option["name"]: pygame.image.load(option["image"]) for option in menu_options}
disk_image = pygame.image.load("assets/disk.png")  # Disk image for ROMs

# Sparkle Generation
sparkles = []

def generate_sparkles(num=50):
    global sparkles
    sparkles = [{"x": random.randint(0, WIDTH), "y": random.randint(0, HEIGHT), "speed": random.randint(1, 4)} for _ in range(num)]

def move_sparkles():
    global sparkles
    for sparkle in sparkles:
        sparkle["y"] -= sparkle["speed"]
        if sparkle["y"] < 0:
            sparkle["y"] = HEIGHT
            sparkle["x"] = random.randint(0, WIDTH)

# Get ROMs from Directories
def get_roms(folder):
    blacklist = ['.cue', '.sav','.zip','.rar','.html','.htm','.txt']  # Default blacklist if not provided
    if not os.path.exists(folder):
        os.makedirs(folder)  # Create folder if it doesn't exist
    # List files and filter out ones with extensions in the blacklist
    return [
        f for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f)) and not any(f.endswith(ext) for ext in blacklist)
    ]

def apply_opacity(image, opacity):
    """Apply the given opacity to an image."""
    # Create a copy of the image
    new_image = image.copy()
    new_image.fill((255, 255, 255, opacity), special_flags=pygame.BLEND_RGBA_MULT)
    return new_image

def draw_menu(selected_index, roms, selected_rom_index):
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
        pygame.draw.circle(screen, WHITE, (sparkle["x"], sparkle["y"]), 2)

    # Dynamic scaling based on resolution
    console_img_size = (WIDTH // 12, WIDTH // 12)  # Console images scale to 8.3% of screen width
    rom_img_size = (WIDTH // 20, WIDTH // 20)  # Disk images scale to 5% of screen width
    total_width = len(menu_options) * (WIDTH // 10)  # Total width of all menu options combined
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
                        rom_text = small_font.render(rom, True, color)
                        rom_text.set_alpha(alpha if alpha > 0 else 0)

                        # Resize disk image
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

def draw_wave(surface, time_offset, wave_color, wave_index):
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

def draw_shading(surface, wave1, wave2):
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


def displayWave(time_offset):
    global WIDTH,HEIGHT
    # Create a transparent surface for the waves
    wave_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    # Draw waves and shaded areas
    previous_wave = None
    for i in range(NUM_WAVES):
        wave_offset = i * WAVE_SPACING
        opacity = int(255 * (1 - (i / NUM_WAVES)))  # Opacity decreases for higher waves
        wave_color = (*current_theme["wave_color_base"], opacity)  # Add alpha value
        current_wave = draw_wave(wave_surface, time_offset + wave_offset, wave_color, i)

        # Add shading between consecutive waves
        if previous_wave:
            draw_shading(wave_surface, previous_wave, current_wave)

        previous_wave = current_wave

    # Overlay the wave surface on the main screen
    return screen.blit(wave_surface, (0, 0))


#check keyboard controller input
def checkInput(menu_options,selected_index,selected_rom_index,roms_dict,roms,event):

    # Get ROMs for selected option from the preloaded dictionary

    # HANDLE KEYBOARD + CONTROLLER INPUT
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
                launch_rom(menu_options[selected_index]["name"], roms[selected_rom_index])
    return True, selected_index, selected_rom_index  # Return updated values and continue
def main():
    global horizontal_scroll_offset,vertical_scroll_offset, screen,gradient_background, WIDTH, HEIGHT
    time_offset = 0  # For animating waves

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
    while running:
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

            running, selected_index, selected_rom_index = checkInput(menu_options, selected_index, selected_rom_index, roms_dict, roms,event)


        
        screen.blit(gradient_background, (0, 0))
        displayWave(time_offset)

        # Update the screen

        # Increment time offset
        time_offset += HORIZONTAL_SPEED
        roms = roms_dict[menu_options[selected_index]["name"]]


        #HANDLE KEYBOARD AND CONTROLLER INPUT:
        

        # Draw Menu with the selected ROMs for the chosen platform
        draw_menu(selected_index, roms, selected_rom_index)

        pygame.display.flip()
        clock.tick(120)

    pygame.quit()

if __name__ == "__main__":

    main()
