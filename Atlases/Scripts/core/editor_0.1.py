import os
import struct
import pygame

# Constants for grid cell size and grid dimensions
CELL_SIZE = 8
GRID_WIDTH = 800  # Adjust as needed
GRID_HEIGHT = 600  # Adjust as needed

# Initialize an empty grid
grid_width_cells = GRID_WIDTH // CELL_SIZE
grid_height_cells = GRID_HEIGHT // CELL_SIZE
grid_data = [[0] * grid_width_cells for _ in range(grid_height_cells)]

# Initialize pygame
pygame.init()

# Create the main display surface
screen = pygame.display.set_mode((GRID_WIDTH, GRID_HEIGHT))
pygame.display.set_caption("Grid Drawing App")

# Create drawing options (0, 1, 2, 3, 4) as colors
colors = [(255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255)]
draw_option = 0  # Initial draw option

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            x //= CELL_SIZE
            y //= CELL_SIZE
            if 0 <= x < grid_width_cells and 0 <= y < grid_height_cells:
                grid_data[y][x] = draw_option
        elif event.type == pygame.KEYDOWN:
            if pygame.K_0 <= event.key <= pygame.K_4:
                draw_option = event.key - pygame.K_0

    # Draw the grid based on the grid_data
    for y in range(grid_height_cells):
        for x in range(grid_width_cells):
            pygame.draw.rect(
                screen,
                colors[grid_data[y][x]],
                (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE),
            )

    pygame.display.flip()

# Save the grid data to a binary file
def save_grid_data():
    save_folder = "your_folder_path_here"  # Specify your folder path
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    file_name = os.path.join(save_folder, "grid_data.bin")

    with open(file_name, "wb") as file:
        for row in grid_data:
            for cell in row:
                binary_value = struct.pack("i", cell)
                file.write(binary_value)

save_grid_data()
pygame.quit()