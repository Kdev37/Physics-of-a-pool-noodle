# Imports
import matplotlib.pyplot as plt
import math

# Constants 
dt = 0.01  # Time step for simulation (seconds)
g = 9.8  # Acceleration due to gravity (m/s^2)

# User-specified velocities
vx = 8.0  # Initial horizontal velocity (m/s)
vy = 1.71  # Initial vertical velocity (m/s)

# Pool noodle properties
mass = 0.15  # Mass of the pool noodle (kg)
radius = 0.035  # Radius of the pool noodle (m)
area = math.pi * radius**2  # Cross-sectional area of the pool noodle (m^2)
rho = 1.225  # Air density (kg/m^3)
Cd = 1.3  # Drag coefficient (dimensionless)

# Initial position
x, y = 0.0, 0.0  # Starting at the origin (0, 0)
positions = []  # List to store positions (x, y) over time
velocities = []  # List to store velocities (vx, vy) over time
timestamps = []  # List to store timestamps

# Simulation loop
t = 0.0  # Initialize time
while y >= 0:
    # Record current position, velocity, and time
    positions.append((x, y))
    velocities.append((vx, vy))
    timestamps.append(t)

    print(f"Time: {t:.2f} s, Position: ({x:.2f}, {y:.2f}) m, Velocity: ({vx:.2f}, {vy:.2f}) m/s")

    # Calculate the magnitude of velocity
    v = math.sqrt(vx**2 + vy**2)

    # Calculate drag force
    Fd = 0.5 * rho * Cd * area * v**2  # Drag force magnitude
    ax_drag = -(Fd / mass) * (vx / v) if v != 0 else 0  # Drag acceleration in x-direction
    ay_drag = -(Fd / mass) * (vy / v) if v != 0 else 0  # Drag acceleration in y-direction

    # Net accelerations
    ax = ax_drag  # Horizontal acceleration (only drag acts in x-direction)
    ay = ay_drag - g  # Vertical acceleration (drag and gravity)

    # Update velocities using acceleration
    vx += ax * dt
    vy += ay * dt

    # Update positions using velocity
    x += vx * dt
    y += vy * dt

    # Increment time
    t += dt

# Plot the trajectory
plt.rcParams['toolbar'] = 'none'  # Disable toolbar in the plot window
x_vals = [p[0] for p in positions]  # Extract x-coordinates
y_vals = [p[1] for p in positions]  # Extract y-coordinates
plt.plot(x_vals, y_vals)  # Plot trajectory
plt.title("Pool Noodle Toss (vx=4.7, vy=1.71)")  # Title of the plot
plt.xlabel("Horizontal Distance (m)")  # Label for x-axis
plt.ylabel("Height (m)")  # Label for y-axis
plt.grid(True)  # Enable grid for better visualization
plt.show()  # Display the plot
