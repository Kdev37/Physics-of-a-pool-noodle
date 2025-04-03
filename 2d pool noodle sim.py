import pygame
import pymunk
import pymunk.pygame_util
import math
import time

pygame.init()
screen = pygame.display.set_mode((900, 700))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

space = pymunk.Space()
space.gravity = (0, 900)
draw_options = pymunk.pygame_util.DrawOptions(screen)

# Sliders
velocity = 20  # m/s
angle = 45
dragging_velocity = False
dragging_angle = False

def draw_slider(x, y, value, label, min_val, max_val):
    pygame.draw.rect(screen, (200, 200, 200), (x, y, 200, 10))
    slider_pos = x + int((value - min_val) / (max_val - min_val) * 200)
    pygame.draw.circle(screen, (50, 50, 255), (slider_pos, y + 5), 8)
    txt = font.render(f"{label}: {round(value, 1)}", True, (0, 0, 0))
    screen.blit(txt, (x, y - 20))
    return slider_pos

def slider_interaction(slider_x, mouse_x, min_val, max_val):
    ratio = (mouse_x - slider_x) / 200
    return min_val + max(0, min(1, ratio)) * (max_val - min_val)

# Ground
ground = pymunk.Segment(space.static_body, (0, 680), (900, 680), 5)
ground.friction = 1.0
space.add(ground)

# Goal
goal_radius = 60
goal_pos = (600, 300)
goal_body = pymunk.Body(body_type=pymunk.Body.STATIC)
goal_body.position = goal_pos
goal_shape = pymunk.Circle(goal_body, goal_radius)
goal_shape.sensor = True
space.add(goal_body, goal_shape)

#noodle
def create_noodle(start_pos, segment_length=25, segment_count=12):
    bodies, shapes, joints = [], [], []
    prev_body = None
    for i in range(segment_count):
        body = pymunk.Body(1, pymunk.moment_for_box(1, (segment_length, 10)))
        body.position = start_pos[0] + i * segment_length, start_pos[1]
        shape = pymunk.Poly.create_box(body, (segment_length, 10))
        shape.friction = 0.5
        space.add(body, shape)
        bodies.append(body)
        shapes.append(shape)
        if prev_body:
            spring = pymunk.DampedSpring(
                prev_body, body,
                (segment_length / 2, 0), (-segment_length / 2, 0),
                rest_length=segment_length,
                stiffness=1500,
                damping=200
            )
            space.add(spring)
            joints.append(spring)
        prev_body = body
    return bodies, shapes, joints

noodle_bodies = []
launch_time = None
air_time = 0
max_height = 680
distance_traveled = 0
last_throw_stats = ""
waiting_to_clear = False

def apply_drag(body, drag_coefficient=0.0025):
    vx, vy = body.velocity
    speed = math.sqrt(vx ** 2 + vy ** 2)
    if speed == 0:
        return
    drag_force = -drag_coefficient * speed * vx, -drag_coefficient * speed * vy
    body.apply_force_at_local_point(drag_force)

# Game loop
running = True
launched = False
passed_through_goal = False
score = 0

while running:
    screen.fill((255, 255, 255))
    mx, my = pygame.mouse.get_pos()

    slider_x = 50
    vel_slider = draw_slider(slider_x, 620, velocity, "Velocity (m/s)", 5, 50)
    ang_slider = draw_slider(slider_x, 670, angle, "Launch Angle (°)", 0, 90)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if 620 <= my <= 640:
                dragging_velocity = True
            elif 670 <= my <= 690:
                dragging_angle = True

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging_velocity = False
            dragging_angle = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if waiting_to_clear:
                    for body in noodle_bodies:
                        space.remove(body)
                    noodle_bodies = []
                    launched = False
                    waiting_to_clear = False
                else:
                    for body in noodle_bodies:
                        space.remove(body)
                    noodle_bodies, _, _ = create_noodle((100, 100))
                    radians = math.radians(angle)
                    launch_vec = (
                        math.cos(radians) * velocity * 50,
                        -math.sin(radians) * velocity * 50
                    )
                    noodle_bodies[0].apply_impulse_at_local_point(launch_vec)
                    launched = True
                    passed_through_goal = False
                    max_height = 680
                    launch_time = time.time()

    # Update sliders if dragging
    if dragging_velocity:
        velocity = slider_interaction(slider_x, mx, 5, 50)
    if dragging_angle:
        angle = slider_interaction(slider_x, mx, 0, 90)

    if launched:
        for body in noodle_bodies:
            apply_drag(body)
            max_height = min(max_height, body.position.y)

        air_time = time.time() - launch_time if launch_time else 0
        if noodle_bodies:
            distance_traveled = noodle_bodies[-1].position.x - 100

        # Goal detection
        if not passed_through_goal:
            for body in noodle_bodies:
                dx = body.position.x - goal_pos[0]
                dy = body.position.y - goal_pos[1]
                distance = math.hypot(dx, dy)
                if distance < goal_radius:
                    passed_through_goal = True
                    score += 1
                    break

        # Detect landing
        landed = all(
            abs(body.velocity.y) < 10 and body.position.y > 670 for body in noodle_bodies
        )
        if landed:
            launched = False
            waiting_to_clear = True
            last_throw_stats = (
                f"Air Time: {air_time:.2f}s | "
                f"Max Height: {round(680 - max_height)} px | "
                f"Distance: {round(distance_traveled)} px"
            )

    # Physics and draw
    space.step(1 / 60.0)
    space.debug_draw(draw_options)

    pygame.draw.circle(screen, (255, 0, 0), (int(goal_pos[0]), int(goal_pos[1])), goal_radius, 3)

    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, (750, 30))

    if last_throw_stats:
        stat_text = font.render(last_throw_stats, True, (0, 0, 0))
        screen.blit(stat_text, (50, 30))

    if waiting_to_clear:
        prompt = font.render("Press SPACE to reset", True, (100, 0, 0))
        screen.blit(prompt, (350, 60))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

#write up
#thiscode simulates a noodle launcher game using Pygame and Pymunk for physics simulation. The player can adjust the launch velocity and angle using sliders, and the noodle is affected by gravity and drag forces. The goal is to pass through a circular target, and the game keeps track of the score and throw statistics.