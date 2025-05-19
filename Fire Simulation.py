import pygame
import numpy as np
import random
from noise import pnoise2

# --- Configuration ---
width, height = 1000, 800
GRID_SIZE = 4
ROWS, COLS = height // GRID_SIZE, width // GRID_SIZE
FIRE_SPREAD_CHANCE = 0.02
BURNOUT_CHANCE = 0.005
PARTICLES_PER_FIRE = 5
MAX_PARTICLES = 1500
RAIN_DURATION = 500

# --- Initialize ---
pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("🔥 Forest Fire Simulator ")
clock = pygame.time.Clock()

# --- Load Textures ---
tree_texture = pygame.Surface((GRID_SIZE, GRID_SIZE))
tree_texture.fill((34, 139, 34))
for _ in range(3):
    pygame.draw.circle(tree_texture, (0, 100, 0), 
                       (random.randint(0, GRID_SIZE), random.randint(0, GRID_SIZE)), 1)

fire_texture = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
fire_texture.fill((255, 69, 0, 220))

burnt_texture = pygame.Surface((GRID_SIZE, GRID_SIZE))
burnt_texture.fill((50, 50, 50))
for _ in range(2):
    pygame.draw.circle(burnt_texture, (30, 30, 30), 
                       (random.randint(0, GRID_SIZE), random.randint(0, GRID_SIZE)), 1)

particle_template = pygame.Surface((6, 6), pygame.SRCALPHA)
pygame.draw.circle(particle_template, (255, 255, 255, 255), (3, 3), 3)
pygame.draw.circle(particle_template, (255, 100, 0, 100), (3, 3), 3, width=1)

# --- Initialize Map ---
forest = np.zeros((ROWS, COLS))
humidity = np.zeros((ROWS, COLS))
rain_timer = 0

for i in range(ROWS):
    for j in range(COLS):
        humidity[i, j] = pnoise2(i/50, j/50)

for i in range(ROWS):
    for j in range(COLS):
        if random.random() < 0.7:
            forest[i, j] = 0
        else:
            forest[i, j] = 2

# --- Wind Field ---
def get_wind(tick):
    angle = np.sin(tick * 0.001) * np.pi / 4
    speed = 1.5 + np.cos(tick * 0.002)
    return np.array([np.cos(angle) * speed, np.sin(angle) * speed])

manual_wind = np.array([0.0, 0.0])
manual_control = True

# --- Particle Class ---
class Particle:
    def __init__(self, x, y, color):
        self.x = x + random.uniform(-2, 2)
        self.y = y + random.uniform(-2, 2)
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-2, -0.5)
        self.life = random.randint(30, 60)
        self.color = color

    def update(self, wind):
        self.vx += wind[0] * 0.01
        self.vy += wind[1] * 0.01
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            alpha = max(0, min(255, int(255 * (self.life / 60))))
            temp = particle_template.copy()
            temp.fill((*self.color, alpha), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(temp, (int(self.x), int(self.y)), special_flags=pygame.BLEND_ADD)

particles = []

# --- Main Loop ---
running = True
tick = 0
font = pygame.font.SysFont(None, 24)

raining = False  # 初始没有雨

while running:
    screen.fill((10, 10, 10))
    tick += 1

    if manual_control:
        wind = manual_wind
    else:
        wind = get_wind(tick)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        manual_wind[0] -= 0.5
    if keys[pygame.K_RIGHT]:
        manual_wind[0] += 0.5
    if keys[pygame.K_UP]:
        manual_wind[1] -= 0.5
    if keys[pygame.K_DOWN]:
        manual_wind[1] += 0.5

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                raining = not raining  # 空格键切换雨
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 鼠标左键
                mx, my = pygame.mouse.get_pos()
                grid_x = mx // GRID_SIZE
                grid_y = my // GRID_SIZE
                if 0 <= grid_x < COLS and 0 <= grid_y < ROWS:
                    if forest[grid_y, grid_x] == 0:
                        forest[grid_y, grid_x] = 1  # 放火点燃

    new_forest = forest.copy()
    for i in range(ROWS):
        for j in range(COLS):
            if forest[i, j] == 1:
                if len(particles) < MAX_PARTICLES:
                    for _ in range(PARTICLES_PER_FIRE):
                        color = random.choice([(255, 140, 0), (255, 100, 0), (255, 180, 0)])
                        particles.append(Particle(j*GRID_SIZE, i*GRID_SIZE, color))

                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        ni, nj = i+dy, j+dx
                        if 0 <= ni < ROWS and 0 <= nj < COLS:
                            if forest[ni, nj] == 0:
                                chance = FIRE_SPREAD_CHANCE * (1 - humidity[ni, nj])
                                if raining:
                                    chance *= 0.3
                                neighbors_on_fire = sum(
                                    (0 <= ni+y < ROWS and 0 <= nj+x < COLS and forest[ni+y, nj+x] == 1)
                                    for y in [-1, 0, 1] for x in [-1, 0, 1]
                                )
                                if neighbors_on_fire >= 5:
                                    chance *= 3
                                if random.random() < chance:
                                    new_forest[ni, nj] = 1

                burnout_chance = BURNOUT_CHANCE * (1.5 if raining else 1.0)
                if random.random() < burnout_chance:
                    new_forest[i, j] = 2

    forest = new_forest

    for i in range(ROWS):
        for j in range(COLS):
            pos = (j*GRID_SIZE, i*GRID_SIZE)
            if forest[i, j] == 0:
                screen.blit(tree_texture, pos)
            elif forest[i, j] == 1:
                glow = pygame.Surface((GRID_SIZE*4, GRID_SIZE*4), pygame.SRCALPHA)
                pygame.draw.circle(glow, (255, 140, 0, 120), (GRID_SIZE*2, GRID_SIZE*2), GRID_SIZE*2)
                screen.blit(glow, (pos[0]-GRID_SIZE, pos[1]-GRID_SIZE), special_flags=pygame.BLEND_ADD)
                screen.blit(fire_texture, pos)
            else:
                screen.blit(burnt_texture, pos)

    particles = [p for p in particles if p.life > 0]
    for p in particles:
        p.update(wind)
        p.draw(screen)

    if raining:
        for _ in range(100):
            x = random.randint(0, width)
            y = random.randint(0, height)
            pygame.draw.line(screen, (100, 100, 255), (x, y), (x+1, y+5), 1)

    # --- Draw wind debug info ---
    wind_text = font.render(f"Wind: ({manual_wind[0]:.2f}, {manual_wind[1]:.2f})", True, (255, 255, 255))
    rain_text = font.render(f"Raining: {'Yes' if raining else 'No'}", True, (100, 200, 255))
    screen.blit(wind_text, (10, 10))
    screen.blit(rain_text, (10, 30))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()