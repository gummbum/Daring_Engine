import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
OUTER_RADIUS = 200
GROWTH_RATE = 5  # You can adjust this rate as needed
BG_COLOR = (0, 0, 0)
CIRCLE_COLOR = (255, 255, 255)

# Create a window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Expanding Circle")

# Initialize variables
circle_radius = 0

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill(BG_COLOR)

    # Draw the expanding circle
    pygame.draw.circle(screen, CIRCLE_COLOR, (WIDTH // 2, HEIGHT // 2), circle_radius, 2)

    # Update the circle's radius
    circle_radius += GROWTH_RATE

    # Check if the circle has reached the desired outer radius
    if circle_radius >= OUTER_RADIUS:
        circle_radius = OUTER_RADIUS

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    pygame.time.delay(10)

# Quit Pygame
pygame.quit()
sys.exit()