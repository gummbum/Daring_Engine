import pygame
import sys
import random
import math
"""
Daring Ducks - Game Engine:
"""

pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600       # Adjust this to your screen size (pixels)
GRID_SIZE = 8                  # Adjust this to your grid cell size (pixels)
FPS = 120                      # Frames per second
PUCK_RADIUS = 6                # Drawn radius (pixels)
COLLISION_RADIUS = 5           # Set your desired collision radius here (pixels)
GRID_BORDER = GRID_SIZE        # Calculate the border thickness based on grid size
MIN_VELOCITY_THRESHOLD = 1.33  # Minimum velocity threshold
MIN_VELOCITY_THRESHOLD_2 = 12.0
MIN_VELOCITY_THRESHOLD_3 = 20.0
PUCK_COUNT = 3
MAX_LIVES = 10
# Colors
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
RED = (255, 0, 0)
PINK = (255, 0, 200)
PURPLE = (120, 0, 200)
PURPLE2 = (180, 0, 220)
GREEN = (20, 150, 100)
GREEN2 = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GREY = (150, 150, 255)
BROWN = (210, 100, 0)

# Pygame setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Puck-Wall Collision Simulation")
clock = pygame.time.Clock()

"""
Backbone functions for engine:
vvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
def entity_collision(entity1, entity2):
    offset = (int(entity2.x - entity1.x), int(entity2.y - entity1.y))

    if entity1.mask.overlap(entity2.mask, offset):
        if hasattr(entity1, 'collision_radius') and hasattr(entity2, 'collision_radius'):
            # Circular collision response
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
            
            if normal != 0:  # Check for zero division
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
        else:
            # Rectangular collision response (same as before)
            entity1_rect = entity1.rect
            entity2_rect = entity2.rect
            intersection = entity1_rect.clip(entity2_rect)

            if intersection.width > 0 and intersection.height > 0:
                if intersection.width < intersection.height:
                    # Horizontal collision
                    if entity1_rect.left < entity2_rect.left:
                        entity1_rect.right = entity2_rect.left
                    else:
                        entity1_rect.left = entity2_rect.right
                else:
                    # Vertical collision
                    if entity1_rect.top < entity2_rect.top:
                        entity1_rect.bottom = entity2_rect.top
                    else:
                        entity1_rect.top = entity2_rect.bottom

                entity1.x = entity1_rect.centerx
                entity1.y = entity1_rect.centery

                # Apply collision response for rectangular collision
                # In this extended version, we'll just reverse the velocities for both entities.
                entity1.vx = -entity1.vx
                entity1.vy = -entity1.vy
                entity2.vx = -entity2.vx
                entity2.vy = -entity2.vy

                entity1.rect = entity1_rect  # Update the rect

# For main loop
def handle_cross_collisions(entity_list_1, entity_list_2):
    for entity_1 in entity_list_1:
        if entity_1.active:
            for entity_2 in entity_list_2:
                if entity_2.active:
                    entity_collision(entity_1, entity_2)

# Debugging
def directional_ray(screen, entity, ray_color):
    # Calculate the direction angle from velocity components
    direction_angle = math.atan2(entity.vy, entity.vx)
    # Calculate the length of the ray (double the entity's radius)
    ray_length = 3 * entity.radius
    # Calculate the endpoint of the ray
    end_x = entity.x + ray_length * math.cos(direction_angle)
    end_y = entity.y + ray_length * math.sin(direction_angle)
    # Draw the ray on the screen
    pygame.draw.line(screen, ray_color, (entity.x, entity.y), (end_x, end_y), 2)

# Debugging
def shooter_directional_ray(screen, entity, ray_color):
    # Calculate the direction angle from velocity components
    direction_angle = math.atan2(entity.vy, entity.vx)
    # Calculate the length of the ray (double the entity's radius)
    ray_length = 7 * entity.radius
    # Calculate the endpoint of the ray
    end_x = entity.x + ray_length * math.cos(direction_angle)
    end_y = entity.y + ray_length * math.sin(direction_angle)
    # Draw the ray on the screen
    pygame.draw.line(screen, ray_color, (entity.x, entity.y), (end_x, end_y), 2)

# Callable basic math function
def rand_angle():
    rand_angle = random.randint(0,-360)
    return rand_angle

"""
Main Classes:
vvvvvvvvvvvvv
"""
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

class UniqueEntity:
    def __init__(self, x, y, vx, vy, mass, width, height, drawn_color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.mass = mass
        self.width = width
        self.height = height
        self.drawn_color = drawn_color
        self.active = True

        self.rect = pygame.Rect(x - (width / 2), y - (height / 2), width, height)

        mask_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(mask_surface, (0, 0, 0, 0), (0, 0, width, height))  # Rectangular mask
        self.mask = pygame.mask.from_surface(mask_surface)

    def entity_collision(self, other_entity):
        offset = (int(other_entity.x - self.x), int(other_entity.y - self.y))
        return self.mask.overlap(other_entity.mask, offset)

# TODO: Fix to accept speed and angle and convert it to directional velocity using engine helper functions.
class SpawnerBox:
    def __init__(self, x, y, width, height, drawn_color, collision_color, spawn_cooldown=1000, initial_spawn_delay=0):
        self.x = float(x)  # Store x and y as floats
        self.y = float(y)
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

        if not self.has_spawned_initial_puck and current_time >= self.initial_spawn_delay:
            # Initial puck spawn after the initial delay
            angle_rad = math.radians(self.angle)
            vx = self.velocity_x * math.cos(angle_rad)
            vy = self.velocity_y * math.sin(angle_rad)
            pucks.append(Puck(self.x, self.y, vx, vy, self.mass, PUCK_RADIUS, COLLISION_RADIUS))
            self.last_spawn_time = current_time
            self.has_spawned_initial_puck = True
        elif current_time - self.last_spawn_time >= self.spawn_cooldown:
            # Regular puck spawn after the cooldown period
            angle_rad = math.radians(self.angle)
            vx = self.velocity_x * math.cos(angle_rad)
            vy = self.velocity_y * math.sin(angle_rad)
            pucks.append(Puck(self.x, self.y, vx, vy, self.mass, PUCK_RADIUS, COLLISION_RADIUS))
            self.last_spawn_time = current_time

    def spawn_shooter_puck(self, shooter_pucks, dt):
        current_time = pygame.time.get_ticks()

        if not self.has_spawned_initial_puck and current_time >= self.initial_spawn_delay:
            # Initial shooter puck spawn after the initial delay
            angle_rad = math.radians(self.angle)
            vx = self.velocity_x * math.cos(angle_rad)
            vy = self.velocity_y * math.sin(angle_rad)
            shooter_pucks.append(ShooterPuck(self.x, self.y, vx, vy, self.mass, PUCK_RADIUS, COLLISION_RADIUS))
            self.last_spawn_time = current_time
            self.has_spawned_initial_puck = True
        elif current_time - self.last_spawn_time >= self.spawn_cooldown:
            # Regular shooter puck spawn after the cooldown period
            angle_rad = math.radians(self.angle)
            vx = self.velocity_x * math.cos(angle_rad)
            vy = self.velocity_y * math.sin(angle_rad)
            shooter_pucks.append(ShooterPuck(self.x, self.y, vx, vy, self.mass, PUCK_RADIUS, COLLISION_RADIUS))
            self.last_spawn_time = current_time

    def spawn_static_puck(self, static_pucks, dt):
        current_time = pygame.time.get_ticks()

        if not self.has_spawned_initial_puck and current_time >= self.initial_spawn_delay:
            # Initial static puck spawn after the initial delay
            angle_rad = math.radians(self.angle)
            vx = self.velocity_x * math.cos(angle_rad)
            vy = self.velocity_y * math.sin(angle_rad)
            static_pucks.append(StaticPuck(self.x, self.y, vx, vy, self.mass, PUCK_RADIUS, COLLISION_RADIUS))
            self.last_spawn_time = current_time
            self.has_spawned_initial_puck = True
        elif current_time - self.last_spawn_time >= self.spawn_cooldown:
            # Regular static puck spawn after the cooldown period
            angle_rad = math.radians(self.angle)
            vx = self.velocity_x * math.cos(angle_rad)
            vy = self.velocity_y * math.sin(angle_rad)
            static_pucks.append(StaticPuck(self.x, self.y, vx, vy, self.mass, PUCK_RADIUS, COLLISION_RADIUS))
            self.last_spawn_time = current_time

    # TODO: Add support for spawning ice_cubes, static_pucks, or pucks based on parameter input when it is instantiated.
    # TODO: It should have presets to instantiate either a cube spawner or puck spawner, all the other parameters stay the same.
    # IceCubes will be able to be spawned stationary, with 0 for the x and y velocity.

    def reset_initial_spawn_timer(self):
        self.has_spawned_initial_puck = False

"""
Entity and UniqueEntity Classes:
vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
# TODO: Finish DuckState
# TODO: A state for the pucks to enter instead of inactivity. (the settled state)
# TODO: For sim purposes the pucks should be reset at random dir velocity from current settled position after 3 seconds in after DuckState triggers
class DuckState(Entity):
    def __init__(self, x, y, vx, vy, drawn_radius):
        return

class Puck(Entity):
    def __init__(self, x, y, vx, vy, mass, drawn_radius, collision_radius):
        super().__init__(x, y, vx, vy, mass, drawn_radius, collision_radius)

class StaticPuck(Entity):
    def __init__(self, x, y, vx, vy, mass, drawn_radius, collision_radius):
        super().__init__(x, y, vx, vy, mass, drawn_radius, collision_radius)

# TODO: Add Skull(Entity) class. ***
# TODO: This class should have movement and collision detection, as well as turning pucks inactive 1 second after collision. (puck will flash rapidly)

# TODO: This class should transform into a regular puck after it hots 0 velocity.
class ShooterPuck(Entity):
    def __init__(self, x, y, vx, vy, mass, drawn_radius, collision_radius):
        super().__init__(x, y, vx, vy, mass, drawn_radius, collision_radius)

# TODO: Fix this entity !!!
class IceCube(UniqueEntity):
    def __init__(self, x, y , vx, vy, mass, width, height, drawn_color):
        super().__init__(x, y, vx, vy, mass, width, height, drawn_color)

# TODO: Make multiple shape options for FrictionZone dimensional parameters, ie. circular and triangular as well as the rectangle that already exists.
# TODO: Each of these options should be named and referenced respectively, ie. circle, rectangle, and triangle.
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

"""
Zone Classes:
vvvvvvvvvvvvv
"""
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

# TODO: Update for ice_cubes.
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

        if puck_overlap_area >= 0.70 * puck_area:
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

        if static_puck_overlap_area >= 0.70 * static_puck_area:
            static_puck.active = False

        # TODO: Check for Ice Cube collision

class DirBooster(Zone):
    def __init__(self, x, y, width, height, angle, boost_velocity):
        super().__init__(x, y, width, height, YELLOW, BLUE)
        self.boost_velocity = boost_velocity
        self.pucks_passed = set()
        self.static_pucks_passed = set()
        self.angle = angle
        self.boost_delay_frames = 4  # Delay the boost by 4 frames (120fps)
        self.frame_count = 0

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

        if puck_overlap_area >= 0.85 * puck_area:
            if puck not in self.pucks_passed:
                # Reset the player velocity
                puck.vx = 1.0
                puck.vy = 1.0
                
                angle_rad = math.radians(self.angle)
                
                # Delay the boost by the specified frames
                if self.frame_count >= self.boost_delay_frames:
                    # Apply the boost in the direction of the current velocity
                    puck.vx = self.boost_velocity * math.cos(angle_rad)
                    puck.vy = self.boost_velocity * math.sin(angle_rad)

                    # Mark the puck as boosted
                    self.pucks_passed.add(puck)

                # Increment the frame count
                self.frame_count += 1
            
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

        if static_puck_overlap_area >= 0.85 * static_puck_area:
            angle_rad = math.radians(self.angle)
            
            # Delay the boost by the specified frames
            if self.frame_count >= self.boost_delay_frames:
                # Apply the boost in the direction of the current velocity
                static_puck.vx = self.boost_velocity * math.cos(angle_rad)
                static_puck.vy = self.boost_velocity * math.sin(angle_rad)

            # Increment the frame count
            self.frame_count += 1

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

        if puck_overlap_area >= 0.71 * puck_area:
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

        if static_puck_overlap_area >= 0.71 * static_puck_area:
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

class Magnet(Zone):
    def __init__(self, x, y, radius, pull_speed, velocity_cap):
        super().__init__(x, y, radius * 2, radius * 2, BLUE, YELLOW)
        self.radius = radius
        self.pull_speed = pull_speed
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
            if distance <= magnetized_puck.radius * 0.001:
                magnetized_puck.active = False
                self.magnetized_pucks.remove(magnetized_puck)  # Remove from magnetized pucks set

# TODO: FIX !!!
class RepulsionZone(Zone):
    def __init__(self, x, y, outer_radius, growth_rate, circle_color, initial_radius, initial_mass):
        super().__init__(x, y, outer_radius * 2, outer_radius * 2, circle_color, circle_color)
        return

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
Function for resetting and drawing:
vvvvvvvvvvvvvvvvvvvvvvvv
"""
# TODO: Reset spawn_box timers!!!
def reset(pucks, *spawner_boxes):
    pucks.clear()
    static_pucks.clear()
    # Define the delay frames
    puck_creation_delay_frames = 0  # Adjust as needed
    # Initialize frame counters
    puck_frame_count = 0

    # TODO: Add this, move ice_cubes back to initial locations on reset.
    # for ice_cube in ice_cubes:
        # Reset Ice Cubes to initial position and initial velocity !!!
        # return
    
    # TODO: Add this, move static_pucks back to initial locations on reset.
    # for static_ice_cube in static_ice_cubes:
        # Reset Ice Cubes to initial position and initial velocity !!!
        # return

    for spawner_box in spawner_boxes:
        spawner_box.reset_initial_spawn_timer()  # Reset the initial spawn delay timer

    for spawner_box in static_spawners:
        spawner_box.reset_initial_spawn_timer()  # Reset the initial spawn delay timer

    for spawner_box in shooter_spawners:
        spawner_box.reset_initial_spawn_timer()  # Reset the initial spawn delay timer

    # Create static_pucks with delay
    for i, (x, y, vx, vy, mass) in enumerate(puck_starting_positions):
        if puck_frame_count >= puck_creation_delay_frames:
            pucks.append(Puck(x, y, vx, vy, mass, PUCK_RADIUS, COLLISION_RADIUS))
        puck_frame_count += 1

def render(screen, pucks, shooter_pucks, static_pucks, friction_zone, friction_zone2, repulsion,
              kill_box, booster, dir_booster, magnet, spawner_boxes, static_spawners, shooter_spawners, GRID_BORDER):
    screen.fill(WHITE)
    pygame.draw.rect(screen, BLUE, (0, 0, WIDTH, GRID_BORDER))
    pygame.draw.rect(screen, BLUE, (0, 0, GRID_BORDER, HEIGHT))
    pygame.draw.rect(screen, BLUE, (0, HEIGHT - GRID_BORDER, WIDTH, GRID_BORDER))
    pygame.draw.rect(screen, BLUE, (WIDTH - GRID_BORDER, 0, GRID_BORDER, HEIGHT))

    pygame.draw.rect(screen, YELLOW, friction_zone.rect, 2)
    pygame.draw.rect(screen, BROWN, friction_zone2.rect, 2)
    pygame.draw.rect(screen, RED, kill_box.rect, 2)
    pygame.draw.rect(screen, GREEN2, booster.rect, 2)
    pygame.draw.rect(screen, GREEN2, dir_booster.rect, 2)

    # Draw magnets
    pygame.draw.circle(screen, PINK, (magnet.rect.centerx, magnet.rect.centery), magnet.radius)

    # Draw the initial RepulsionZone circle
    # pygame.draw.circle(screen, PURPLE2, (int(repulsion.x), int(repulsion.y)), int(repulsion.outer_radius), 2)

    # Draw the updating RepulsionZone circle if it's active
    # if repulsion.triggered:
        # pygame.draw.circle(screen, PURPLE2, (int(repulsion.x), int(repulsion.y)), int(repulsion.circle_radius))

    for spawner_box in spawner_boxes:
        pygame.draw.rect(screen, GREEN, spawner_box.rect, 2)

    for spawner_box in static_spawners:
        pygame.draw.rect(screen, PURPLE, spawner_box.rect, 2)

    for spawner_box in shooter_spawners:
        pygame.draw.rect(screen, BLUE, spawner_box.rect, 2)

    for shooter_puck in shooter_pucks:
        if shooter_puck.active:
            # Debug vvv
            shooter_directional_ray(screen, shooter_puck, GREEN2)
            pygame.draw.circle(screen, BLUE, (int(shooter_puck.x), int(shooter_puck.y)), shooter_puck.radius)

    for puck in pucks:
        if puck.active:
            # Debug vvv
            # directional_ray(screen, puck, GREEN2)
            pygame.draw.circle(screen, GREEN, (int(puck.x), int(puck.y)), puck.radius)

    for static_puck in static_pucks:
        if static_puck.active:
            # Debug vvv
            # directional_ray(screen, static_puck, GREEN2)
            pygame.draw.circle(screen, BLACK, (int(static_puck.x), int(static_puck.y)), static_puck.radius)

"""
Testing / Debug:
vvvvvvvvvvvvvvvv
"""
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
static_spawners = [spawner_box_zone1, spawner_box_zone2, spawner_box_zone3]
spawner_boxes = [spawner_box_zone4, spawner_box_zone5, spawner_box_zone6, spawner_box_zone7]
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
#                  x    y    W   H    B  dir
dir_booster = Booster(600, 132, 32, 300, -45, 75.0) # 75.0 is STANDARD boost multiplier

#                  x    y    W   H    B   dir
dir_booster2 = Booster(600, 132, 32, 300, -45, 100.0) # 100.0 is HIGH boost multiplier

#                   x    y    W   H    B  dir
dir_booster3 = Booster(600, 132, 32, 300, -45, 150.0) # 150.0 is MAXIMUM boost multiplier
    # Inside main loop vvv
    # Apply boost from DirBooster
    for puck in pucks:
        dir_booster.apply_boost(puck)
--------------------------------------------------
#                x    y    R  PULL  vCap
magnet = Magnet(300, 400, 20, 0.25, 10.0) # vCap = velocity cap for puck entry (small radius is 20)

#                x    y    R  PULL  vCap
magnet2 = Magnet(300, 400, 30, 0.25, 10.0) # vCap = velocity cap for puck entry (medium radius is 30)

#                x    y    R  PULL  vCap
magnet3 = Magnet(300, 400, 50, 0.25, 10.0) # vCap = velocity cap for puck entry (large radius is 50)
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
    pygame.draw.rect(screen, GREEN, dir_booster.rect, 2)
    # Draw Magnet
    pygame.draw.circle(screen, PINK, (magnet.rect.centerx, magnet.rect.centery), magnet.radius)
    # Draw SpawnerBox
    pygame.draw.rect(screen, PURPLE, spawner_box_zone1.rect, 2)
    pygame.draw.rect(screen, PURPLE, spawner_box_zone2.rect, 2)
----------------------------------------------------------------
----------------------------------------------------------------
"""

"""
Angle to (dx/dy) Table:
vvvvvvvvvvvv
"""
"""
Angle Table: (per base of 10 speed and can be multiplied or divided to fit desired speed but still retain desired angle)
---------------------------
#               (dx, dy)
- 0 degrees = (10, 0)
- -22 degrees = (9, -4)
- -45 degrees = (7, -7)
- -67 degrees = (4, -9)
- -90 degrees = (6, -10)
- -112 degrees = (-4, -9)
- -135 degrees = (-7, -7)
- -157 degrees = (-9, -4)
- -180 degrees = (-10, -1)
- -202 degrees = (-9, 4)
- -225 degrees = (-7, 7)
- -247 degrees = (-4, 9)
- -270 degrees = (-2, 10)
- -292 degrees = (4, 9)
- -315 degrees = (7, 7)
- -337 degrees = (9, 4)
- -360 degrees = (10, 0)
---------------------------
"""

# TODO: Add Ice Cube Test Spawns (hard spawns, and spawner_box spawns)!!!
puck_starting_positions = [
    (400, 401, 60, -100, 8),
]

# Initialize lives
lives = MAX_LIVES

"""
Functions for instantiation:
"""
spawner_box_zone4 = SpawnerBox(0, 100, 24, 24, PURPLE, PURPLE, spawn_cooldown=2500, initial_spawn_delay=3000)
spawner_box_zone4.set_parameters(velocity_x=125, velocity_y=125, mass=6, angle=360)
spawner_box_zone5 = SpawnerBox(0, 75, 24, 24, PURPLE, PURPLE, spawn_cooldown=2500, initial_spawn_delay=3250)
spawner_box_zone5.set_parameters(velocity_x=125, velocity_y=125, mass=6, angle=360)
spawner_box_zone6 = SpawnerBox(50, 0, 24, 24, PURPLE, PURPLE, spawn_cooldown=2500, initial_spawn_delay=1500)
spawner_box_zone6.set_parameters(velocity_x=56, velocity_y=56, mass=6, angle=90)
spawner_box_zone7 = SpawnerBox(768, 568, 24, 24, PURPLE, PURPLE, spawn_cooldown=2500, initial_spawn_delay=2000)
spawner_box_zone7.set_parameters(velocity_x=175, velocity_y=175, mass=6, angle=-160)
"""
Shooter:
vvvvvvvv
    Notes:
    - Shooter puck mass starts at 12x regular static puck mass
"""
# TODO: Add params to for exact pixel layout distances from one another.
spawner_box_zone8 = SpawnerBox(459.66, 516, 11, 11, BLUE, BLUE, spawn_cooldown=2500, initial_spawn_delay=3000)
# 25 is lowest shot average is 50 vx/vy, max is 75 (20 is reserved for mess ups) 85 is reserved for a power perfection trigger
spawner_box_zone8.set_parameters(velocity_x=50, velocity_y=50, mass=72, angle=-90) # Shooter (10 degrees both sides of -90) (player selects from 10 available degrees in 2 degree ranges and -90)
# Players vvv
spawner_box_zone9 = SpawnerBox(452.65, 500, 11, 11, GREEN, GREEN, spawn_cooldown=2500, initial_spawn_delay=2500)
spawner_box_zone9.set_parameters(velocity_x=1, velocity_y=1, mass=11, angle=-90)
spawner_box_zone10 = SpawnerBox(466.7, 500, 11, 11, GREEN, GREEN, spawn_cooldown=2500, initial_spawn_delay=2500)
spawner_box_zone10.set_parameters(velocity_x=1, velocity_y=1, mass=10, angle=-90)

# Zones
friction_zone = FrictionZone(100, 85, 200, 100, 0.965)
friction_zone2 = FrictionZone(692, 8, 100, 100, 0.94)
kill_box = KillBox(8, 468, 124, 124)
booster = Booster(600, 132, 32, 200, 6.25)
dir_booster = DirBooster(350, 8, 64, 32, -270, 100.0)
magnet = Magnet(300, 400, 50, 0.25, 10.0)
repulsion = RepulsionZone(200, 300, 24, 5.0, PURPLE2, 8.0, 8.0)

# Initial reset
pucks = []
static_pucks = []
shooter_pucks = []
ice_cubes = []
# TODO: Add empty lists to store the other classes like magnets, friction_zones, kill_boxes, etc...
# TODO: Figure out how to implement resetting of specified ice cubes at spawn location.
static_ice_cubes = []
static_spawners = [spawner_box_zone6, spawner_box_zone9, spawner_box_zone10]
spawner_boxes = [spawner_box_zone5, spawner_box_zone4, spawner_box_zone7]
shooter_spawners = [spawner_box_zone8]

# ice_cube = IceCube(100, 100, 10, 10, 24, 32, 32, GREY)
# ice_cubes.append(ice_cube)

reset(pucks, *spawner_boxes)

"""
Main Loop:
vvvvvvvvvv
"""
# TODO: Add all functionality for shooter_puck interactions.
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    dt = clock.tick(FPS) / 120.0

    # Handle cross collisions between pucks and static_pucks
    handle_cross_collisions(pucks, static_pucks)

    # Handle cross collisions between pucks and ice_cubes
    handle_cross_collisions(pucks, ice_cubes)

    # Handle cross collisions between pucks and shooter_pucks
    handle_cross_collisions(pucks, shooter_pucks)

    # Handle cross collisions between shooter_pucks
    handle_cross_collisions(shooter_pucks, shooter_pucks)

    # Handle cross collisions between shooter_pucks and ice_cubes
    handle_cross_collisions(shooter_pucks, ice_cubes)

    # Handle cross collisions between static_pucks and shooter_pucks
    handle_cross_collisions(static_pucks, shooter_pucks)

    # Handle cross collisions between static_pucks
    handle_cross_collisions(static_pucks, static_pucks)

    # Handle cross collisions between ice_cubes and static_pucks
    handle_cross_collisions(ice_cubes, static_pucks)

    # Handle cross collisions between ice_cubes
    handle_cross_collisions(ice_cubes, ice_cubes)

    # TODO: Eventually update these for loops when all classes are stored in lists.
    # Check for collisions with KillBox
    for puck in pucks:
        kill_box.check_collision(puck)

    # for puck in pucks:
        # if not repulsion.triggered and entity_collision(puck, repulsion):
            # repulsion.trigger()

    # Apply friction from FrictionZone
    for puck in pucks:
        friction_zone.apply_friction(puck)
        friction_zone2.apply_friction(puck)

    # Apply boost from Booster
    for puck in pucks:
        booster.apply_boost(puck)

    # Apply boost from DirBooster
    for puck in pucks:
        dir_booster.apply_boost(puck)

    # Apply magnetism from Magnet
    for puck in pucks:
        magnet.apply_magnetism(puck)


    # Check for collisions with KillBox (static_puck)
    for static_puck in static_pucks:
        kill_box.check_static_collision(static_puck)

    # for static_puck in static_pucks:
        # if not repulsion.triggered and entity_collision(static_puck, repulsion):
            # repulsion.trigger()


    # Check for collisions with FrictionZone (static_puck)
    for static_puck in static_pucks:
        friction_zone.apply_static_friction(static_puck)
        friction_zone2.apply_static_friction(static_puck)

    # Check for collisions with Booster (static_puck)
    for static_puck in static_pucks:
        booster.apply_static_boost(static_puck)

    # Check for collisions with Booster (static_puck)
    for static_puck in static_pucks:
        dir_booster.apply_static_boost(static_puck)

    # Spawn pucks with spawner_boxes[] list
    for spawner_box in spawner_boxes:
        spawner_box.spawn_puck(pucks, dt)

    # Spawn pucks with static_spawner[] list
    for spawner_box in static_spawners:
        spawner_box.spawn_puck(static_pucks, dt)

    # Spawn pucks with static_spawner[] list
    for spawner_box in shooter_spawners:
        spawner_box.spawn_puck(shooter_pucks, dt)

    # TODO: Add ice_cube interactions.
        # TODO: Add additional functionality for ice_cubes to reset to original location 6 frames after one becomes inactive.

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

    # Move and update shooter_pucks
    for shooter_puck in shooter_pucks:
        if shooter_puck.active:
            shooter_puck.vx *= 0.991
            shooter_puck.vy *= 0.991

            shooter_puck.x += shooter_puck.vx * dt
            shooter_puck.y += shooter_puck.vy * dt

            if (shooter_puck.x - shooter_puck.radius < GRID_BORDER) and shooter_puck.vx < 0:
                shooter_puck.vx = -shooter_puck.vx
            elif (shooter_puck.x + shooter_puck.radius > WIDTH - GRID_BORDER) and shooter_puck.vx > 0:
                shooter_puck.vx = -shooter_puck.vx

            if (shooter_puck.y - shooter_puck.radius < GRID_BORDER) and shooter_puck.vy < 0:
                shooter_puck.vy = -shooter_puck.vy
            elif (shooter_puck.y + shooter_puck.radius > HEIGHT - GRID_BORDER) and shooter_puck.vy > 0:
                shooter_puck.vy = -shooter_puck.vy

            velocity_magnitude_static = math.sqrt(shooter_puck.vx ** 2 + shooter_puck.vy ** 2)
            if velocity_magnitude_static < MIN_VELOCITY_THRESHOLD_3:
                shooter_puck.active = True
                shooter_puck.mass = 24

            velocity_magnitude_static = math.sqrt(shooter_puck.vx ** 2 + shooter_puck.vy ** 2)
            if velocity_magnitude_static < MIN_VELOCITY_THRESHOLD_2:
                regular_puck = Puck(shooter_puck.x, shooter_puck.y, shooter_puck.vx, shooter_puck.vy, 12, PUCK_RADIUS, COLLISION_RADIUS)
                shooter_pucks.remove(shooter_puck)
                pucks.append(regular_puck)

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

            velocity_magnitude_static = math.sqrt(static_puck.vx ** 2 + static_puck.vy ** 2)
            if velocity_magnitude_static < MIN_VELOCITY_THRESHOLD:
                static_puck.active = True
                static_puck.vx = 0
                static_puck.vy = 0

    # Move and update IceCubes
    for ice_cube in ice_cubes:
        if ice_cube.active:
            ice_cube.vx *= 0.991
            ice_cube.vy *= 0.991

            ice_cube.x += ice_cube.vx * dt
            ice_cube.y += ice_cube.vy * dt

            if (ice_cube.x - (ice_cube.width / 2) < GRID_BORDER) and ice_cube.vx < 0:
                ice_cube.vx = -ice_cube.vx
            elif (ice_cube.x + (ice_cube.width / 2) > WIDTH - GRID_BORDER) and ice_cube.vx > 0:
                ice_cube.vx = -ice_cube.vx

            if (ice_cube.y - (ice_cube.height / 2) < GRID_BORDER) and ice_cube.vy < 0:
                ice_cube.vy = -ice_cube.vy
            elif (ice_cube.y + (ice_cube.height / 2) > HEIGHT - GRID_BORDER) and ice_cube.vy > 0:
                ice_cube.vy = -ice_cube.vy

            velocity_magnitude_ice = math.sqrt(ice_cube.vx ** 2 + ice_cube.vy ** 2)
            if velocity_magnitude_ice < MIN_VELOCITY_THRESHOLD:
                ice_cube.active = True
                ice_cube.vx = 0
                ice_cube.vy = 0

    # TODO: Update rand_angle once per every 2 frames.

    # Call the draw_game function to handle drawing
    render(screen, pucks, shooter_pucks, static_pucks, friction_zone, friction_zone2, repulsion,
              kill_box, booster, dir_booster, magnet, spawner_boxes, static_spawners, shooter_spawners, GRID_BORDER)

    pygame.display.flip()

    pucks = [puck for puck in pucks if puck.active]

    if not pucks:
        lives -= 1
        if lives > 0:
            reset(pucks)
        else:
            running = False

    pygame.display.flip()

pygame.quit()
sys.exit()