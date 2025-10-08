import math
import random
import sys
from dataclasses import dataclass

import pygame

# --------- Config ---------
WIDTH, HEIGHT = 900, 700
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Gameplay
START_ASTEROIDS = 5
MAX_BULLETS = 4
SHIP_INVINCIBLE_MS = 2000

# --------- Helper math ---------

def wrap_position(pos):
    x, y = pos
    return (x % WIDTH, y % HEIGHT)


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


# --------- Game objects ---------
@dataclass
class GameObject:
    pos: pygame.math.Vector2
    vel: pygame.math.Vector2
    radius: float

    def update(self, dt):
        self.pos += self.vel * dt
        self.pos = pygame.math.Vector2(wrap_position(self.pos))


class Ship(GameObject):
    def __init__(self, pos):
        super().__init__(pygame.math.Vector2(pos), pygame.math.Vector2(0, 0), 12)
        self.angle = -math.pi / 2  # facing up
        self.thrusting = False
        self.rotation_dir = 0
        self.lives = 3
        self.invincible_timer = 0

    def rotate(self, direction):
        self.rotation_dir = direction

    def thrust(self, on):
        self.thrusting = on

    def shoot(self):
        # spawn bullet slightly ahead of ship
        dir_vec = pygame.math.Vector2(math.cos(self.angle), math.sin(self.angle))
        speed = 500
        bpos = self.pos + dir_vec * (self.radius + 5)
        bvel = self.vel + dir_vec * speed
        return Bullet(bpos, bvel)

    def update(self, dt):
        # rotate
        self.angle += self.rotation_dir * 4.0 * dt
        # thrust
        if self.thrusting:
            accel = pygame.math.Vector2(math.cos(self.angle), math.sin(self.angle)) * 200
            self.vel += accel * dt
        # apply friction
        self.vel *= 0.999
        super().update(dt)
        if self.invincible_timer > 0:
            self.invincible_timer = max(0, self.invincible_timer - dt * 1000)

    def draw(self, surf):
        # ship shape (triangle)
        dir_vec = pygame.math.Vector2(math.cos(self.angle), math.sin(self.angle))
        right = pygame.math.Vector2(math.cos(self.angle + math.pi * 2 / 3), math.sin(self.angle + math.pi * 2 / 3))
        left = pygame.math.Vector2(math.cos(self.angle - math.pi * 2 / 3), math.sin(self.angle - math.pi * 2 / 3))
        p1 = self.pos + dir_vec * 18
        p2 = self.pos + right * 14
        p3 = self.pos + left * 14
        alpha = 255
        if self.invincible_timer > 0:
            # blink effect
            alpha = 80 + int(175 * (self.invincible_timer % 300) / 300)
        points = [p1, p2, p3]
        pygame.draw.polygon(surf, WHITE + (alpha,), [(p.x, p.y) for p in points])
        # thrust flame
        if self.thrusting:
            flame = self.pos - dir_vec * 14
            pygame.draw.circle(surf, WHITE, (int(flame.x), int(flame.y)), 3)


class Bullet(GameObject):
    def __init__(self, pos, vel):
        super().__init__(pygame.math.Vector2(pos), pygame.math.Vector2(vel), 2)
        self.life = 1.5  # seconds

    def update(self, dt):
        super().update(dt)
        self.life -= dt

    def draw(self, surf):
        pygame.draw.circle(surf, WHITE, (int(self.pos.x), int(self.pos.y)), self.radius)


class Asteroid(GameObject):
    def __init__(self, pos, size=3):
        # size: 3=large,2=medium,1=small
        radius = {3: 45, 2: 25, 1: 12}[size]
        speed = random.uniform(20, 80) / size
        angle = random.uniform(0, math.pi * 2)
        vel = pygame.math.Vector2(math.cos(angle), math.sin(angle)) * speed
        super().__init__(pygame.math.Vector2(pos), vel, radius)
        self.size = size
        # random jagged polygon shape
        self.vertex_count = random.randint(8, 12)
        self.jag = [random.uniform(0.7, 1.3) for _ in range(self.vertex_count)]
        self.rot = random.uniform(-0.5, 0.5)
        self.rotation = 0

    def update(self, dt):
        self.rotation += self.rot * dt
        super().update(dt)

    def draw(self, surf):
        points = []
        for i in range(self.vertex_count):
            ang = (i / self.vertex_count) * math.tau + self.rotation
            r = self.radius * self.jag[i]
            points.append((self.pos.x + math.cos(ang) * r, self.pos.y + math.sin(ang) * r))
        pygame.draw.polygon(surf, WHITE, points, 2)


# --------- Game manager ---------
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Asteroids - Python + Pygame")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)
        self.restart()

    def restart(self):
        self.ship = Ship((WIDTH / 2, HEIGHT / 2))
        self.bullets = []
        self.asteroids = []
        self.score = 0
        self.game_over = False
        self.pause = False
        for _ in range(START_ASTEROIDS):
            self.spawn_asteroid(None, 3)

    def spawn_asteroid(self, near_pos=None, size=3):
        # spawn away from ship
        while True:
            x = random.uniform(0, WIDTH)
            y = random.uniform(0, HEIGHT)
            if near_pos is None or distance((x, y), (self.ship.pos.x, self.ship.pos.y)) > 120:
                break
        self.asteroids.append(Asteroid((x, y), size))

    def split_asteroid(self, ast):
        if ast.size > 1:
            for _ in range(2):
                a = Asteroid(ast.pos, ast.size - 1)
                # give them different velocities
                a.vel = ast.vel.rotate(random.uniform(-60, 60)) * random.uniform(0.8, 1.3)
                self.asteroids.append(a)

    def update(self, dt):
        if self.game_over or self.pause:
            return
        self.ship.update(dt)
        for b in list(self.bullets):
            b.update(dt)
            if b.life <= 0:
                self.bullets.remove(b)
        for a in self.asteroids:
            a.update(dt)
        # collisions: bullets vs asteroids
        for b in list(self.bullets):
            for a in list(self.asteroids):
                if distance(b.pos, a.pos) < b.radius + a.radius:
                    try:
                        self.bullets.remove(b)
                    except ValueError:
                        pass
                    try:
                        self.asteroids.remove(a)
                    except ValueError:
                        pass
                    self.score += {3: 20, 2: 50, 1: 100}[a.size]
                    self.split_asteroid(a)
                    break
        # ship vs asteroids
        if self.ship.invincible_timer <= 0:
            for a in list(self.asteroids):
                if distance(self.ship.pos, a.pos) < self.ship.radius + a.radius:
                    self.ship.lives -= 1
                    self.ship.pos = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
                    self.ship.vel = pygame.math.Vector2(0, 0)
                    self.ship.invincible_timer = SHIP_INVINCIBLE_MS
                    if self.ship.lives <= 0:
                        self.game_over = True
                    break
        # spawn new wave if all asteroids destroyed
        if not self.asteroids:
            # create next wave with more asteroids
            for _ in range(START_ASTEROIDS + self.score // 200):
                self.spawn_asteroid(None, 3)

    def draw_ui(self):
        s = self.font.render(f"Score: {self.score}", True, WHITE)
        lives = self.font.render("Lives: " + "❤" * self.ship.lives, True, WHITE)
        self.screen.blit(s, (10, 10))
        self.screen.blit(lives, (10, 36))
        if self.pause:
            txt = self.font.render("PAUSED - press P to resume", True, WHITE)
            r = txt.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(txt, r)
        if self.game_over:
            go = self.font.render("GAME OVER - press R to restart", True, WHITE)
            r = go.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(go, r)

    def run(self):
        dt = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_LEFT:
                        self.ship.rotate(-1)
                    if event.key == pygame.K_RIGHT:
                        self.ship.rotate(1)
                    if event.key == pygame.K_UP:
                        self.ship.thrust(True)
                    if event.key == pygame.K_SPACE:
                        if len(self.bullets) < MAX_BULLETS and not self.game_over:
                            self.bullets.append(self.ship.shoot())
                    if event.key == pygame.K_p:
                        self.pause = not self.pause
                    if event.key == pygame.K_r:
                        self.restart()
                elif event.type == pygame.KEYUP:
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        self.ship.rotate(0)
                    if event.key == pygame.K_UP:
                        self.ship.thrust(False)

            # update
            self.update(dt)

            # draw
            self.screen.fill(BLACK)
            for a in self.asteroids:
                a.draw(self.screen)
            for b in self.bullets:
                b.draw(self.screen)
            self.ship.draw(self.screen)
            self.draw_ui()

            pygame.display.flip()
            dt = self.clock.tick(FPS) / 1000.0


if __name__ == "__main__":
    Game().run()
