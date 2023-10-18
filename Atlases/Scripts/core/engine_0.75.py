import pygame
import sys
import random
import math

# TODO: Revise all graphics to use OpenGL***

"""
DARING DUCKS ENGINE
<><><><><><><><><><>
- Written by Jay Lever
<><><><><><><><><><>

Description:
vvvvvvvvvvvv
"""
"""
Daring Ducks - Game Engine:
--------------------------
- Game Engine with full custom physics, basic vector rendering, debug rendering, main loop implementation,
  and pixel perfect collision detection for circles and rectangles.
- Backbone functions for collision detection, physics, and debugging, have the job of providing easy to call,
  easy to understand, and reusable code.
  
- Classes representing different objects in the game, including:
  - Puck
  - Duck
  - Booster
  - Bumper
  - etc...
- Each object has its own class with its own attributes and methods.

- Rendering functions for each class type.
- Advanced input params for each class, easy to manipulate for debugging purposes.
"""

#* Initialization
pygame.init()

"""
Constants:
vvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
WIDTH, HEIGHT = 800, 600         # Adjust this to your screen size (pixels)
GRID_SIZE = 8                    # Adjust this to your grid cell size (pixels)
FPS = 120                        # Frames per second
PUCK_RADIUS = 6                  # Drawn radius (pixels)
COLLISION_RADIUS = 5             # Set your desired collision radius here (pixels)
GRID_BORDER = GRID_SIZE          # Calculate the border thickness based on grid size
MIN_VELOCITY_THRESHOLD = 1.33    #
MIN_VELOCITY_THRESHOLD_2 = 12.0  #
MIN_VELOCITY_THRESHOLD_3 = 20.0  #
PUCK_COUNT = 3                   #
MAX_LIVES = 10                   #
#* Colors (RGB) vvv
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

#* Pygame setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Puck-Wall Collision Simulation")
clock = pygame.time.Clock()

"""
Backbone functions for engine:
vvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
#* Main function for most collisions.
def entity_collision(entity1, entity2):
    """
    Check for collision between two entities and apply response.

    Args:
        entity1 (Entity): The first entity.
        entity2 (Entity): The second entity.

    This function checks if the two entities' collision masks overlap.
    If so, it applies a collision response based on whether the entities 
    are circular or rectangular.

    For circular entities, it calculates the collision normal and applies
    an impulse to adjust velocities and nudge entities apart.

    For rectangular entities, it adjusts the positions and velocities 
    to resolve the collision along the shortest axis.

    It also checks if either entity is a Repulsion and triggers
    that entity's grow() method if so.
    """

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
                entity1.vx = -entity1.vx
                entity1.vy = -entity1.vy
                entity2.vx = -entity2.vx
                entity2.vy = -entity2.vy

                entity1.rect = entity1_rect  # Update the rect

    # Check if entity1 or entity2 is a Repulsion object
    if isinstance(entity1, Bumper):
        entity1.grow(entity2.initial_radius, entity2.initial_mass)
    elif isinstance(entity2, Bumper):
        entity2.grow(entity1.initial_radius, entity1.initial_mass)

#* Handling all of the collision checks in a separate function for implementation in main loop.
def cross_collisions(entity_list_1, entity_list_2):
    """
    Check for collisions between two lists of entities.

    Args:
        entity_list_1 (list): List of entities.
        entity_list_2 (list): List of entities.

    Calls entity_collision() for every active entity pair
    between the two lists.
    """
    for entity_1 in entity_list_1:
        if entity_1.active:
            for entity_2 in entity_list_2:
                if entity_2.active:
                    entity_collision(entity_1, entity_2)

#* Handling bumper specific collision checks.
def bumper_collision(repulsion, pucks, static_pucks):
    # Handle collisions between a Repulsion bumper and Pucks
    # Checks distance between bumper and each Puck
    # Applies impulse to Puck velocity if within collision radius
    # Handles both moving and static Pucks
    for puck in pucks:
        dx = puck.x - repulsion.x
        dy = puck.y - repulsion.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance < repulsion.collision_radius + puck.collision_radius:
            # Calculate unit vector from RepulsionZone to puck
            if distance != 0:
                dx /= distance
                dy /= distance

            # Apply an impulse to simulate the push
            impulse = 45  # You can adjust this value for the desired effect

            # Check if the puck has zero velocity or very small velocity (adjust as needed)
            if abs(puck.vx) < 0.1 and abs(puck.vy) < 0.1:
                # Set a minimum velocity in the direction of the RepulsionZone
                min_velocity = 10  # Adjust this value as needed
                puck.vx = min_velocity * dx
                puck.vy = min_velocity * dy
            else:
                # Add an impulse to the puck's velocity
                puck.vx += impulse * dx
                puck.vy += impulse * dy

    for static_puck in static_pucks:
        dx = static_puck.x - repulsion.x
        dy = static_puck.y - repulsion.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance < repulsion.collision_radius + static_puck.collision_radius:
            # Calculate unit vector from RepulsionZone to static puck
            if distance != 0:
                dx /= distance
                dy /= distance

            # Apply an impulse to simulate the push
            impulse = 45  # You can adjust this value for the desired effect

            # Check if the static puck has zero velocity or very small velocity (adjust as needed)
            if abs(static_puck.vx) < 0.1 and abs(static_puck.vy) < 0.1:
                # Set a minimum velocity in the direction of the RepulsionZone
                min_velocity = 10  # Adjust this value as needed
                static_puck.vx = min_velocity * dx
                static_puck.vy = min_velocity * dy
            else:
                # Add an impulse to the static puck's velocity
                static_puck.vx += impulse * dx
                static_puck.vy += impulse * dy

# TODO: Phase out pygame rendering for on board .py script!

#* Debugging widget for directional tracking.
def directional_ray(screen, entity, ray_color):
    # Draws a directional ray on the screen for a given entity.
    # Used for debugging visualization of entity direction.
    # Calculate the direction angle from velocity components
    direction_angle = math.atan2(entity.vy, entity.vx)
    # Calculate the length of the ray (double the entity's radius)
    ray_length = 3 * entity.radius
    # Calculate the endpoint of the ray
    end_x = entity.x + ray_length * math.cos(direction_angle)
    end_y = entity.y + ray_length * math.sin(direction_angle)
    # Draw the ray on the screen
    pygame.draw.line(screen, ray_color, (entity.x, entity.y), (end_x, end_y), 2)

#* Debugging widget for shooter specific directional tracking. 
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

#* Callable basic math function for random negative angles
def rand_angle():
    rand_angle = random.randint(0,-360)
    return rand_angle

"""
Main Classes:
vvvvvvvvvvvvv
"""
class Entity:
    # Entity class represents a basic object in the game world with position, velocity, mass, collision detection etc.
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

# TODO: Figure out how to implement this class.
class UniqueEntity:
    # UniqueEntity class represents a unique entity in the game world
    # with custom dimensions, position, velocity and collision detection.
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

# TODO: Fix to accept speed and negative angle and convert it to directional velocity using backbone angle functions.
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

# TODO: Fix so that all pucks and static pucks within target radius are calculated within update and adjusted accordingly.
# TODO: Use this list ^^^ to add collision detection and repulsion to all surrounding pucks even if there velocity is 0, 0.
# TODO: Add static velocity in respective direction to stationary pucks based location away from repulsion center.
# TODO: Fix Reset delay to be called!!!
class Bumper:
    def __init__(self, x, y, initial_radius, initial_mass, growth_rate, circle_color, target_radius=None):
        # Initialize RepulsionZone properties
        self.x = x
        self.y = y
        self.radius = initial_radius
        self.mass = initial_mass
        self.growth_rate = growth_rate
        self.circle_color = circle_color
        self.triggered = False
        self.triggered_time = 0
        self.initial_radius = initial_radius
        self.initial_mass = initial_mass
        self.growing = False
        self.target_radius = target_radius
        self.reset_delay = 240
        self.reset_counter = 0
        self.collision_radius = initial_radius  # Set the collision_radius to initial_radius
        self.mask = pygame.mask.from_surface(pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA))
        self.mask.fill()

        # Set initial values
        self.active = True
        self.radius = self.initial_radius
        self.growing = True if (self.target_radius is not None) else False

    def trigger_condition(self, entity):
        # Implement your trigger condition logic here
        # For example, you can check if the distance between the RepulsionZone and the entity is less than a threshold
        dx = entity.x - self.x
        dy = entity.y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        trigger_threshold = 14  # Adjust this threshold as needed
        return distance < trigger_threshold

    def trigger(self):
        # Trigger the RepulsionZone
        self.triggered = True
        self.triggered_time = 0

    def grow(self):
        # Increase the RepulsionZone's radius if target_radius is specified
        if self.target_radius is not None:
            self.radius = min(self.target_radius, self.radius + self.growth_rate)

            # Update the collision radius to match the growing radius
            self.collision_radius = self.radius  # Add this line

    def update(self, dt):
        # Update the RepulsionZone if triggered
        if self.triggered:
            # Increase the triggered time
            self.triggered_time += dt

            # Calculate the new radius based on the growth rate and time elapsed
            new_radius = self.initial_radius + self.growth_rate * self.triggered_time

            # Update the RepulsionZone's radius
            self.radius = new_radius

            # Check if the target_radius has been reached, and trigger a reset
            if self.radius >= self.target_radius:
                self.reset()

    def reset(self):
        # Reset the RepulsionZone
        self.triggered = False
        self.triggered_time = 0
        self.radius = self.initial_radius  # Reset the radius to the initial value
        self.growing = False  # Reset growing to False when resetting
        self.mask = pygame.mask.from_surface(pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA))
        self.mask.fill()

    def collide(self, pucks, static_pucks):
        # Check for collisions with pucks
        for puck in pucks:
            distance = math.sqrt((puck.x - self.x) ** 2 + (puck.y - self.y) ** 2)

            # Check if the puck is within the collision radius
            if distance < self.collision_radius + puck.collision_radius:
                # Trigger the RepulsionZone on collision
                self.trigger()

        # Check for collisions with static pucks
        for static_puck in static_pucks:
            distance = math.sqrt((static_puck.x - self.x) ** 2 + (static_puck.y - self.y) ** 2)

            # Check if the static puck is within the collision radius
            if distance < self.collision_radius + static_puck.collision_radius:
                # Trigger the RepulsionZone on collision
                self.trigger()

"""
Entity and UniqueEntity Classes:
vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
class Puck(Entity):
    def __init__(self, x, y, vx, vy, mass, drawn_radius, collision_radius):
        super().__init__(x, y, vx, vy, mass, drawn_radius, collision_radius)

class StaticPuck(Entity):
    def __init__(self, x, y, vx, vy, mass, drawn_radius, collision_radius):
        super().__init__(x, y, vx, vy, mass, drawn_radius, collision_radius)

class ShooterPuck(Entity):
    def __init__(self, x, y, vx, vy, mass, drawn_radius, collision_radius):
        super().__init__(x, y, vx, vy, mass, drawn_radius, collision_radius)

# TODO: Add Skull(Entity) class. ***
# TODO: This class should have movement and collision detection, as well as turning pucks inactive 1 second after collision. (puck will flash rapidly)

# TODO: Add BurningSkull(Entity) class. ***
# TODO: This class should have movement and collision detection, as well as turning pucks inactive on collision and leaving a path of friction2 ice in its wake.

# TODO: Fix this entity !!!
class IceCube(UniqueEntity):
    def __init__(self, x, y , vx, vy, mass, width, height, drawn_color):
        super().__init__(x, y, vx, vy, mass, width, height, drawn_color)

# TODO: Make multiple shape options for Zone dimensional parameters, ie. circular and triangular as well as the rectangle that already exists.
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
# For triggering instantiation or activation of an entity that previously was inactive or non-existent.
class Activation(Zone):
    def __init__(self, x, y, width, height, event, delay):
        super().__init__(x, y, width, height, BLACK, WHITE)
        self.event = event
        self.delay = delay

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

        if puck_overlap_area >= 0.25 * puck_area:
            # Trigger the event after the delay has passed in milliseconds
            if self.delay <= 0:
                self.event()
            else:
                self.delay -= 1

# For triggering a specific function or set of functions, in a standard order, on an entity that already is active or exists.
class Trigger(Zone):
    def __init__(self, x, y, width, height, event, delay):
        super().__init__(x, y, width, height, BLACK, WHITE)
        self.event = event
        self.delay = delay

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

        if puck_overlap_area >= 0.25 * puck_area:
            # Trigger the event after the delay has passed in milliseconds
            if self.delay <= 0:
                self.event()
            else:
                self.delay -= 1

# For triggering a SpawnerBox with custom params.
class SpawnTrigger(Zone):
    def __init__(self, x, y, width, height, event, delay):
        super().__init__(x, y, width, height, BLACK, WHITE)
        self.event = event
        self.delay = delay

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

        if puck_overlap_area >= 0.25 * puck_area:
            # Trigger the event after the delay has passed in milliseconds
            if self.delay <= 0:
                self.event()
            else:
                self.delay -= 1

# TODO: Update for ice_cubes, and shooter_pucks.
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
Functions for input handling:
vvvvvvvvvvvvvvvvvvvvvvvv
"""

# TODO: def button_input():

# TODO: def joystick_input():

"""
Functions for resetting and rendering:
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

# TODO: Update for Repulsion Zones when fixed.
# TODO: Update for new draw functions instead of pygame.
def render(screen, pucks, shooter_pucks, static_pucks, friction_zones, bumpers, kill_boxes, heavy_friction_zones,
           boosters, dir_boosters, magnets, spawner_boxes, static_spawners, shooter_spawners, GRID_BORDER):
    screen.fill(WHITE)
    pygame.draw.rect(screen, BLUE, (0, 0, WIDTH, GRID_BORDER))
    pygame.draw.rect(screen, BLUE, (0, 0, GRID_BORDER, HEIGHT))
    pygame.draw.rect(screen, BLUE, (0, HEIGHT - GRID_BORDER, WIDTH, GRID_BORDER))
    pygame.draw.rect(screen, BLUE, (WIDTH - GRID_BORDER, 0, GRID_BORDER, HEIGHT))

    for friction_zone in friction_zones:
        pygame.draw.rect(screen, YELLOW, friction_zone.rect, 2)
    for friction_zone in heavy_friction_zones:
        pygame.draw.rect(screen, BROWN, friction_zone.rect, 2)

    for kill_box in kill_boxes:
        pygame.draw.rect(screen, RED, kill_box.rect, 2)

    # Render the repulsion zones
    for bumper in bumpers:
        if bumper.active:
            pygame.draw.circle(screen, PURPLE2, (int(bumper.x), int(bumper.y)), int(bumper.radius), 2)
        else:
            pygame.draw.circle(screen, PURPLE2, (int(bumper.x), int(bumper.y)), int(bumper.radius), 2)

    for booster in boosters:
        pygame.draw.rect(screen, GREEN2, booster.rect, 2)

    for dir_booster in dir_boosters:
        pygame.draw.rect(screen, GREEN2, dir_booster.rect, 2)

    for magnet in magnets:
        pygame.draw.circle(screen, PINK, (magnet.rect.centerx, magnet.rect.centery), magnet.radius)

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

"""
Initial Spawns:
vvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
# TODO: Add Ice Cube Test Spawns (hard spawns, and spawner_box spawns)!!!
puck_starting_positions = [
    (135, 540, 70, -70, 8),
]
# ice_cube = IceCube(100, 100, 10, 10, 24, 32, 32, GREY)
# ice_cubes.append(ice_cube)

# Initialize lives
lives = MAX_LIVES

"""
Methods for Instantiation:
vvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
spawner_box_zone4 = SpawnerBox(0, 100, 24, 24, PURPLE, PURPLE, spawn_cooldown=2500, initial_spawn_delay=3000)
spawner_box_zone4.set_parameters(velocity_x=125, velocity_y=125, mass=6, angle=360)
spawner_box_zone5 = SpawnerBox(0, 75, 24, 24, PURPLE, PURPLE, spawn_cooldown=2500, initial_spawn_delay=3250)
spawner_box_zone5.set_parameters(velocity_x=125, velocity_y=125, mass=6, angle=360)
spawner_box_zone6 = SpawnerBox(768, 568, 24, 24, PURPLE, PURPLE, spawn_cooldown=2500, initial_spawn_delay=2000)
spawner_box_zone6.set_parameters(velocity_x=125, velocity_y=125, mass=6, angle=-160)

# Zones
kill_box = KillBox(8, 8, 50, 584)
kill_box2 = KillBox(742, 8, 50, 584)
kill_box3 = KillBox(8, 8, 784, 50)
kill_box4 = KillBox(8, 542, 784, 50)
bumper = Bumper(390, 300, 12, 10.0, 15.0, PURPLE2, target_radius=40)
#* friction_zone = FrictionZone(100, 85, 200, 100, 0.965)
#* friction_zone2 = FrictionZone(692, 8, 100, 100, 0.94)
#* booster = Booster(600, 132, 32, 200, 6.25)
#* dir_booster = DirBooster(350, 8, 64, 32, -270, 100.0)
#* magnet = Magnet(300, 400, 50, 0.25, 10.0)
# x, y, initial_radius, initial_mass, growth_rate, circle_color, target_radius=None
#* bumper2 = Bumper(730, 335, 12, 10.0, 15.0, PURPLE2, target_radius=40)

"""
Shooter Formation:
vvvvvvvv
"""
"""
spawner_box_zone = SpawnerBox(459, 518, 11, 11, BLUE, BLUE, spawn_cooldown=2500, initial_spawn_delay=3000)
# 25 is lowest shot average is 50 vx/vy, max is 75 (20 is reserved for mess ups) 85 is reserved for a power perfection trigger
spawner_box_zone.set_parameters(velocity_x=50, velocity_y=50, mass=72, angle=-90) # Shooter (10 degrees both sides of -90) (player selects from 10 available degrees in 2 degree ranges and -90)
# Players vvv
spawner_box_zone2 = SpawnerBox(452.65, 500, 11, 11, GREEN, GREEN, spawn_cooldown=2500, initial_spawn_delay=2500)
spawner_box_zone2.set_parameters(velocity_x=1, velocity_y=1, mass=12, angle=-90)
spawner_box_zone3 = SpawnerBox(466.7, 500, 11, 11, GREEN, GREEN, spawn_cooldown=2500, initial_spawn_delay=2500)
spawner_box_zone3.set_parameters(velocity_x=1, velocity_y=1, mass=11, angle=-90)
"""

"""
Initial Reset:
vvvvvvvv
"""
#* Entities
pucks = []
static_pucks = []
shooter_pucks = []
resting_pucks = []
ice_cubes = []
skulls = []
flaming_skulls = []
#* Spawners
spawner_boxes = []
static_spawners = [spawner_box_zone5, spawner_box_zone4, spawner_box_zone6]
shooter_spawners = []
ice_cubes_spawners = []
#* Objects
kill_boxes = [kill_box, kill_box2, kill_box3, kill_box4]
bumpers = [bumper]
magnets = []
boosters = []
dir_boosters = []
friction_zones = []
heavy_friction_zones = []

#* Reset
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

    #* Frame Rate Settings
    dt = clock.tick(FPS) / 120.0

    """
    Entity Cross Collision Logic:
    vvvvvvvvvvvvvvvvvvvvvvvv
    """
    # Handle cross collisions between pucks and static_pucks
    cross_collisions(pucks, pucks)
    # Handle cross collisions between pucks and static_pucks
    cross_collisions(pucks, static_pucks)
    # Handle cross collisions between pucks and ice_cubes
    cross_collisions(pucks, ice_cubes)
    # Handle cross collisions between pucks and shooter_pucks
    cross_collisions(pucks, shooter_pucks)
    # Handle cross collisions between shooter_pucks
    cross_collisions(shooter_pucks, shooter_pucks)
    # Handle cross collisions between shooter_pucks and ice_cubes
    cross_collisions(shooter_pucks, ice_cubes)
    # Handle cross collisions between static_pucks and shooter_pucks
    cross_collisions(static_pucks, shooter_pucks)
    # Handle cross collisions between static_pucks
    cross_collisions(static_pucks, static_pucks)
    # Handle cross collisions between ice_cubes and static_pucks
    cross_collisions(ice_cubes, static_pucks)
    # Handle cross collisions between ice_cubes
    cross_collisions(ice_cubes, ice_cubes)

    # TODO: Eventually update these for loops when all classes are stored in lists.
    # Check for collisions with KillBox
    for puck in pucks:
        kill_box.check_collision(puck)
        kill_box2.check_collision(puck)
        kill_box3.check_collision(puck)
        kill_box4.check_collision(puck)

    # Check for collisions with KillBox (static_puck)
    for static_puck in static_pucks:
        kill_box.check_static_collision(static_puck)
        kill_box2.check_static_collision(static_puck)
        kill_box3.check_static_collision(static_puck)
        kill_box4.check_static_collision(static_puck)

    for bumper in bumpers:
        bumper.update(dt)

    for bumper in bumpers:
        bumper_collision(bumper, pucks, static_pucks)

    # Check for triggering condition with regular pucks
    for bumper in bumpers:
        if not bumper.triggered:
            for puck in pucks:
                if bumper.trigger_condition(puck):
                    bumper.trigger()

        # Check for triggering condition with static pucks
        elif not bumper.triggered:
            for static_puck in static_pucks:
                if bumper.trigger_condition(static_puck):
                    bumper.trigger()

    # Spawn pucks with spawner_boxes[] list
    for spawner_box in spawner_boxes:
        spawner_box.spawn_puck(pucks, dt)

    # Spawn pucks with static_spawner[] list
    for spawner_box in static_spawners:
        spawner_box.spawn_puck(static_pucks, dt)

    # Spawn pucks with static_spawner[] list
    for spawner_box in shooter_spawners:
        spawner_box.spawn_puck(shooter_pucks, dt)

    # Apply boost from Booster
    # for puck in pucks:
        # booster.apply_boost(puck)

    # Apply boost from DirBooster
    # for puck in pucks:
        # dir_booster.apply_boost(puck)

    # Apply magnetism from Magnet
    # for puck in pucks:
        # magnet.apply_magnetism(puck)

    # Apply friction from FrictionZone
    # for puck in pucks:
        # friction_zone.apply_friction(puck)
        # friction_zone2.apply_friction(puck)

    # Check for collisions with FrictionZone (static_puck)
    # for static_puck in static_pucks:
        # friction_zone.apply_static_friction(static_puck)
        # friction_zone2.apply_static_friction(static_puck)

    # Check for collisions with Booster (static_puck)
    # for static_puck in static_pucks:
        # booster.apply_static_boost(static_puck)

    # Check for collisions with Booster (static_puck)
    # for static_puck in static_pucks:
        # dir_booster.apply_static_boost(static_puck)

    # TODO: Add ice_cube interactions.
        # TODO: Add additional functionality for ice_cubes to reset to original location 6 frames after one becomes inactive.

    """
    Bumper Collision Logic:
    vvvvvvvvvvvvvvvvvvvvvvvv
    """
    # Check for collisions with regular pucks
    for puck in pucks:
        if bumper.collide([puck], static_pucks):  # Check collision with regular pucks and static pucks
            # Handle collision response here (e.g., apply forces, change velocities, etc.) for regular pucks
            # Example collision response for regular pucks (you can modify this as needed):
            dx = puck.x - bumper.x
            dy = puck.y - bumper.y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            penetration = bumper.collision_radius + puck.collision_radius - distance
            if penetration > 0:
                # Calculate normal and apply force to separate pucks
                normal_x = dx / distance
                normal_y = dy / distance
                force = penetration * 0.5  # Adjust this value as needed
                puck.x += normal_x * force
                puck.y += normal_y * force

    # Check for collisions with static pucks
    for static_puck in static_pucks:
        if bumper.collide([static_puck], pucks + static_pucks):  # Check collision with all pucks and static pucks
            # Handle collision response here (e.g., apply forces, change velocities, etc.) for static pucks
            # Example collision response for static pucks (you can modify this as needed):
            dx = static_puck.x - bumper.x
            dy = static_puck.y - bumper.y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            penetration = bumper.collision_radius + static_puck.collision_radius - distance
            if penetration > 0:
            # Calculate normal and apply force to separate pucks
                normal_x = dx / distance
                normal_y = dy / distance
                force = penetration * 0.5  # Adjust this value as needed
                static_puck.x += normal_x * force
                static_puck.y += normal_y * force

    """
    Movement and Update Logic:
    vvvvvvvvvvvvvvvvvvvvvvvv
    """
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
            ice_cube.vx *= 0.998
            ice_cube.vy *= 0.998

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
    render(screen, pucks, shooter_pucks, static_pucks, friction_zones, bumpers, kill_boxes, heavy_friction_zones,
           boosters, dir_boosters, magnets, spawner_boxes, static_spawners, shooter_spawners, GRID_BORDER)

    pygame.display.flip()

    pucks = [puck for puck in pucks if puck.active]
    # TODO: Add mxpucks variable to calc when there is 50 static_pucks active at one time how many static pucks

    if not pucks:
        lives -= 1
        if lives > 0:
            reset(pucks)
        else:
            running = False

    pygame.display.flip()

pygame.quit()
sys.exit()