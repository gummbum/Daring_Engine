import os
import pygame
import tkinter as tk
from tkinter import filedialog, simpledialog
import threading
import queue

# Initialize Pygame
pygame.init()
pygame.font.init()  # Initialize Pygame's font module

# Pygame constants
WINDOW_WIDTH = 420
WINDOW_HEIGHT = 630
FONT_SIZE_LARGE = 40
FONT_SIZE_SMALL = 24
FONT_SIZE_X_SMALL = 12
TEXT_COLOR = (200, 255, 200)
BACKGROUND_COLOR = (0, 0, 0)

# Global variables
font_path = None
text_to_display = "Sample Text"
font_thread = None
font_thread_running = False
font_thread_lock = threading.Lock()

# Pygame thread function
def pygame_thread():
    global font_thread_running
    global font_thread

    # Create Pygame window
    pygame.display.set_caption("Font Helper - Display")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    # Set the position of the Pygame window beneath the Tkinter window
    pygame.display.window_pos = (root.winfo_x(), root.winfo_y() + root.winfo_height() + 10)
    
    font_large = None
    font_small = None
    font_x_small = None

    while font_thread_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                font_thread_running = False
        
        screen.fill(BACKGROUND_COLOR)

        if font_path:
            try:
                font_large = pygame.font.Font(font_path, FONT_SIZE_LARGE)
                font_small = pygame.font.Font(font_path, FONT_SIZE_SMALL)
                font_x_small = pygame.font.Font(font_path, FONT_SIZE_X_SMALL)
                # Create font objects for bold variations
                font_large_bold = pygame.font.Font(font_path, FONT_SIZE_LARGE)
                font_large_bold.set_bold(True)
                font_small_bold = pygame.font.Font(font_path, FONT_SIZE_SMALL)
                font_small_bold.set_bold(True)
                font_x_small_bold = pygame.font.Font(font_path, FONT_SIZE_X_SMALL)
                font_x_small_bold.set_bold(True)
                # Create font objects for italic variations
                font_large_italic = pygame.font.Font(font_path, FONT_SIZE_LARGE)
                font_large_italic.set_italic(True)
                font_small_italic = pygame.font.Font(font_path, FONT_SIZE_SMALL)
                font_small_italic.set_italic(True)
                font_x_small_italic = pygame.font.Font(font_path, FONT_SIZE_X_SMALL)
                font_x_small_italic.set_italic(True)
            except Exception as e:
                print(f"Error loading font: {str(e)}")

        if font_large and font_small and font_x_small:
            # Create text surfaces for different variations
            text_variations = {
                "Large_Upper": font_large.render(text_to_display.upper(), True, TEXT_COLOR),
                "Large_Lower": font_large.render(text_to_display.lower(), True, TEXT_COLOR),
                "Small_Upper": font_small.render(text_to_display.upper(), True, TEXT_COLOR),
                "Small_Lower": font_small.render(text_to_display.lower(), True, TEXT_COLOR),
                "X_Small_Upper": font_x_small.render(text_to_display.upper(), True, TEXT_COLOR),
                "X_Small_Lower": font_x_small.render(text_to_display.lower(), True, TEXT_COLOR),
                "Large_Bold_Upper": font_large_bold.render(text_to_display.upper(), True, TEXT_COLOR),
                "Large_Bold_Lower": font_large_bold.render(text_to_display.lower(), True, TEXT_COLOR),
                "Small_Bold_Upper": font_small_bold.render(text_to_display.upper(), True, TEXT_COLOR),
                "Small_Bold_Lower": font_small_bold.render(text_to_display.lower(), True, TEXT_COLOR),
                "X_Small_Bold_Upper": font_x_small_bold.render(text_to_display.upper(), True, TEXT_COLOR),
                "X_Small_Bold_Lower": font_x_small_bold.render(text_to_display.lower(), True, TEXT_COLOR),
                "Large_Italic_Upper": font_large_italic.render(text_to_display.upper(), True, TEXT_COLOR),
                "Large_Italic_Lower": font_large_italic.render(text_to_display.lower(), True, TEXT_COLOR),
                "Small_Italic_Upper": font_small_italic.render(text_to_display.upper(), True, TEXT_COLOR),
                "Small_Italic_Lower": font_small_italic.render(text_to_display.lower(), True, TEXT_COLOR),
                "X_Small_Italic_Upper": font_x_small_italic.render(text_to_display.upper(), True, TEXT_COLOR),
                "X_Small_Italic_Lower": font_x_small_italic.render(text_to_display.lower(), True, TEXT_COLOR),
            }

            # Define positions for text variations
            text_positions = {
                "Large_Upper": (10, 20),
                "Large_Lower": (10, 60),
                "Small_Upper": (10, 110),
                "Small_Lower": (10, 140),
                "X_Small_Upper": (10, 175),
                "X_Small_Lower": (10, 190),
                "Large_Bold_Upper": (10, 220),
                "Large_Bold_Lower": (10, 260),
                "Small_Bold_Upper": (10, 310),
                "Small_Bold_Lower": (10, 340),
                "X_Small_Bold_Upper": (10, 375),
                "X_Small_Bold_Lower": (10, 390),
                "Large_Italic_Upper": (10, 420),
                "Large_Italic_Lower": (10, 460),
                "Small_Italic_Upper": (10, 510),
                "Small_Italic_Lower": (10, 540),
                "X_Small_Italic_Upper": (10, 575),
                "X_Small_Italic_Lower": (10, 590),
            }

            # Display text on the screen
            for variation, text_surface in text_variations.items():
                screen.blit(text_surface, text_positions[variation])

            pygame.display.flip()

    pygame.quit()

# Tkinter GUI
def open_font_dialog():
    global font_path
    file_path = filedialog.askopenfilename(
        initialdir=os.path.abspath(os.path.dirname(__file__)),
        title="Select Font File",
        filetypes=[("Font Files", "*.ttf *.otf")]
    )
    if file_path:
        font_path = file_path
        update_display_font()

def switch_text():
    global text_to_display
    max_characters = 11  # Set the maximum number of characters here
    new_text = simpledialog.askstring("Input", f"Enter new text (max {max_characters} characters):", parent=root)
    if new_text:
        text_to_display = new_text[:max_characters]
        update_display_font()

def create_gui():
    global root
    root = tk.Tk()
    root.title("Font Helper")

    # Calculate one-fifth of the screen height
    screen_height = root.winfo_screenheight()
    tkinter_window_height = screen_height // 10

    # Set the position of the Tkinter window in the top-left corner and one-fifth of the screen height
    root.geometry(f"{WINDOW_WIDTH}x{tkinter_window_height}+0+0")

    select_font_button = tk.Button(root, text="Load Font", command=open_font_dialog)
    select_font_button.pack()

    switch_text_button = tk.Button(root, text="Change Text", command=switch_text)
    switch_text_button.pack()

    root.mainloop()

# Function to update the font and display text in the Pygame window
def update_display_font():
    with font_thread_lock:
        font_thread_queue.put("reload_font")

# Start Pygame thread
font_thread_running = True
font_thread_queue = queue.Queue()
font_thread = threading.Thread(target=pygame_thread)
font_thread.start()

# Start Tkinter GUI
create_gui()

# Clean up when Tkinter GUI closes
font_thread_running = False
font_thread.join()