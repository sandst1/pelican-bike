#!/usr/bin/env python3
"""
Pelican Bike Game
A pelican rides a bicycle through a scenic 2D world.
Collect fish, avoid obstacles, and have fun!
"""

import math
import pygame
import random
import sys

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.5
JUMP_SPEED = -12
GROUND_Y = 480
SCROLL_SPEED = 5

# Colors
SKY_BLUE = (135, 206, 235)
GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pelican Bike")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)


class Pelican:
    """The pelican character riding a bicycle."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vy = 0
        self.width = 100  # Larger body, more bird-like
        self.height = 90  # Taller to accommodate head and neck
        self.on_ground = True
        self.wing_angle = 0  # For flapping animation
        self.pedal_phase = 0  # Pedaling cycle for leg animation
        # Sequential wheel jump state
        self.wheel_front_offset = 0.0  # 0 = on ground, negative = up
        self.wheel_back_offset = 0.0
        self.front_vy = 0.0
        self.back_vy = 0.0
        self.jump_frame = 0
        self.body_vert_offset = 0.0  # body moves up/down with avg of wheels
        self.body_tilt = 0.0  # radians

    def jump(self):
        if self.on_ground:
            self.front_vy = JUMP_SPEED
            self.back_vy = 0
            self.wheel_front_offset = 0
            self.wheel_back_offset = 0
            self.jump_frame = 0
            self.body_vert_offset = 0
            self.body_tilt = 0
            self.on_ground = False

    def update(self):
        if not self.on_ground:
            self.jump_frame += 1

            # Front wheel physics
            self.front_vy += GRAVITY
            self.wheel_front_offset += self.front_vy
            if self.wheel_front_offset >= 0:
                self.wheel_front_offset = 0
                self.front_vy = 0

            # Back wheel: starts after 8 frames delay
            if self.jump_frame == 8:
                self.back_vy = JUMP_SPEED

            if self.jump_frame >= 8:
                self.back_vy += GRAVITY
                self.wheel_back_offset += self.back_vy
                if self.wheel_back_offset >= 0:
                    self.wheel_back_offset = 0
                    self.back_vy = 0

            # Body vertical offset: weighted average of wheel heights
            self.body_vert_offset = (self.wheel_front_offset + self.wheel_back_offset) * 0.4

            # Body tilt based on difference between front and back wheel heights
            diff = self.wheel_front_offset - self.wheel_back_offset
            # Scale: ~40px diff => ~0.15 rad (~8.6 deg), clamped to max
            self.body_tilt = -diff * 0.15 / 40
            self.body_tilt = max(-0.15, min(0.15, self.body_tilt))

            # Ground detection: both wheels must be >= 0
            if self.wheel_front_offset >= 0 and self.wheel_back_offset >= 0:
                self.on_ground = True
                self.body_vert_offset = 0
                self.body_tilt = 0

        # Pedal animation (only while on ground)
        if self.on_ground:
            self.pedal_phase += 0.12
        # Wing flapping
        if not self.on_ground:
            self.wing_angle += 0.2
        else:
            self.wing_angle = 0

    def draw(self, surface):
        cx = self.x + self.width // 2
        # Ground body center (not affected by wheel offsets)
        base_cy = (GROUND_Y - self.height) + self.height // 2
        # Actual body center with vertical offset
        cy = base_cy + self.body_vert_offset

        # Helper: apply tilt and vertical offset to y coordinate
        # Small-angle y-shear: y_adj = y + tilt * (x - cx) + vert_offset
        def ty(x_off, y_off):
            """Tilt-and-offset a point relative to cx, base_cy.
            Returns (x, y) with tilt and vertical offset applied."""
            x = cx + x_off
            y = base_cy + y_off + self.body_tilt * x_off + self.body_vert_offset
            return (x, y)

        # --- Bicycle wheels (two wheels, with individual vertical offsets) ---
        wheel_radius = 15
        rear_wheel_cx = cx - 32
        rear_wheel_cy = base_cy + 32 + self.wheel_back_offset
        front_wheel_cx = cx + 30
        front_wheel_cy = base_cy + 32 + self.wheel_front_offset

        # Rear wheel (left)
        pygame.draw.circle(surface, DARK_GRAY, (rear_wheel_cx, rear_wheel_cy), wheel_radius)
        pygame.draw.circle(surface, GRAY, (rear_wheel_cx, rear_wheel_cy), wheel_radius - 3, 2)
        # Front wheel (right)
        pygame.draw.circle(surface, DARK_GRAY, (front_wheel_cx, front_wheel_cy), wheel_radius)
        pygame.draw.circle(surface, GRAY, (front_wheel_cx, front_wheel_cy), wheel_radius - 3, 2)

        # --- Bicycle frame (connecting body to offset wheel positions) ---
        # Frame connection points move with the wheels
        rear_wc_y = base_cy + 18 + self.wheel_back_offset  # wheel connection y for rear
        front_wc_y = base_cy + 18 + self.wheel_front_offset  # wheel connection y for front

        # Seat post (tilted with body)
        p1 = ty(-10, -10)
        p2 = ty(-10, 18)
        pygame.draw.line(surface, GRAY, p1, p2, 5)
        # Top tube (to front wheel) — untouched end follows wheel
        p3 = ty(6, -10)
        pygame.draw.line(surface, GRAY, p3, (front_wheel_cx, front_wc_y), 5)
        # Bottom tube (to rear wheel)
        p4 = ty(-10, 18)
        pygame.draw.line(surface, GRAY, p4, (rear_wheel_cx, rear_wc_y), 5)
        # Front fork
        p5 = ty(30, -5)
        pygame.draw.line(surface, GRAY, p5, (front_wheel_cx, front_wc_y), 5)

        # --- Tail feathers (fan at back of body) ---
        base_x, base_y = ty(-28, -8)
        for i in range(5):
            spread = 0.2 + i * 0.25
            tip_x = base_x - 14 - i * 2
            tip_y = base_y - 4 + spread * 18
            pygame.draw.polygon(surface, DARK_GRAY, [
                (base_x, base_y),
                (tip_x - 2, tip_y - 3),
                (tip_x + 2, tip_y + 3),
            ])

        # --- Wings (pronounced dark shapes on the side of body) ---
        wing_angle_offset = self.wing_angle * 5 if not self.on_ground else 0
        w1, w2, w3, w4 = ty(-12, -32), ty(-38, -52 - wing_angle_offset), ty(-8, -42), ty(4, -30)
        pygame.draw.polygon(surface, BLACK, [w1, w2, w3, w4])
        # Lower/secondary wing
        w5, w6, w7, w8 = ty(6, -24), ty(-22, -18), ty(-32, -35 - wing_angle_offset * 0.5), ty(-4, -28)
        pygame.draw.polygon(surface, DARK_GRAY, [w5, w6, w7, w8])

        # --- Body (large oval) ---
        body_tl = ty(-28, -26)
        body_rect = pygame.Rect(body_tl[0], body_tl[1], 56, 38)
        pygame.draw.ellipse(surface, WHITE, body_rect)
        pygame.draw.ellipse(surface, GRAY, body_rect, 2)

        # --- S-curve neck (connecting head to body) ---
        neck_pts = [ty(12, -8), ty(16, -20), ty(26, -32), ty(32, -38)]
        pygame.draw.lines(surface, WHITE, False, neck_pts, 7)

        # --- Head ---
        hx, hy = ty(34, -40)
        head_radius = 13
        pygame.draw.circle(surface, WHITE, (hx, hy), head_radius)
        pygame.draw.circle(surface, GRAY, (hx, hy), head_radius, 2)

        # --- Realistic orange beak (upper and lower mandible) ---
        head_right = hx + head_radius
        head_top = hy

        # Upper mandible
        upper_beak = [
            (head_right - 1, head_top - 4),
            (head_right + 18, head_top - 14),
            (head_right + 3, head_top + 2),
        ]
        pygame.draw.polygon(surface, ORANGE, upper_beak)

        # Lower mandible
        lower_beak = [
            (head_right - 1, head_top + 4),
            (head_right + 14, head_top + 10),
            (head_right + 3, head_top - 1),
        ]
        pygame.draw.polygon(surface, ORANGE, lower_beak)

        # Mouth line
        pygame.draw.line(
            surface, DARK_GRAY,
            (head_right, head_top),
            (head_right + 16, head_top),
            2,
        )

        # --- Eye (on head) ---
        eye_x = hx + 6
        eye_y = hy - 5
        pygame.draw.circle(surface, BLACK, (eye_x, eye_y), 5)
        pygame.draw.circle(surface, WHITE, (eye_x + 2, eye_y - 2), 2)

        # --- Pedaling animation (legs with rotating pedals) ---
        # Crank center follows body tilt
        crank_cx, crank_cy = ty(-10, 18)
        pedal_radius = 16

        # Both feet rotate clockwise: left moves (sinθ, -cosθ), right moves (-sinθ, cosθ)
        left_px = crank_cx + math.sin(self.pedal_phase) * pedal_radius
        left_py = crank_cy - math.cos(self.pedal_phase) * pedal_radius

        right_px = crank_cx - math.sin(self.pedal_phase) * pedal_radius
        right_py = crank_cy + math.cos(self.pedal_phase) * pedal_radius

        # Legs from body to pedals
        leg_l, leg_r = ty(-12, 12), ty(12, 12)
        pygame.draw.line(surface, WHITE, leg_l, (left_px, left_py), 4)
        pygame.draw.line(surface, WHITE, leg_r, (right_px, right_py), 4)

        pygame.draw.circle(surface, DARK_GRAY, (round(left_px), round(left_py)), 4)
        pygame.draw.circle(surface, DARK_GRAY, (round(right_px), round(right_py)), 4)

        # --- Bicycle handlebar ---
        hb1, hb2 = ty(30, -5), ty(38, -20)
        pygame.draw.line(surface, GRAY, hb1, hb2, 4)
        hb3 = ty(38, -22)
        pygame.draw.circle(surface, GRAY, hb3, 5)

        # --- Basket (for fish!) ---
        b_tl = ty(-16, -44)
        basket_rect = pygame.Rect(b_tl[0], b_tl[1], 32, 14)
        pygame.draw.rect(surface, BROWN, basket_rect, 2)
        # A fish in the basket
        f_tl = ty(-8, -42)
        pygame.draw.ellipse(surface, ORANGE, (f_tl[0], f_tl[1], 14, 10))

    def get_rect(self):
        # Collision rect matches the visual body: head-through-wheels area.
        # Visual spans x~165..235, y~400..480 on ground.
        # self.y = GROUND_Y - 50 = 430. Center rect on the drawn shape.
        rect_x = self.x + 10
        rect_y = self.y - 30 + self.body_vert_offset
        rect_w = 70
        rect_h = 80
        return pygame.Rect(rect_x, rect_y, rect_w, rect_h)


class Fish:
    """A tasty fish for the pelican to collect!"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 15
        self.collected = False

    def update(self, speed):
        self.x -= speed
        # Slight bobbing
        self.y += random.choice([-1, 0, 0, 1])

    def draw(self, surface):
        # Fish body
        pygame.draw.ellipse(surface, ORANGE, (self.x, self.y, self.width, self.height))
        # Tail
        tail_points = [
            (self.x, self.y + self.height // 2),
            (self.x - 10, self.y - 2),
            (self.x - 10, self.y + self.height + 2),
        ]
        pygame.draw.polygon(surface, ORANGE, tail_points)
        # Eye
        pygame.draw.circle(surface, BLACK, (self.x + 20, self.y + self.height // 2), 3)
        # Fin
        pygame.draw.polygon(
            surface, ORANGE,
            [(self.x + 10, self.y + 2), (self.x + 5, self.y - 5), (self.x + 15, self.y + 2)],
        )

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Obstacle:
    """An obstacle (rock or car) to avoid."""

    def __init__(self, x, y, kind="rock"):
        self.x = x
        self.y = y
        self.kind = kind
        self.width = 40
        self.height = 40

    def update(self, speed):
        self.x -= speed

    def draw(self, surface):
        if self.kind == "rock":
            pygame.draw.circle(surface, DARK_GRAY, (self.x + 20, self.y + 20), 20)
            pygame.draw.circle(surface, GRAY, (self.x + 20, self.y + 20), 15, 2)
            # Some texture
            pygame.draw.circle(surface, GRAY, (self.x + 12, self.y + 12), 4)
            pygame.draw.circle(surface, GRAY, (self.x + 28, self.y + 18), 3)
        else:  # car
            pygame.draw.rect(surface, RED, (self.x, self.y + 10, 50, 20))
            pygame.draw.rect(surface, RED, (self.x, self.y, 50, 15))
            # Wheels
            pygame.draw.circle(surface, DARK_GRAY, (self.x + 10, self.y + 32), 8)
            pygame.draw.circle(surface, DARK_GRAY, (self.x + 40, self.y + 32), 8)
            # Windows
            pygame.draw.rect(surface, SKY_BLUE, (self.x + 8, self.y + 3, 12, 8))
            pygame.draw.rect(surface, SKY_BLUE, (self.x + 28, self.y + 3, 12, 8))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Cloud:
    """A fluffy cloud in the sky."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(30, 60)

    def update(self, speed):
        self.x -= speed * 0.3  # Parallax

    def draw(self, surface):
        color = (255, 255, 255, 200) if hasattr(pygame, "SWSURFACE") else WHITE
        pygame.draw.ellipse(surface, WHITE, (self.x, self.y, self.size, self.size * 0.6))
        pygame.draw.ellipse(
            surface, WHITE, (self.x + self.size * 0.3, self.y - 5, self.size * 0.7, self.size * 0.5)
        )


class Tree:
    """A nice tree on the background."""

    def __init__(self, x):
        self.x = x
        self.y = GROUND_Y - 20
        self.height = random.randint(60, 100)
        self.trunk_width = 16

    def update(self, speed):
        self.x -= speed

    def draw(self, surface):
        # Trunk
        pygame.draw.rect(
            surface, BROWN,
            (self.x + 12, self.y - self.height, self.trunk_width, self.height),
        )
        # Leaves (circle)
        leaf_color = (34, 139, 34) if random.random() > 0.3 else (50, 150, 50)
        pygame.draw.circle(
            surface, leaf_color,
            (self.x + 20, self.y - self.height - 10), 20,
        )
        # Some extra leaves
        pygame.draw.circle(
            surface, leaf_color,
            (self.x + 5, self.y - self.height), 12,
        )
        pygame.draw.circle(
            surface, leaf_color,
            (self.x + 35, self.y - self.height), 12,
        )


def show_start_screen():
    screen.fill(SKY_BLUE)
    title = big_font.render("Pelican Bike!", True, (255, 255, 255))
    subtitle = font.render("Press SPACE to start", True, (255, 255, 255))
    controls = font.render("SPACE/UP to jump | Avoid obstacles, collect fish!", True, (255, 255, 255))

    # Draw a pelican on the start screen
    pelican = Pelican(350, 250)
    pelican.draw(screen)

    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))
    screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 200))
    screen.blit(controls, (SCREEN_WIDTH // 2 - controls.get_width() // 2, 500))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
    return True


def show_game_over(score, fish_eaten):
    screen.fill(SKY_BLUE)
    go_text = big_font.render("Game Over!", True, RED)
    score_text = font.render(f"Score: {score}", True, WHITE)
    fish_text = font.render(f"Fish eaten: {fish_eaten}", True, ORANGE)
    restart_text = font.render("Press SPACE to play again, ESC to quit", True, WHITE)

    screen.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, 100))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 200))
    screen.blit(fish_text, (SCREEN_WIDTH // 2 - fish_text.get_width() // 2, 250))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 400))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False
    return False


def main():
    while True:
        if not show_start_screen():
            break

        # Game state
        pelican = Pelican(150, GROUND_Y - 50)
        fishes = []
        obstacles = []
        clouds = [Cloud(random.randint(0, SCREEN_WIDTH), random.randint(0, 200)) for _ in range(5)]
        trees = [Tree(random.randint(0, SCREEN_WIDTH * 2)) for _ in range(4)]
        score = 0
        fish_eaten = 0
        frame_count = 0
        game_over = False
        speed = SCROLL_SPEED

        while not game_over:
            clock.tick(FPS)

            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_SPACE, pygame.K_UP):
                        pelican.jump()

            # Update
            pelican.update()

            # Parallax clouds
            for cloud in clouds:
                cloud.update(speed)
                if cloud.x + cloud.size < 0:
                    cloud.x = SCREEN_WIDTH + random.randint(0, 100)
                    cloud.y = random.randint(0, 200)

            # Trees
            for tree in trees:
                tree.update(speed)
                if tree.x + 40 < 0:
                    tree.x = SCREEN_WIDTH + random.randint(0, 150)

            # Spawn fish and obstacles
            frame_count += 1
            if frame_count % 90 == 0 and len(fishes) < 4:
                fy = random.randint(GROUND_Y - 100, GROUND_Y - 40)
                fishes.append(Fish(SCREEN_WIDTH + 20, fy))

            if frame_count % 120 == 0 and len(obstacles) < 2:
                oy = GROUND_Y - 40
                kind = random.choice(["rock", "car"])
                obstacles.append(Obstacle(SCREEN_WIDTH + 20, oy, kind))

            # Update fishes
            for fish in fishes[:]:
                fish.update(speed)
                if fish.x + fish.width < 0:
                    fishes.remove(fish)

            # Update obstacles
            for obs in obstacles[:]:
                obs.update(speed)
                if obs.x + obs.width < 0:
                    obstacles.remove(obs)

            # Collision with fish
            pel_rect = pelican.get_rect()
            for fish in fishes[:]:
                if pel_rect.colliderect(fish.get_rect()):
                    fishes.remove(fish)
                    fish_eaten += 1
                    score += 50

            # Collision with obstacles
            for obs in obstacles:
                if pel_rect.colliderect(obs.get_rect()):
                    game_over = True

            # Score increases over time
            score += 0.1

            # Distance scoring (optional speed increase over time)
            if score > 100:
                speed = SCROLL_SPEED + (score // 200) * 0.5
                speed = min(speed, 12)

            # --- Draw ---
            screen.fill(SKY_BLUE)

            # Draw clouds
            for cloud in clouds:
                cloud.draw(screen)

            # Draw ground
            pygame.draw.rect(screen, GREEN, (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))
            pygame.draw.line(screen, BROWN, (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 3)

            # Draw road
            road_y = GROUND_Y + 20
            pygame.draw.rect(
                screen, GRAY,
                (0, road_y, SCREEN_WIDTH, SCREEN_HEIGHT - road_y),
            )
            # Road markings
            for i in range(0, SCREEN_WIDTH, 40):
                offset = (frame_count * speed) % 40
                pygame.draw.rect(
                    screen, WHITE,
                    (i * 2 - offset * 2, road_y + 10, 20, 4),
                )

            # Draw trees
            for tree in trees:
                tree.draw(screen)

            # Draw obstacles
            for obs in obstacles:
                obs.draw(screen)

            # Draw fishes
            for fish in fishes:
                fish.draw(screen)

            # Draw pelican
            pelican.draw(screen)

            # Draw HUD
            score_text = font.render(f"Score: {int(score)}", True, WHITE)
            fish_text = font.render(f"Fish: {fish_eaten}", True, ORANGE)
            screen.blit(score_text, (10, 10))
            screen.blit(fish_text, (10, 50))

            pygame.display.flip()

        # Game Over screen
        if not show_game_over(int(score), fish_eaten):
            break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
