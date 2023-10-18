import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 8  # Adjust this to your grid size
FPS = 120
PUCK_RADIUS = 8
COLLISION_RADIUS = 7  # Set your desired collision radius here
PUCK_COUNT = 50
MAX_LIVES = 100  # Maximum number of lives

# Colors
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)  # Blue color for walls

# Calculate the border thickness based on grid size
GRID_BORDER = GRID_SIZE  # You can adjust this to control the border thickness

# Pygame setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Puck-Wall Collision Simulation")
clock = pygame.time.Clock()

# Minimum velocity threshold (you can adjust this value)
MIN_VELOCITY_THRESHOLD = 1.33

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

        # Create a rect for collision detection
        self.rect = pygame.Rect(x - collision_radius, y - collision_radius, collision_radius * 2, collision_radius * 2)

        # Create a surface for the mask and draw a circle on it
        mask_surface = pygame.Surface((collision_radius * 2, collision_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(mask_surface, BLACK, (collision_radius, collision_radius), collision_radius)
        self.mask = pygame.mask.from_surface(mask_surface)

# Class for a zone that affects puck friction
class FrictionZone:
    def __init__(self, x, y, width, height, friction):
        self.rect = pygame.Rect(x, y, width, height)
        self.friction = friction

    def apply_friction(self, puck):
        if self.rect.colliderect(puck.rect):
            puck.vx *= self.friction
            puck.vy *= self.friction

    def set_friction(self, new_friction):
        self.friction = new_friction

class KillBox:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.mask = pygame.mask.from_surface(pygame.Surface((width, height), pygame.SRCALPHA))

    def check_collision(self, puck):
        offset = (int(puck.x - self.rect.left), int(puck.y - self.rect.top))
        if self.mask.overlap(puck.mask, offset):
            puck.active = False

# Class for a zone that boosts puck velocity
class Booster:
    def __init__(self, x, y, width, height, boost_velocity):
        self.rect = pygame.Rect(x, y, width, height)
        self.boost_velocity = boost_velocity
        self.pucks_passed = set()  # To track which pucks have already received the boost

    def apply_boost(self, puck):
        if self.rect.colliderect(puck.rect) and puck not in self.pucks_passed:
            puck.vx += self.boost_velocity
            self.pucks_passed.add(puck)

    def set_boost_velocity(self, new_boost_velocity):
        self.boost_velocity = new_boost_velocity

# Function to reset the simulation
def reset_simulation(pucks):
    # Reset the pucks
    pucks.clear()
    for _ in range(PUCK_COUNT):
        while True:
            x = random.randint(PUCK_RADIUS + GRID_BORDER, WIDTH - PUCK_RADIUS - GRID_BORDER)
            y = random.randint(PUCK_RADIUS + GRID_BORDER, HEIGHT - PUCK_RADIUS - GRID_BORDER)
            valid_spawn = True
            for puck in pucks:
                if math.sqrt((puck.x - x) ** 2 + (puck.y - y) ** 2) < 2 * COLLISION_RADIUS:
                    valid_spawn = False
                    break
            if valid_spawn:
                break
        vx = random.uniform(-200, 200)
        vy = random.uniform(-200, 200)
        # Ensure that vx and vy have a minimum absolute value in both directions
        if abs(vx) < MIN_VELOCITY_THRESHOLD:
            vx = MIN_VELOCITY_THRESHOLD if vx < 0 else -MIN_VELOCITY_THRESHOLD

        if abs(vy) < MIN_VELOCITY_THRESHOLD:
            vy = MIN_VELOCITY_THRESHOLD if vy < 0 else -MIN_VELOCITY_THRESHOLD

        mass = 6
        pucks.append(Puck(x, y, vx, vy, mass, PUCK_RADIUS, COLLISION_RADIUS))

# Initialize lives
lives = MAX_LIVES

# Initial reset
pucks = []
reset_simulation(pucks)

# Create FrictionZone, KillBox, and Booster instances
friction_zone = FrictionZone(100, 100, 200, 50, 0.95)  # Example: x, y, width, height, friction
kill_box = KillBox(400, 400, 100, 100)  # Example: x, y, width, height
booster = Booster(600, 300, 50, 150, 40)  # Example: x, y, width, height, boost_velocity

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

    # Apply friction from FrictionZone
    for puck in pucks:
        friction_zone.apply_friction(puck)

    # Check for collisions with KillBox
    for puck in pucks:
        kill_box.check_collision(puck)

    # Apply boost from Booster
    for puck in pucks:
        booster.apply_boost(puck)

    # Move and update pucks
    for puck in pucks:
        if puck.active:
            # Apply friction to gradually decrease velocity
            puck.vx *= 0.991
            puck.vy *= 0.991

            # Update puck position based on velocity
            puck.x += puck.vx * dt
            puck.y += puck.vy * dt

            # Check for wall collisions
            if (puck.x - puck.radius < GRID_BORDER) and puck.vx < 0:
                puck.vx = -puck.vx
            elif (puck.x + puck.radius > WIDTH - GRID_BORDER) and puck.vx > 0:
                puck.vx = -puck.vx

            if (puck.y - puck.radius < GRID_BORDER) and puck.vy < 0:
                puck.vy = -puck.vy
            elif (puck.y + puck.radius > HEIGHT - GRID_BORDER) and puck.vy > 0:
                puck.vy = -puck.vy

            # Check for inactivity based on velocity magnitude
            velocity_magnitude = math.sqrt(puck.vx ** 2 + puck.vy ** 2)
            if velocity_magnitude < MIN_VELOCITY_THRESHOLD:
                puck.active = False

    # Clear the screen and draw walls in blue
    screen.fill(WHITE)
    pygame.draw.rect(screen, BLUE, (0, 0, WIDTH, GRID_BORDER))  # Top wall
    pygame.draw.rect(screen, BLUE, (0, 0, GRID_BORDER, HEIGHT))  # Left wall
    pygame.draw.rect(screen, BLUE, (0, HEIGHT - GRID_BORDER, WIDTH, GRID_BORDER))  # Bottom wall
    pygame.draw.rect(screen, BLUE, (WIDTH - GRID_BORDER, 0, GRID_BORDER, HEIGHT))  # Right wall

    # Draw highlighted borders for the zones
    pygame.draw.rect(screen, YELLOW, friction_zone.rect, 2)  # Red border for FrictionZone
    pygame.draw.rect(screen, RED, kill_box.rect, 2)  # Green border for KillBox
    pygame.draw.rect(screen, GREEN, booster.rect, 2)  # Yellow border for Booster

    # Draw active pucks
    for puck in pucks:
        if puck.active:
            pygame.draw.circle(screen, BLACK, (int(puck.x), int(puck.y)), puck.radius)

    # Remove inactive pucks
    pucks = [puck for puck in pucks if puck.active]

    # If all pucks are inactive, reset the simulation
    if not pucks:
        lives -= 1
        if lives > 0:
            reset_simulation(pucks)
        else:
            running = False  # No more lives, stop the simulation

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()