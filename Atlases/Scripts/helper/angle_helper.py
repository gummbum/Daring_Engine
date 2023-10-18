import math

"""
Angle Table:
vvvvvvvvvvvv
"""
"""
Angle Table: (per base of 10 speed and can be multiplied or divided to fit desired speed)
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

# Define Spawn parameters
spawn_angle_degrees = -45.0  # Angle in degrees
spawn_speed = 10.0  # Speed magnitude

# Define velocity components
vx = 7.0  # Velocity component in the x-direction
vy = -7.0  # Velocity component in the y-direction

# Convert the Spawn angle from degrees to radians
spawn_angle = math.radians(spawn_angle_degrees)

# Function to convert angle and speed to velocity components
def angle_speed_to_velocity(angle, speed):
    """
    Convert angle (in radians) and speed into directional velocity components (vx, vy).
    
    Args:
        angle (float): Angle in radians.
        speed (float): Speed magnitude.
        
    Returns:
        tuple: A tuple containing (vx, vy) representing directional velocity components.
    """
    vx = speed * math.cos(angle)
    vy = speed * math.sin(angle)
    
    return vx, vy

# Calculate velocity components using Spawn parameters
vx, vy = angle_speed_to_velocity(spawn_angle, spawn_speed)
# Calculate the angle (in radians) from velocity components
angle = math.atan2(vy, vx)
# Calculate the speed magnitude
speed = math.sqrt(vx**2 + vy**2)
# Convert the angle from radians to degrees
angle_degrees = math.degrees(angle)

# Print the results
print("SpawnerBox Angle in degrees:", math.degrees(spawn_angle))
print("SpawnerBox Velocity component in the x-direction:", vx)
print("SpawnerBox Velocity component in the y-direction:", vy)
print("Reversed Angle in degrees:", angle_degrees)
print("Reversed Speed:", speed)