import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 8
FPS = 60
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
RED = (255, 0, 0)
PUCK_RADIUS = 10
COLLISION_RADIUS = 8  # Set your desired collision radius here
PUCK_COUNT = 30

# Pygame setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Puck-Wall Collision Simulation")
clock = pygame.time.Clock()

# Minimum velocity threshold (you can adjust this value)
MIN_VELOCITY_THRESHOLD = 1.2

# Function to check pixel-perfect collision between pucks with slipperiness and edge nudge
def check_pixel_perfect_collision(puck1, puck2):
    # Calculate the offset between the two pucks
    offset = (int(puck2.x - puck1.x), int(puck2.y - puck1.y))
    
    # Calculate the overlap area between the masks
    overlap = puck1.mask.overlap_area(puck2.mask, offset)
    
    # Check if there's a collision
    if overlap > 0:
        # Calculate the distance between the centers of the pucks
        distance = math.sqrt((puck2.x - puck1.x) ** 2 + (puck2.y - puck1.y) ** 2)
        
        # If the pucks' centers are very close, nudge them slightly away
        if distance < 2 * puck1.collision_radius:
            # Calculate the unit vector between the centers
            dx = puck2.x - puck1.x
            dy = puck2.y - puck1.y
            norm = math.sqrt(dx ** 2 + dy ** 2)
            if norm != 0:
                dx /= norm
                dy /= norm
            
            # Nudge the pucks away from each other
            nudging_distance = (2 * puck1.collision_radius - distance) / 2
            puck1.x -= dx * nudging_distance
            puck1.y -= dy * nudging_distance
            puck2.x += dx * nudging_distance
            puck2.y += dy * nudging_distance
        
        # Perform collision resolution without slipperiness
        dx = puck2.x - puck1.x
        dy = puck2.y - puck1.y
        normal = math.sqrt(dx ** 2 + dy ** 2)
        nx = dx / normal
        ny = dy / normal
        relative_vel_x = puck1.vx - puck2.vx
        relative_vel_y = puck1.vy - puck2.vy
        dot_product = relative_vel_x * nx + relative_vel_y * ny
        impulse = (2 * dot_product) / (puck1.mass + puck2.mass)
        
        # Apply slipperiness to the impulse
        slipperiness = 0.9  # You can adjust this value
        impulse *= slipperiness
        
        # Update velocities
        puck1.vx -= impulse * puck2.mass * nx
        puck1.vy -= impulse * puck2.mass * ny
        puck2.vx += impulse * puck1.mass * nx
        puck2.vy += impulse * puck1.mass * ny

# Puck class
class Puck:
    def __init__(self, x, y, vx, vy, mass, drawn_radius, collision_radius):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.mass = mass
        self.radius = drawn_radius  # Drawn radius
        self.collision_radius = collision_radius  # Collision radius
        self.active = True

        # Create a surface for the mask and draw a circle on it
        mask_surface = pygame.Surface((collision_radius * 2, collision_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(mask_surface, BLACK, (collision_radius, collision_radius), collision_radius)
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
        result = self.mask.overlap(other.mask, offset, slipperiness=0.9)
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

# Set the minimum value threshold
min_value = 20  # You can adjust this threshold as needed

# Create pucks with no overlap
pucks = []
for _ in range(PUCK_COUNT):
    while True:
        x = random.randint(PUCK_RADIUS, WIDTH - PUCK_RADIUS)
        y = random.randint(PUCK_RADIUS, HEIGHT - PUCK_RADIUS)
        valid_spawn = True
        for puck in pucks:
            if math.sqrt((puck.x - x) ** 2 + (puck.y - y) ** 2) < 2 * COLLISION_RADIUS:
                valid_spawn = False
                break
        if valid_spawn:
            break
    vx = random.uniform(-60, 60)
    vy = random.uniform(-60, 60)
    # Ensure that vx and vy have a minimum absolute value in both directions
    if abs(vx) < MIN_VELOCITY_THRESHOLD:
        vx = MIN_VELOCITY_THRESHOLD if vx < 0 else -MIN_VELOCITY_THRESHOLD

    if abs(vy) < MIN_VELOCITY_THRESHOLD:
        vy = MIN_VELOCITY_THRESHOLD if vy < 0 else -MIN_VELOCITY_THRESHOLD
    
    mass = 12
    pucks.append(Puck(x, y, vx, vy, mass, PUCK_RADIUS, COLLISION_RADIUS))

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

    # Handle puck collisions using pixel-perfect collision check
    for i in range(len(pucks)):
        for j in range(i + 1, len(pucks)):
            if pucks[i].active and pucks[j].active:
                check_pixel_perfect_collision(pucks[i], pucks[j])

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
            pygame.draw.circle(screen, BLACK, (int(puck.x), int(puck.y)), PUCK_RADIUS)

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
            mass = 12
            pucks.append(Puck(x, y, vx, vy, mass, PUCK_RADIUS))

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()