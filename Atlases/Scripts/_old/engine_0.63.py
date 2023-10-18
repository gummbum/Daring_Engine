import pygame
import sys
import random
import math

pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600      # Adjust this to your screen size (pixels)
GRID_SIZE = 8                 # Adjust this to your grid cell size (pixels)
FPS = 120                     # Frames per second
PUCK_RADIUS = 8               # Drawn radius (pixels)
COLLISION_RADIUS = 7          # Set your desired collision radius here (pixels)
GRID_BORDER = GRID_SIZE       # Calculate the border thickness based on grid size
MIN_VELOCITY_THRESHOLD = 1.33 # Minimum velocity threshold
PUCK_COUNT = 20
MAX_LIVES = 100
# Colors
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
RED = (255, 0, 0)
PINK = (255, 0, 200)
PURPLE = (120, 0, 200)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
BABY = (50, 50, 150)
BROWN = (210, 100, 0)

# Pygame setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Puck-Wall Collision Simulation")
clock = pygame.time.Clock()

# Modify the entity_collision function
def entity_collision(entity1, entity2):
    offset = (int(entity2.x - entity1.x), int(entity2.y - entity1.y))

    if entity1.mask.overlap(entity2.mask, offset):
        distance = math.sqrt((entity2.x - entity1.x) ** 2 + (entity2.y - entity1.y) ** 2)

        if distance < 2 * entity1.collision_radius:
            dx = entity2.x - entity1.x
            dy = entity2.y - entity1.y
            norm = math.sqrt(dx ** 2 + dy ** 2)
            if norm != 0:
                dx /= norm
                dy /= norm

            nudging_distance = (2 * entity1.collision_radius - distance) / 4
            entity1.x -= dx * nudging_distance
            entity1.y -= dy * nudging_distance
            entity2.x += dx * nudging_distance
            entity2.y += dy * nudging_distance

        dx = entity2.x - entity1.x
        dy = entity2.y - entity1.y
        normal = math.sqrt(dx ** 2 + dy ** 2)
        nx = dx / normal
        ny = dy / normal
        relative_vel_x = entity1.vx - entity2.vx
        relative_vel_y = entity1.vy - entity2.vy
        dot_product = relative_vel_x * nx + relative_vel_y * ny
        impulse = (2 * dot_product) / (entity1.mass + entity2.mass)

        slipperiness = 0.9  # You can adjust this value
        impulse *= slipperiness

        # Check if the collision is from the outside
        if dot_product > 0:
            entity1.vx -= impulse * entity2.mass * nx
            entity1.vy -= impulse * entity2.mass * ny
            entity2.vx += impulse * entity1.mass * nx
            entity2.vy += impulse * entity1.mass * ny

def rand_angle():
    rand_angle = random.randint(0,360)
    return rand_angle

"""
Classes for player, entities, spawners, zones, and other objects:
vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
# TODO: Finish DuckState
class DuckState():
    def __init__(self, x, y, vx, vy, drawn_radius):
        return

class SpawnerBox:
    def __init__(self, x, y, width, height, drawn_color, collision_color, spawn_cooldown=1000, initial_spawn_delay=0):
        self.rect = pygame.Rect(x, y, width, height)
        self.drawn_color = drawn_color
        self.collision_color = collision_color
        self.velocity_x = 0
        self.velocity_y = 0
        self.mass = 0
        self.angle = 0
        self.spawn_cooldown = spawn_cooldown  # Cooldown time between puck spawns in milliseconds
        self.initial_spawn_delay = initial_spawn_delay  # Delay before the first spawn in milliseconds
        self.last_spawn_time = pygame.time.get_ticks()
        self.has_spawned_initial_puck = False

    def set_parameters(self, velocity_x, velocity_y, mass, angle):
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.mass = mass
        self.angle = angle
    
    def spawn_puck(self, pucks, dt):
        current_time = pygame.time.get_ticks()
        
        # TODO: Fix the initial puck spawn. When initial puck is fired it should skip the first puck fired after cooldown.
        if not self.has_spawned_initial_puck and current_time >= self.initial_spawn_delay:
            # Initial puck spawn after the initial delay
            x = self.rect.centerx
            y = self.rect.centery
            angle_rad = math.radians(self.angle)
            vx = self.velocity_x * math.cos(angle_rad)
            vy = self.velocity_y * math.sin(angle_rad)
            pucks.append(Puck(x, y, vx, vy, self.mass, PUCK_RADIUS, COLLISION_RADIUS))
            self.last_spawn_time = current_time
            self.has_spawned_initial_puck = True
        elif current_time - self.last_spawn_time >= self.spawn_cooldown:
            # Regular puck spawn after the cooldown period
            x = self.rect.centerx
            y = self.rect.centery
            angle_rad = math.radians(self.angle)
            vx = self.velocity_x * math.cos(angle_rad)
            vy = self.velocity_y * math.sin(angle_rad)
            pucks.append(Puck(x, y, vx, vy, self.mass, PUCK_RADIUS, COLLISION_RADIUS))
            self.last_spawn_time = current_time

    def spawn_static_puck(self, static_pucks, dt):
        current_time = pygame.time.get_ticks()
    
        if not self.has_spawned_initial_puck and current_time >= self.initial_spawn_delay:
            # Initial puck spawn after the initial delay
            x = self.rect.centerx
            y = self.rect.centery
            angle_rad = math.radians(self.angle)
            vx = self.velocity_x * math.cos(angle_rad)
            vy = self.velocity_y * math.sin(angle_rad)
            static_pucks.append(StaticPuck(x, y, vx, vy, self.mass, PUCK_RADIUS, COLLISION_RADIUS))
            self.last_spawn_time = current_time
            self.has_spawned_initial_puck = True
            print("Initial static puck spawned.")  # Add this line for debugging
        elif current_time - self.last_spawn_time >= self.spawn_cooldown:
            # Regular puck spawn after the cooldown period
            x = self.rect.centerx
            y = self.rect.centery
            angle_rad = math.radians(self.angle)
            vx = self.velocity_x * math.cos(angle_rad)
            vy = self.velocity_y * math.sin(angle_rad)
            static_pucks.append(StaticPuck(x, y, vx, vy, self.mass, PUCK_RADIUS, COLLISION_RADIUS))
            self.last_spawn_time = current_time
            print("Regular static puck spawned.")  # Add this line for debugging

    # TODO: Add support for spawning ice_cubes, static_pucks or pucks based on parameter input when it is instantiated.
        # TODO: It should have presets to instantiate either a cube spawner or puck spawner, all the other parameters stay the same.
        # IceCubes will be able to be spawned stationary, at 0 for the x and y velocity.

    def reset_initial_spawn_timer(self):
        self.has_spawned_initial_puck = False

class Entity:
    def __init__(self, x, y, vx, vy, mass, drawn_radius, collision_radius):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.mass = mass
        self.radius = drawn_radius
        self.collision_radius = collision_radius
        self.active = True

        self.rect = pygame.Rect(x - collision_radius, y - collision_radius, collision_radius * 2, collision_radius * 2)
        
        mask_surface = pygame.Surface((collision_radius * 2, collision_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(mask_surface, BLACK, (collision_radius, collision_radius), collision_radius)
        self.mask = pygame.mask.from_surface(mask_surface)

    def entity_collision(self, other_entity):
        offset = (int(other_entity.x - self.x), int(other_entity.y - self.y))
        return self.mask.overlap(other_entity.mask, offset)

class Puck(Entity):
    def __init__(self, x, y, vx, vy, mass, drawn_radius, collision_radius):
        super().__init__(x, y, vx, vy, mass, drawn_radius, collision_radius)

class StaticPuck(Entity):
    def __init__(self, x, y, vx, vy, mass, drawn_radius, collision_radius):
        super().__init__(x, y, vx, vy, mass, drawn_radius, collision_radius)

# TODO: Fix this entity !!!
# TODO: Ice Cubes can only be turned inactive by kill_boxes! (they should be able to remain stationary when velocity is low or non-existent)
class IceCube(Entity):
    def __init__(self, x, y , vx, vy, mass, width, height, drawn_color, collision_color):
        super().__init__(x, y, vx, vy, mass, 0, 0, 0, 0, 0)
        self.width = width
        self.height = height
        self.drawn_color = drawn_color
        self.collision_color = collision_color

        self.rect = pygame.Rect(x, y, width, height)

        drawn_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(drawn_surface, drawn_color, (0, 0, width, height))
        self.drawn_mask = pygame.mask.from_surface(drawn_surface)

        collision_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(collision_surface, collision_color, (0, 0, width, height))
        self.collision_mask = pygame.mask.from_surface(collision_surface)

class Zone(Entity):
    def __init__(self, x, y, width, height, drawn_color, collision_color):
        super().__init__(x, y, 0, 0, 0, 0, 0)
        self.width = width
        self.height = height
        self.drawn_color = drawn_color
        self.collision_color = collision_color

        self.rect = pygame.Rect(x, y, width, height)

        drawn_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(drawn_surface, drawn_color, (0, 0, width, height))
        self.drawn_mask = pygame.mask.from_surface(drawn_surface)

        collision_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(collision_surface, collision_color, (0, 0, width, height))
        self.collision_mask = pygame.mask.from_surface(collision_surface)

# TODO: Make multiple shape options for FrictionZone dimensional parameters, ie. circular and triangular as well as the rectangle that already exists.
    #  TODO: Each of these options should be named and referenced respectively, ie. circle, rectangle, and triangle.
class FrictionZone(Zone):
    def __init__(self, x, y, width, height, friction):
        super().__init__(x, y, width, height, RED, GREEN)
        self.friction = friction

    def apply_friction(self, puck):
        puck_left = puck.x - puck.radius
        puck_right = puck.x + puck.radius
        puck_top = puck.y - puck.radius
        puck_bottom = puck.y + puck.radius

        box_left = self.rect.left
        box_right = self.rect.right
        box_top = self.rect.top
        box_bottom = self.rect.bottom

        puck_overlap_x = max(0, min(puck_right, box_right) - max(puck_left, box_left))
        puck_overlap_y = max(0, min(puck_bottom, box_bottom) - max(puck_top, box_top))

        puck_overlap_area = puck_overlap_x * puck_overlap_y
        puck_area = math.pi * (puck.radius ** 2)

        if puck_overlap_area >= 0.33 * puck_area:
            # Apply friction to the puck's velocities
            puck.vx *= self.friction
            puck.vy *= self.friction

    def apply_static_friction(self, static_puck):
        static_puck_left = static_puck.x - static_puck.radius
        static_puck_right = static_puck.x + static_puck.radius
        static_puck_top = static_puck.y - static_puck.radius
        static_puck_bottom = static_puck.y + static_puck.radius

        box_left = self.rect.left
        box_right = self.rect.right
        box_top = self.rect.top
        box_bottom = self.rect.bottom

        static_puck_overlap_x = max(0, min(static_puck_right, box_right) - max(static_puck_left, box_left))
        static_puck_overlap_y = max(0, min(static_puck_bottom, box_bottom) - max(static_puck_top, box_top))

        static_puck_overlap_area = static_puck_overlap_x * static_puck_overlap_y
        static_puck_area = math.pi * (static_puck.radius ** 2)

        if static_puck_overlap_area >= 0.33 * static_puck_area:
            # Apply friction to the puck's velocities
            static_puck.vx *= self.friction
            static_puck.vy *= self.friction


# TODO: Make multiple shape options for KillBox dimensional parameters, ie. circular and triangular as well as the rectangle that already exists.
    #  TODO: Each of these options should be named and referenced respectively, ie. circle, rectangle, and triangle.
class KillBox(Zone):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, BLACK, WHITE)

    def check_collision(self, puck):
        puck_left = puck.x - puck.radius
        puck_right = puck.x + puck.radius
        puck_top = puck.y - puck.radius
        puck_bottom = puck.y + puck.radius

        box_left = self.rect.left
        box_right = self.rect.right
        box_top = self.rect.top
        box_bottom = self.rect.bottom

        puck_overlap_x = max(0, min(puck_right, box_right) - max(puck_left, box_left))
        puck_overlap_y = max(0, min(puck_bottom, box_bottom) - max(puck_top, box_top))

        puck_overlap_area = puck_overlap_x * puck_overlap_y
        puck_area = math.pi * (puck.radius ** 2)

        if puck_overlap_area >= 0.60 * puck_area:
            puck.active = False

    def check_static_collision(self, static_puck):
        static_puck_left = static_puck.x - static_puck.radius
        static_puck_right = static_puck.x + static_puck.radius
        static_puck_top = static_puck.y - static_puck.radius
        static_puck_bottom = static_puck.y + static_puck.radius

        box_left = self.rect.left
        box_right = self.rect.right
        box_top = self.rect.top
        box_bottom = self.rect.bottom

        static_puck_overlap_x = max(0, min(static_puck_right, box_right) - max(static_puck_left, box_left))
        static_puck_overlap_y = max(0, min(static_puck_bottom, box_bottom) - max(static_puck_top, box_top))

        static_puck_overlap_area = static_puck_overlap_x * static_puck_overlap_y
        static_puck_area = math.pi * (static_puck.radius ** 2)

        if static_puck_overlap_area >= 0.60 * static_puck_area:
            static_puck.active = False


# TODO: Add a DirBooster class that acts as booster but overrides the pucks current velocity and direction, applies a small amount of friction,
# TODO: and sets desired velocity and direction to pucks that cross its threshold (boost_dir is an angle out of 360) (one direction boosters).
"""
class DirBooster(Zone):
    def __init__(self, x, y, width, height, boost_dir, boost_velocity):
        super().__init__(x, y, width, height, YELLOW, BLUE)
        self.boost_dir = boost_dir
        self.boost_velocity = boost_velocity
        self.pucks_passed = set()
"""

# TODO: Make multiple shape options for FrictionZone dimensional parameters, ie. triangular as well as the rectangle that already exists.
    #  TODO: Each of these options should be named and referenced respectively, ie. rectangle and triangle.
class Booster(Zone):
    def __init__(self, x, y, width, height, boost_velocity):
        super().__init__(x, y, width, height, YELLOW, BLUE)
        self.boost_velocity = boost_velocity
        self.pucks_passed = set()
        self.static_pucks_passed = set()

    def apply_boost(self, puck):
        puck_left = puck.x - puck.radius
        puck_right = puck.x + puck.radius
        puck_top = puck.y - puck.radius
        puck_bottom = puck.y + puck.radius

        box_left = self.rect.left
        box_right = self.rect.right
        box_top = self.rect.top
        box_bottom = self.rect.bottom

        puck_overlap_x = max(0, min(puck_right, box_right) - max(puck_left, box_left))
        puck_overlap_y = max(0, min(puck_bottom, box_bottom) - max(puck_top, box_top))

        puck_overlap_area = puck_overlap_x * puck_overlap_y
        puck_area = math.pi * (puck.radius ** 2)

        if puck_overlap_area >= 0.51 * puck_area:
            # Calculate the direction vector of the puck's current velocity
            velocity_magnitude = math.sqrt(puck.vx ** 2 + puck.vy ** 2)
            if velocity_magnitude != 0:
                dx = puck.vx / velocity_magnitude
                dy = puck.vy / velocity_magnitude

                # Apply the boost in the direction of the current velocity
                puck.vx += self.boost_velocity * dx
                puck.vy += self.boost_velocity * dy

                # Mark the puck as boosted
                self.pucks_passed.add(puck)
            
    def apply_static_boost(self, static_puck):
        static_puck_left = static_puck.x - static_puck.radius
        static_puck_right = static_puck.x + static_puck.radius
        static_puck_top = static_puck.y - static_puck.radius
        static_puck_bottom = static_puck.y + static_puck.radius

        box_left = self.rect.left
        box_right = self.rect.right
        box_top = self.rect.top
        box_bottom = self.rect.bottom

        static_puck_overlap_x = max(0, min(static_puck_right, box_right) - max(static_puck_left, box_left))
        static_puck_overlap_y = max(0, min(static_puck_bottom, box_bottom) - max(static_puck_top, box_top))

        static_puck_overlap_area = static_puck_overlap_x * static_puck_overlap_y
        static_puck_area = math.pi * (static_puck.radius ** 2)

        if static_puck_overlap_area >= 0.51 * static_puck_area:
            # Calculate the direction vector of the puck's current velocity
            velocity_magnitude = math.sqrt(static_puck.vx ** 2 + static_puck.vy ** 2)
            if velocity_magnitude != 0:
                dx = static_puck.vx / velocity_magnitude
                dy = static_puck.vy / velocity_magnitude

                # Apply the boost in the direction of the current velocity
                static_puck.vx += self.boost_velocity * dx
                static_puck.vy += self.boost_velocity * dy

                # Mark the puck as boosted
                self.static_pucks_passed.add(static_puck)

# TODO: Make multiple shape options for magnet dimensional parameters, ie. rectangular and triangular as well as the circle that already exists.
    #  TODO: Each of these options should be named and referenced respectively, ie. circle, rectangle, and triangle.
class Magnet(Zone):
    def __init__(self, x, y, radius, pull_speed, inactivation_threshold, velocity_cap):
        super().__init__(x, y, radius * 2, radius * 2, BLUE, YELLOW)
        self.radius = radius
        self.pull_speed = pull_speed
        self.inactivation_threshold = inactivation_threshold
        self.velocity_cap = velocity_cap  # Maximum velocity allowed inside the magnet zone
        self.magnetized_pucks = set()  # Keep track of magnetized pucks

    def apply_magnetism(self, puck):
        # Calculate the distance between the puck and the center of the magnet
        dx = self.rect.centerx - puck.x
        dy = self.rect.centery - puck.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # Check if the puck is inside the magnet's circular area
        if puck not in self.magnetized_pucks and distance <= self.radius + puck.radius:
            self.magnetized_pucks.add(puck)  # Mark the puck as magnetized

        # Apply magnetism to all magnetized pucks
        for magnetized_puck in self.magnetized_pucks.copy():
            dx = self.rect.centerx - magnetized_puck.x
            dy = self.rect.centery - magnetized_puck.y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            # Calculate the direction vector from the puck to the center of the magnet
            if distance != 0:
                dx /= distance
                dy /= distance

            # Calculate the desired distance from the puck to the center of the magnet
            desired_distance = self.radius - magnetized_puck.radius

            # Cap the velocity if it exceeds the velocity_cap
            velocity_magnitude = math.sqrt(magnetized_puck.vx ** 2 + magnetized_puck.vy ** 2)
            if velocity_magnitude > self.velocity_cap:
                scale_factor = self.velocity_cap / velocity_magnitude
                magnetized_puck.vx *= scale_factor
                magnetized_puck.vy *= scale_factor

            # Move the puck towards the center of the magnet with the specified pull_speed
            move_distance = min(self.pull_speed, desired_distance)
            magnetized_puck.x += dx * move_distance
            magnetized_puck.y += dy * move_distance

            # Check if the puck has reached the center of the magnet
            if distance <= magnetized_puck.radius:
                # Check if the puck's velocity is below the inactivation threshold
                velocity_magnitude = math.sqrt(magnetized_puck.vx ** 2 + magnetized_puck.vy ** 2)
                if velocity_magnitude <= self.inactivation_threshold:
                    magnetized_puck.active = False
                    self.magnetized_pucks.remove(magnetized_puck)  # Remove from magnetized pucks set

# TODO: Fix Inactivity and change to something else and this triggers next level.
class Goal(Zone):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, BLACK, WHITE)

    def check_collision(self, puck):
        puck_left = puck.x - puck.radius
        puck_right = puck.x + puck.radius
        puck_top = puck.y - puck.radius
        puck_bottom = puck.y + puck.radius

        box_left = self.rect.left
        box_right = self.rect.right
        box_top = self.rect.top
        box_bottom = self.rect.bottom

        puck_overlap_x = max(0, min(puck_right, box_right) - max(puck_left, box_left))
        puck_overlap_y = max(0, min(puck_bottom, box_bottom) - max(puck_top, box_top))

        puck_overlap_area = puck_overlap_x * puck_overlap_y
        puck_area = math.pi * (puck.radius ** 2)

        if puck_overlap_area >= 0.99 * puck_area:
            puck.active = False

"""
Functions for resetting, updating, instantiation, and the main loop:
vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
def reset_simulation(pucks, *spawner_boxes):
    pucks.clear()

    # TODO: Add this, move ice_cubes back to initial locations on reset.
    # for ice_cube in ice_cubes:
        # Reset Ice Cubes to initial position and initial velocity !!!
        # return
    
    # TODO: Add this, move static_pucks back to initial locations on reset.
    # for ice_cube in ice_cubes:
        # Reset Ice Cubes to initial position and initial velocity !!!
        # return

    for spawner_box in spawner_boxes:
        spawner_box.reset_initial_spawn_timer()  # Reset the initial spawn delay timer

    for spawner_box in static_spawners:
        spawner_box.reset_initial_spawn_timer()  # Reset the initial spawn delay timer

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
        if abs(vx) < MIN_VELOCITY_THRESHOLD:
            vx = MIN_VELOCITY_THRESHOLD if vx < 0 else -MIN_VELOCITY_THRESHOLD

        if abs(vy) < MIN_VELOCITY_THRESHOLD:
            vy = MIN_VELOCITY_THRESHOLD if vy < 0 else -MIN_VELOCITY_THRESHOLD

        mass = 6
        pucks.append(Puck(x, y, vx, vy, mass, PUCK_RADIUS, COLLISION_RADIUS))

# Initialize lives
lives = MAX_LIVES

"""
Spawn Testing / Debug:
----------------------------------------------------------------
----------------------------------------------------------------
# Angle Chart: (NEGATIVE)
 -  0 = East          (Right)
 - -45 = North-East   (Up-Right)
 - -90 = North        (Up)
 - -135 = North-West  (Up-left)
 - -180 = West        (Left)
 - -225 = South-West  (Down-Left)
 - -270 = South       (Down)
 - -315 = South-East  (Down-Right)
 - -360 = East        (Right)
--------------------------------------------------
# Standard mass for pucks is 6, 3 is light and 12 is Heavy
# Standard mass for ice_cubes is 20
#                               x    y    W   H   Col1   Col2                   mSec                      mSec
spawner_box_zone1 = SpawnerBox(225, 200, 24, 24, PURPLE, PURPLE, spawn_cooldown=3000, initial_spawn_delay=3000)
spawner_box_zone1.set_parameters(velocity_x=50, velocity_y=50, mass=6, angle=50) # Standard velocity

#                               x    y    W   H   Col1   Col2                   mSec                      mSec
spawner_box_zone2 = SpawnerBox(225, 200, 24, 24, PURPLE, PURPLE, spawn_cooldown=3000, initial_spawn_delay=3000)
spawner_box_zone2.set_parameters(velocity_x=100, velocity_y=100, mass=6, angle=50) # Medium velocity

#                               x    y    W   H   Col1   Col2                   mSec                      mSec
spawner_box_zone3 = SpawnerBox(225, 200, 24, 24, PURPLE, PURPLE, spawn_cooldown=3000, initial_spawn_delay=3000)
spawner_box_zone3.set_parameters(velocity_x=150, velocity_y=150, mass=6, angle=50) # High velocity

#                               x    y    W   H   Col1   Col2                   mSec                      mSec
spawner_box_zone4 = SpawnerBox(225, 200, 24, 24, PURPLE, PURPLE, spawn_cooldown=3000, initial_spawn_delay=3000)
spawner_box_zone4.set_parameters(velocity_x=225, velocity_y=225, mass=6, angle=50) # Maximum velocity

# Add spawner_boxes to list
spawner_boxes = [spawner_box_zone1, spawner_box_zone2, spawner_box_zone3, spawner_box_zone4, etc...]
--------------------------------------------------
#                             x    y    W    H     FR
friction_zone = FrictionZone(100, 100, 200, 100, 0.965) # 0.965 is standard heavy friction (faster of the two)

#                              x   y   W    H    FR
friction_zone2 = FrictionZone(692, 8, 100, 100, 0.94) # 0.94 is standard for this zone, very heavy FR (slower of the two)
    # Inside main loop vvv
    # Apply friction from FrictionZone
    for puck in pucks:
        friction_zone.apply_friction(puck)
        friction_zone2.apply_friction(puck)
--------------------------------------------------
#                  x   y    W    H
kill_box = KillBox(8, 468, 124, 124)
    # Inside main loop vvv
    # Check for collisions with KillBox
    for puck in pucks:
        kill_box.check_collision(puck)
-------------------------------------------------- 
#                  x    y    W   H    B
booster = Booster(600, 132, 32, 300, 4.25) # 4.25 is STANDARD boost multiplier

#                  x    y    W   H    B
booster2 = Booster(600, 132, 32, 300, 6.25) # 6.25 is HIGH boost multiplier

#                   x    y    W   H    B 
booster3 = Booster(600, 132, 32, 300, 9.0) # 9.0 is MAXIMUM boost multiplier
    # Inside main loop vvv
    # Apply boost from Booster
    for puck in pucks:
        booster.apply_boost(puck)
--------------------------------------------------
#                x    y    R  PULL   t   vCap
magnet = Magnet(300, 400, 50, 0.12, 1.0, 10.0) # t = inactivation threshold / vCap = velocity cap for puck entry (large radius is 50)

#                x    y    R   PULL   t   vCap
magnet2 = Magnet(300, 400, 33, 0.12, 1.0, 10.0) # t = inactivation threshold / vCap = velocity cap for puck entry (standard radius is 33)

#                x    y    R   PULL   t   vCap
magnet3 = Magnet(300, 400, 33, 0.12, 1.0, 10.0) # t = inactivation threshold / vCap = velocity cap for puck entry (small radius is 16)
    # Inside main loop vvv
    # Apply magnetism from Magnet
    for puck in pucks:
        magnet.apply_magnetism(puck)
--------------------------------------------------
# Inside main loop vvv (drawing)
    # Draw Zones
    pygame.draw.rect(screen, YELLOW, friction_zone.rect, 2)
    pygame.draw.rect(screen, BROWN, friction_zone2.rect, 2)
    pygame.draw.rect(screen, RED, kill_box.rect, 2)
    pygame.draw.rect(screen, GREEN, booster.rect, 2)
    # Draw Magnet
    pygame.draw.circle(screen, PINK, (magnet.rect.centerx, magnet.rect.centery), magnet.radius)
    # Draw SpawnerBox
    pygame.draw.rect(screen, PURPLE, spawner_box_zone1.rect, 2)
    pygame.draw.rect(screen, PURPLE, spawner_box_zone2.rect, 2)
----------------------------------------------------------------
----------------------------------------------------------------
"""

# TODO: Add Ice Cube Test Spawns (hard spawns, and spawner_box spawns)!!!

spawner_box_zone1 = SpawnerBox(225, 200, 24, 24, PURPLE, PURPLE, spawn_cooldown=2500, initial_spawn_delay=3000)
spawner_box_zone1.set_parameters(velocity_x=225, velocity_y=225, mass=6, angle=50)
spawner_box_zone2 = SpawnerBox(250, 200, 24, 24, PURPLE, PURPLE, spawn_cooldown=2500, initial_spawn_delay=3250)
spawner_box_zone2.set_parameters(velocity_x=225, velocity_y=225, mass=6, angle=50)
spawner_box_zone3 = SpawnerBox(275, 200, 24, 24, PURPLE, PURPLE, spawn_cooldown=2500, initial_spawn_delay=3500)
spawner_box_zone3.set_parameters(velocity_x=225, velocity_y=225, mass=6, angle=50)
spawner_box_zone4 = SpawnerBox(0, 100, 24, 24, PURPLE, PURPLE, spawn_cooldown=2500, initial_spawn_delay=3000)
spawner_box_zone4.set_parameters(velocity_x=125, velocity_y=125, mass=6, angle=360)
spawner_box_zone5 = SpawnerBox(0, 75, 24, 24, PURPLE, PURPLE, spawn_cooldown=2500, initial_spawn_delay=3250)
spawner_box_zone5.set_parameters(velocity_x=125, velocity_y=125, mass=6, angle=360)
spawner_box_zone6 = SpawnerBox(50, 0, 24, 24, PURPLE, PURPLE, spawn_cooldown=2500, initial_spawn_delay=1500)
spawner_box_zone6.set_parameters(velocity_x=56, velocity_y=56, mass=6, angle=90)
spawner_box_zone7 = SpawnerBox(768, 568, 24, 24, PURPLE, PURPLE, spawn_cooldown=2500, initial_spawn_delay=1500)
spawner_box_zone7.set_parameters(velocity_x=175, velocity_y=175, mass=6, angle=190)

friction_zone = FrictionZone(100, 100, 200, 100, 0.965)
friction_zone2 = FrictionZone(692, 8, 100, 100, 0.94)
kill_box = KillBox(8, 468, 124, 124)
booster = Booster(600, 132, 32, 300, 6.25)
magnet = Magnet(300, 400, 50, 0.12, 1.0, 10.0)

# Initial reset
pucks = []
static_pucks = []
ice_cubes = []
# TODO: Add empty lists to store the other classes like magnets, friction_zones, kill_boxes, etc...
static_spawners = [spawner_box_zone1, spawner_box_zone2, spawner_box_zone3]
spawner_boxes = [spawner_box_zone4, spawner_box_zone5, spawner_box_zone6, spawner_box_zone7]
# TODO: Add static_pucks and ice_cubes to this. vvv
reset_simulation(pucks, *spawner_boxes)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    dt = clock.tick(FPS) / 120.0

    # TODO: Add ice_cube collision checks.
    # Handle puck collisions using entity_collision
    for i in range(len(pucks)):
        for j in range(i + 1, len(pucks)):
            if pucks[i].active and pucks[j].active:
                entity_collision(pucks[i], pucks[j])

    # Handle static_puck collisions using entity_collision
    for i in range(len(static_pucks)):
        for j in range(i + 1, len(static_pucks)):
            if static_pucks[i].active and static_pucks[j].active:
                entity_collision(static_pucks[i], static_pucks[j])

    # Handle cross puck collisions using entity_collision
    for i in range(len(pucks)):
        for j in range(i + 1, len(static_pucks)):
            if pucks[i].active and static_pucks[j].active:
                entity_collision(pucks[i], static_pucks[j])

    # TODO: Add ice_cube collision handling using entity collision.

    # TODO: Eventually update these for loops when all classes are stored in lists.
    # Apply friction from FrictionZone
    for puck in pucks:
        friction_zone.apply_friction(puck)
        friction_zone2.apply_friction(puck)

    # Check for collisions with KillBox
    for puck in pucks:
        kill_box.check_collision(puck)

    # Apply boost from Booster
    for puck in pucks:
        booster.apply_boost(puck)

    # Apply magnetism from Magnet
    for puck in pucks:
        magnet.apply_magnetism(puck)

    # Spawn pucks with spawner_boxes[] list
    for spawner_box in spawner_boxes:
        spawner_box.spawn_puck(pucks, dt)

    # Spawn pucks with static_spawner[] list
    for spawner_box in static_spawners:
        spawner_box.spawn_puck(static_pucks, dt)

    # TODO: Test static_puck interactions.
    # Check for collisions with KillBox (static_puck)
    for static_puck in static_pucks:
        kill_box.check_static_collision(static_puck)

    # Check for collisions with Booster (static_puck)
    for static_puck in static_pucks:
        booster.apply_static_boost(static_puck)

    # Check for collisions with FrictionZone (static_puck)
    for static_puck in static_pucks:
        friction_zone.apply_static_friction(static_puck)
        friction_zone2.apply_static_friction(static_puck)

    # TODO: Add ice_cube interactions.
        # TODO: Add additional functionality for ice_cubes to reset to original location 6 frames after one becomes inactive.
    # Check for collisions with KillBox (ice_cubes)
    # for ice_cube in ice_cubes:
        # kill_box.check_collision(ice_cube)

    # Check for collisions with Booster (ice_cubes)
    # for ice_cube in ice_cubes:
        # booster.check_collision(ice_cube)

    # Move and update pucks
    for puck in pucks:
        if puck.active:
            puck.vx *= 0.991
            puck.vy *= 0.991

            puck.x += puck.vx * dt
            puck.y += puck.vy * dt

            if (puck.x - puck.radius < GRID_BORDER) and puck.vx < 0:
                puck.vx = -puck.vx
            elif (puck.x + puck.radius > WIDTH - GRID_BORDER) and puck.vx > 0:
                puck.vx = -puck.vx

            if (puck.y - puck.radius < GRID_BORDER) and puck.vy < 0:
                puck.vy = -puck.vy
            elif (puck.y + puck.radius > HEIGHT - GRID_BORDER) and puck.vy > 0:
                puck.vy = -puck.vy

            # TODO: Eventually fix this to not kill pucks for inactivity, instead should trigger duckState.
            velocity_magnitude = math.sqrt(puck.vx ** 2 + puck.vy ** 2)
            if velocity_magnitude < MIN_VELOCITY_THRESHOLD:
                puck.active = False

    # Move and update static_pucks
    for static_puck in static_pucks:
        if static_puck.active:
            static_puck.vx *= 0.991
            static_puck.vy *= 0.991

            static_puck.x += static_puck.vx * dt
            static_puck.y += static_puck.vy * dt

            if (static_puck.x - static_puck.radius < GRID_BORDER) and static_puck.vx < 0:
                static_puck.vx = -static_puck.vx
            elif (static_puck.x + static_puck.radius > WIDTH - GRID_BORDER) and static_puck.vx > 0:
                static_puck.vx = -static_puck.vx

            if (static_puck.y - static_puck.radius < GRID_BORDER) and static_puck.vy < 0:
                static_puck.vy = -static_puck.vy
            elif (static_puck.y + static_puck.radius > HEIGHT - GRID_BORDER) and static_puck.vy > 0:
                static_puck.vy = -static_puck.vy

            # TODO: Eventually fix this to not kill pucks for inactivity, instead should trigger duckState.
            velocity_magnitude = math.sqrt(puck.vx ** 2 + puck.vy ** 2)
            if velocity_magnitude < MIN_VELOCITY_THRESHOLD:
                puck.active = False

            velocity_magnitude_static = math.sqrt(static_puck.vx ** 2 + static_puck.vy ** 2)
            if velocity_magnitude_static < MIN_VELOCITY_THRESHOLD:
                static_puck.active = True
                static_puck.vx = 0
                static_puck.vy = 0

    # TODO: Move and update ice_cubes using similar function to pucks!!!

    # TODO: Update rand_angle once per every 2 frames.

    screen.fill(WHITE)
    pygame.draw.rect(screen, BLUE, (0, 0, WIDTH, GRID_BORDER))
    pygame.draw.rect(screen, BLUE, (0, 0, GRID_BORDER, HEIGHT))
    pygame.draw.rect(screen, BLUE, (0, HEIGHT - GRID_BORDER, WIDTH, GRID_BORDER))
    pygame.draw.rect(screen, BLUE, (WIDTH - GRID_BORDER, 0, GRID_BORDER, HEIGHT))

    # Draw magnets
    pygame.draw.rect(screen, YELLOW, friction_zone.rect, 2)
    pygame.draw.rect(screen, BROWN, friction_zone2.rect, 2)
    pygame.draw.rect(screen, RED, kill_box.rect, 2)
    pygame.draw.rect(screen, GREEN, booster.rect, 2)
    # Draw magnets
    pygame.draw.circle(screen, PINK, (magnet.rect.centerx, magnet.rect.centery), magnet.radius)
    # Draw spawner_boxes
    pygame.draw.rect(screen, PURPLE, spawner_box_zone1.rect, 2)
    pygame.draw.rect(screen, PURPLE, spawner_box_zone2.rect, 2)
    pygame.draw.rect(screen, PURPLE, spawner_box_zone3.rect, 2)
    pygame.draw.rect(screen, PURPLE, spawner_box_zone4.rect, 2)
    pygame.draw.rect(screen, PURPLE, spawner_box_zone5.rect, 2)
    pygame.draw.rect(screen, PURPLE, spawner_box_zone6.rect, 2)
    pygame.draw.rect(screen, PURPLE, spawner_box_zone7.rect, 2)

    for puck in pucks:
        if puck.active:
            pygame.draw.circle(screen, BLACK, (int(puck.x), int(puck.y)), puck.radius)

    for static_puck in static_pucks:
        if static_puck.active:
            pygame.draw.circle(screen, BLUE, (int(static_puck.x), int(static_puck.y)), static_puck.radius)

    # TODO: Add functionality to draw ice_cubes in a similar way to how pucks are drawn.
    # for ice_cube in ice_cubes:
        # if ice_cube.active:
            # pygame.draw.rect(screen, BABY, (int(puck.x), int(puck.y)), puck.radius)

    pucks = [puck for puck in pucks if puck.active]

    if not pucks:
        lives -= 1
        if lives > 0:
            reset_simulation(pucks)
        else:
            running = False

    pygame.display.flip()

pygame.quit()
sys.exit()