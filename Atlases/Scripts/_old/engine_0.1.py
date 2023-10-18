import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 8
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 60
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PUCK_RADIUS = 10
PUCK_COUNT = 30

# Pygame setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Puck-Wall Collision Simulation")
clock = pygame.time.Clock()

# Grid setup
grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# Minimum velocity threshold (you can adjust this value)
MIN_VELOCITY_THRESHOLD = 1.2

# Puck class
class Puck:
    def __init__(self, x, y, vx, vy, mass, radius):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.mass = mass
        self.radius = radius
        self.active = True

        # Create a surface for the mask and draw a circle on it
        mask_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(mask_surface, RED, (radius, radius), radius)
        self.mask = pygame.mask.from_surface(mask_surface)

    def move(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Check velocity threshold and set to zero if below
        if abs(self.vx) < MIN_VELOCITY_THRESHOLD:
            self.vx = 0
        if abs(self.vy) < MIN_VELOCITY_THRESHOLD:
            self.vy = 0

    def check_collision(self, other):
        offset = (int(other.x - self.x), int(other.y - self.y))
        result = self.mask.overlap(other.mask, offset)
        return result is not None

    def handle_collision(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        normal = math.sqrt(dx ** 2 + dy ** 2)
        nx = dx / normal
        ny = dy / normal
        relative_vel_x = self.vx - other.vx
        relative_vel_y = self.vy - other.vy
        dot_product = relative_vel_x * nx + relative_vel_y * ny
        impulse = (2 * dot_product) / (self.mass + other.mass)
        self.vx -= impulse * other.mass * nx
        self.vy -= impulse * other.mass * ny
        other.vx += impulse * self.mass * nx
        other.vy += impulse * self.mass * ny

# Wall class
class Wall:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

# Friction coefficient (you can adjust this value)
FRICTION_COEFFICIENT = 0.991

# Create pucks with no overlap
pucks = []
for _ in range(PUCK_COUNT):
    while True:
        x = random.randint(PUCK_RADIUS, WIDTH - PUCK_RADIUS)
        y = random.randint(PUCK_RADIUS, HEIGHT - PUCK_RADIUS)
        valid_spawn = True
        for puck in pucks:
            if math.sqrt((puck.x - x) ** 2 + (puck.y - y) ** 2) < PUCK_RADIUS * 2:
                valid_spawn = False
                break
        if valid_spawn:
            break
    vx = random.uniform(-60, 60)
    vy = random.uniform(-60, 60)
    mass = random.uniform(1, 5)
    pucks.append(Puck(x, y, vx, vy, mass, PUCK_RADIUS))

# Create walls
walls = []
# Top wall
walls.append(Wall(0, 0, WIDTH, GRID_SIZE))
# Bottom wall
walls.append(Wall(0, HEIGHT - GRID_SIZE, WIDTH, GRID_SIZE))
# Left wall
walls.append(Wall(0, GRID_SIZE, GRID_SIZE, HEIGHT - 2 * GRID_SIZE))
# Right wall
walls.append(Wall(WIDTH - GRID_SIZE, GRID_SIZE, GRID_SIZE, HEIGHT - 2 * GRID_SIZE))

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    dt = clock.tick(FPS) / 120.0

    # Handle puck collisions
    for i in range(len(pucks)):
        for j in range(i + 1, len(pucks)):
            if pucks[i].active and pucks[j].active and pucks[i].check_collision(pucks[j]):
                pucks[i].handle_collision(pucks[j])

    # Move and update pucks
    for puck in pucks:
        if puck.active:
            puck.move(dt)

            # Apply friction to gradually decrease velocity
            puck.vx *= FRICTION_COEFFICIENT
            puck.vy *= FRICTION_COEFFICIENT

            # Check for edge-of-screen collisions
            if (puck.x - puck.radius < 0) or (puck.x + puck.radius > WIDTH):
                puck.vx = -puck.vx
            if (puck.y - puck.radius < 0) or (puck.y + puck.radius > HEIGHT):
                puck.vy = -puck.vy

            # If velocity is very small, consider the puck inactive
            if abs(puck.vx) < 0.1 and abs(puck.vy) < 0.1:
                puck.active = False

    # Clear the screen
    screen.fill(WHITE)

    # Draw walls
    for wall in walls:
        pygame.draw.rect(screen, RED, (wall.x, wall.y, wall.width, wall.height))

    # Draw active pucks
    for puck in pucks:
        if puck.active:
            pygame.draw.circle(screen, RED, (int(puck.x), int(puck.y)), PUCK_RADIUS)

    # Remove inactive pucks
    pucks = [puck for puck in pucks if puck.active]

    # If all pucks are inactive, reset the simulation
    if not pucks:
        pucks = []
        for _ in range(PUCK_COUNT):
            x = random.randint(PUCK_RADIUS, WIDTH - PUCK_RADIUS)
            y = random.randint(PUCK_RADIUS, HEIGHT - PUCK_RADIUS)
            vx = random.uniform(-60, 60)
            vy = random.uniform(-60, 60)
            mass = 2
            pucks.append(Puck(x, y, vx, vy, mass, PUCK_RADIUS))

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()