import pygame
from collections import deque
from function import loadImage
import random
import math

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()
pygame.display.set_caption("Zombie High School")

ii = 0
bg = loadImage("imgs/background.png", (1920 + ii, 1080 + ii))
playerImage = loadImage("imgs/player/player.png", (300 // 4, 300 // 4))
zombieImage = loadImage("imgs/player/zombie.png", (300 // 4 + 5, 300 // 4 + 5))
bossImage = loadImage("imgs/player/zombie.png", (300 // 4 * 3 + 15, 300 // 4 * 3 + 15))
ballImage = loadImage("imgs/weapons/ball.png", (50, 50))
batImage = loadImage("imgs/weapons/bat.png", (100, 50))

font = pygame.font.Font(None, 74)

player_speed = 3
zombie_speed = 2
boss_speed = 1
ball_speed = 20
ball_cooldown = 200
bat_knockback_distance = 70
bat_throw_speed = 15
bat_cooldown = 1

pygame.mouse.set_visible(False)

def reset_game():
    global px, py, zombies, zombie_spawn_time, start_time, position_queue, run, balls, bats, last_ball_time, last_bat_time, stage, boss, zombies_to_kill, zombies_killed, zombies_spawned, tornado_mode, tornado_start_time
    px, py = 1000, 1000
    zombies = []
    balls = []
    bats = []
    zombie_spawn_time = pygame.time.get_ticks()
    start_time = pygame.time.get_ticks()
    position_queue = deque(maxlen=120)
    last_ball_time = 0
    last_bat_time = 0
    stage = 1
    boss = None
    run = True
    zombies_to_kill = 1
    zombies_killed = 0
    zombies_spawned = False
    tornado_mode = False
    tornado_start_time = 0

def show_stage_clear(stage):
    screen.fill((0, 0, 0))
    screen_width, screen_height = screen.get_size()
    
    stage_clear_text = font.render(f"Stage {stage} Clear!", True, (0, 255, 0))
    stage_clear_rect = stage_clear_text.get_rect(center=(screen_width / 2, screen_height / 2))
    screen.blit(stage_clear_text, stage_clear_rect)
    
    pygame.display.update()
    pygame.time.wait(2000)

def fire_ball(target_x, target_y):
    global last_ball_time
    current_time = pygame.time.get_ticks()
    if current_time - last_ball_time >= ball_cooldown:
        direction_x = target_x - px
        direction_y = target_y - py
        distance = math.sqrt(direction_x ** 2 + direction_y ** 2)
        if distance != 0:
            direction_x /= distance
            direction_y /= distance
        balls.append({'position': [px + playerImage.get_width() // 2, py + playerImage.get_height() // 2], 'direction': [direction_x, direction_y]})
        last_ball_time = current_time

def throw_tornado_balls():
    for _ in range(500):
        angle = random.uniform(0, 2 * math.pi)
        direction_x = math.cos(angle)
        direction_y = math.sin(angle)
        balls.append({'position': [px + playerImage.get_width() // 2, py + playerImage.get_height() // 2], 'direction': [direction_x, direction_y]})

def spawn_zombie():
    side = random.choice(['top', 'bottom', 'left', 'right'])
    if side == 'top':
        position = [random.randint(0, screen.get_width()), 0]
    elif side == 'bottom':
        position = [random.randint(0, screen.get_width()), screen.get_height() - zombieImage.get_height()]
    elif side == 'left':
        position = [0, random.randint(0, screen.get_height())]
    elif side == 'right':
        position = [screen.get_width() - zombieImage.get_width(), random.randint(0, screen.get_height())]

    zombies.append({
        'position': position,
        'delay': random.randint(30, 120)
    })

def spawn_boss():
    global boss
    if boss is None:
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            position = [random.randint(0, bg.get_width()), 0]
        elif side == 'bottom':
            position = [random.randint(0, bg.get_width()), bg.get_height() - bossImage.get_height()]
        elif side == 'left':
            position = [0, random.randint(0, bg.get_height())]
        elif side == 'right':
            position = [bg.get_width() - bossImage.get_width(), random.randint(0, bg.get_height())]
        
        boss = {
            'position': position,
            'health': 10,
            'delay': 60
        }

def move_boss(boss):
    if len(position_queue) >= boss['delay']:
        target_x, target_y = position_queue[-boss['delay']]
        direction_x = target_x - boss['position'][0]
        direction_y = target_y - boss['position'][1]
        distance = (direction_x**2 + direction_y**2) ** 0.5

        if distance != 0:
            boss['position'][0] += boss_speed * direction_x / distance
            boss['position'][1] += boss_speed * direction_y / distance

        boss['position'][0] = max(0, min(boss['position'][0], bg.get_width() - bossImage.get_width()))
        boss['position'][1] = max(0, min(boss['position'][1], bg.get_height() - bossImage.get_height()))

def move_zombie(zombie):
    if len(position_queue) >= zombie['delay']:
        target_x, target_y = position_queue[-zombie['delay']]
        direction_x = target_x - zombie['position'][0]
        direction_y = target_y - zombie['position'][1]
        distance = (direction_x**2 + direction_y**2) ** 0.5

        if distance != 0:
            zombie['position'][0] += zombie_speed * direction_x / distance
            zombie['position'][1] += zombie_speed * direction_y / distance

        zombie['position'][0] = max(0, min(zombie['position'][0], bg.get_width() - zombieImage.get_width()))
        zombie['position'][1] = max(0, min(zombie['position'][1], bg.get_height() - zombieImage.get_height()))

def throw_bat():
    global last_bat_time
    current_time = pygame.time.get_ticks()
    if current_time - last_bat_time >= bat_cooldown:
        closest_zombie = None
        closest_distance = float('inf')
        for zombie in zombies:
            distance = math.sqrt((zombie['position'][0] - px) ** 2 + (zombie['position'][1] - py) ** 2)
            if distance < closest_distance:
                closest_zombie = zombie
                closest_distance = distance

        if closest_zombie:
            direction_x = closest_zombie['position'][0] - px
            direction_y = closest_zombie['position'][1] - py
            distance = math.sqrt(direction_x ** 2 + direction_y ** 2)
            if distance != 0:
                direction_x /= distance
                direction_y /= distance
            bats.append({'position': [px + playerImage.get_width() // 2, py + playerImage.get_height() // 2], 'direction': [direction_x, direction_y]})
            last_bat_time = current_time

reset_game()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            fire_ball(mouse_x, mouse_y)

    keys = pygame.key.get_pressed()

    if keys[pygame.K_q]:
        pygame.quit()
        exit()
    if keys[pygame.K_d]:
        px += player_speed
    if keys[pygame.K_a]:
        px -= player_speed
    if keys[pygame.K_w]:
        py -= player_speed
    if keys[pygame.K_s]:
        py += player_speed

    if keys[pygame.K_f]:
        throw_bat()

    if keys[pygame.K_e]:
        if not tornado_mode:
            tornado_mode = True
            tornado_start_time = pygame.time.get_ticks()
            throw_tornado_balls()

    px = max(0, min(px, bg.get_width() - playerImage.get_width()))
    py = max(0, min(py, bg.get_height() - playerImage.get_height()))

    position_queue.append((px, py))
    
    current_time = pygame.time.get_ticks()
    
    if current_time - zombie_spawn_time > 3000 and not zombies_spawned:
        num_zombies = stage * 2
        for _ in range(num_zombies):
            spawn_zombie()
        zombies_spawned = True

    if stage % 10 == 0 and boss is None:
        spawn_boss()

    if tornado_mode and (current_time - tornado_start_time > 5000):
        tornado_mode = False

    screen.blit(bg, (0, 0))
    screen.blit(playerImage, (px, py))

    player_rect = pygame.Rect(px, py, playerImage.get_width(), playerImage.get_height())

    if boss:
        move_boss(boss)
        boss_rect = pygame.Rect(boss['position'][0], boss['position'][1], bossImage.get_width(), bossImage.get_height())

        if player_rect.colliderect(boss_rect):
            end_time = pygame.time.get_ticks()
            total_time = (end_time - start_time) / 1000
            print(f"Game Over! The boss caught you. You survived for {total_time:.2f} seconds.")
            pygame.quit()
            exit()

        screen.blit(bossImage, (boss['position'][0], boss['position'][1]))

    for zombie in zombies[:]:
        move_zombie(zombie)
        zombie_rect = pygame.Rect(zombie['position'][0], zombie['position'][1], zombieImage.get_width(), zombieImage.get_height())

        if player_rect.colliderect(zombie_rect):
            end_time = pygame.time.get_ticks()
            total_time = (end_time - start_time) / 1000
            print(f"Game Over! The zombie caught you. You survived for {total_time:.2f} seconds.")
            pygame.quit()
            exit()

        screen.blit(zombieImage, (zombie['position'][0], zombie['position'][1]))

    for ball in balls[:]:
        ball['position'][0] += ball['direction'][0] * ball_speed
        ball['position'][1] += ball['direction'][1] * ball_speed
        ball_rect = pygame.Rect(ball['position'][0], ball['position'][1], ballImage.get_width(), ballImage.get_height())

        for zombie in zombies[:]:
            zombie_rect = pygame.Rect(zombie['position'][0], zombie['position'][1], zombieImage.get_width(), zombieImage.get_height())
            if ball_rect.colliderect(zombie_rect):
                if zombie in zombies:
                    zombies.remove(zombie)
                if ball in balls:
                    balls.remove(ball)
                zombies_killed += 1
                if zombies_to_kill - zombies_killed == 0:
                    if not boss:
                        show_stage_clear(stage)
                        zombies_to_kill = stage * 2
                        zombies_killed = 0
                        stage += 1
                        zombies.clear()
                        balls.clear()
                        zombies_spawned = False
                    break

        if boss:
            boss_rect = pygame.Rect(boss['position'][0], boss['position'][1], bossImage.get_width(), bossImage.get_height())
            if ball_rect.colliderect(boss_rect):
                boss['health'] -= 1
                if ball in balls:
                    balls.remove(ball)
                if boss['health'] <= 0:
                    boss = None
                    show_stage_clear(stage)
                    zombies_to_kill = stage * 2
                    zombies_killed = 0
                    stage += 1
                    zombies.clear()
                    balls.clear()
                    zombies_spawned = False
                break

        if 0 <= ball['position'][0] <= screen.get_width() and 0 <= ball['position'][1] <= screen.get_height():
            screen.blit(ballImage, ball['position'])
        else:
            if ball in balls:
                balls.remove(ball)

    for bat in bats[:]:
        bat['position'][0] += bat['direction'][0] * bat_throw_speed
        bat['position'][1] += bat['direction'][1] * bat_throw_speed
        bat_rect = pygame.Rect(bat['position'][0], bat['position'][1], batImage.get_width(), batImage.get_height())

        for zombie in zombies[:]:
            zombie_rect = pygame.Rect(zombie['position'][0], zombie['position'][1], zombieImage.get_width(), zombieImage.get_height())
            if bat_rect.colliderect(zombie_rect):
                direction_x = zombie['position'][0] - px
                direction_y = zombie['position'][1] - py
                distance = math.sqrt(direction_x ** 2 + direction_y ** 2)
                if distance != 0:
                    direction_x /= distance
                    direction_y /= distance

                zombie['position'][0] += direction_x * bat_knockback_distance
                zombie['position'][1] += direction_y * bat_knockback_distance

                zombie['position'][0] = max(0, min(zombie['position'][0], bg.get_width() - zombieImage.get_width()))
                zombie['position'][1] = max(0, min(zombie['position'][1], bg.get_height() - zombieImage.get_height()))

                if bat in bats:
                    bats.remove(bat)

        if boss:
            boss_rect = pygame.Rect(boss['position'][0], boss['position'][1], bossImage.get_width(), bossImage.get_height())
            if bat_rect.colliderect(boss_rect):
                boss['health'] -= 1
                if bat in bats:
                    bats.remove(bat)
                if boss['health'] <= 0:
                    boss = None
                    show_stage_clear(stage)
                    zombies_to_kill = stage * 2
                    zombies_killed = 0
                    stage += 1
                    zombies.clear()
                    bats.clear()
                    zombies_spawned = False
                break

        if 0 <= bat['position'][0] <= screen.get_width() and 0 <= bat['position'][1] <= screen.get_height():
            screen.blit(batImage, bat['position'])
        else:
            if bat in bats:
                bats.remove(bat)

    current_survival_time = (pygame.time.get_ticks() - start_time) / 1000
    time_text = font.render(f"Time: {current_survival_time:.2f} s", True, (255, 255, 255))
    screen.blit(time_text, (50, 50))

    zombies_remaining = zombies_to_kill - zombies_killed
    zombies_needed_text = font.render(f"Zombies to Kill: {zombies_remaining}", True, (255, 255, 255))
    screen.blit(zombies_needed_text, (50, 100))

    mouse_x, mouse_y = pygame.mouse.get_pos()
    pygame.draw.line(screen, (0, 255, 0), (mouse_x - 10, mouse_y), (mouse_x + 10, mouse_y), 2)
    pygame.draw.line(screen, (0, 255, 0), (mouse_x, mouse_y - 10), (mouse_x, mouse_y + 10), 2)

    pygame.display.update()
    clock.tick(60)
