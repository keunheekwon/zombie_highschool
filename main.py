import tkinter.messagebox
import pygame
from collections import deque
from function import loadImage
import random
import math
import tkinter

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()
pygame.display.set_caption("Zombie BaseBall")

ii = 0
bg = loadImage("imgs/background.jpg", (screen.get_size()[0] + ii, screen.get_size()[1] + ii))
playerImage = loadImage("imgs/player/player.png", (300 // 4, 300 // 4))
zombieImage = loadImage("imgs/player/zombie.png", ((300 // 4 + 5) * 2, (300 // 4 + 5) * 2))
bossImage = loadImage("imgs/player/zombie.png", ((300 // 4 * 3 + 15) * 2, (300 // 4 * 3 + 15) * 2))
ballImage = loadImage("imgs/weapons/ball.png", (50, 50))
batImage = loadImage("imgs/weapons/bat.png", (100, 50))

font = pygame.font.Font(None, 74)

player_speed = 3
player_speed_boost = 10
player_hp = 3
zombie_speed = 2
boss_speed = 1
ball_speed = 20
ball_cooldown = 200
bat_knockback_distance = 100
bat_throw_speed = 15
bat_cooldown = 500
speed_boost_duration = 5000

pygame.mouse.set_visible(False)

def reset_game():
    global px, py, zombies, player_speed, zombie_spawn_time, zombie_spawn_interval, start_time, position_queue, run, balls, bats, last_ball_time, last_bat_time, stage, boss, zombies_to_kill, zombies_killed, zombies_spawned, tornado_mode, tornado_start_time, zombie_last_spawn_time, zombies_spawned_count, speed_boost_start_time, speed_boost_active
    px, py = 960, 540
    zombies = []
    balls = []
    bats = []
    zombie_spawn_time = pygame.time.get_ticks()
    zombie_spawn_interval = random.randint(1000, 2000)
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
    zombie_last_spawn_time = 0
    zombies_spawned_count = 0
    speed_boost_start_time = 0
    speed_boost_active = False

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
    for _ in range(100):
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
    zombies.append({'position': position, 'delay': random.randint(30, 120)})

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
        boss = {'position': position, 'health': 10, 'delay': 60}

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
    global last_bat_time, speed_boost_start_time, speed_boost_active
    current_time = pygame.time.get_ticks()
    if current_time - last_bat_time >= bat_cooldown:
        closest_zombie = min(zombies, key=lambda z: math.sqrt((z['position'][0] - px) ** 2 + (z['position'][1] - py) ** 2), default=None)
        if closest_zombie:
            direction_x = closest_zombie['position'][0] - px
            direction_y = closest_zombie['position'][1] - py
            distance = math.sqrt(direction_x ** 2 + direction_y ** 2)
            if distance != 0:
                direction_x /= distance
                direction_y /= distance
            bats.append({'position': [px + playerImage.get_width() // 2, py + playerImage.get_height() // 2], 'direction': [direction_x, direction_y]})
            speed_boost_start_time = pygame.time.get_ticks()
            speed_boost_active = True
        last_bat_time = current_time

reset_game()

key_right_pressed = False
key_left_pressed = False

while run:
    try:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                fire_ball(mouse_x, mouse_y)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT and not key_right_pressed:
                    zombies_to_kill = stage * 2
                    zombies_killed = 0
                    zombies_spawned_count = 0
                    stage += 1
                    zombies.clear()
                    balls.clear()
                    zombies_spawned = False
                    key_right_pressed = True
                elif event.key == pygame.K_LEFT and not key_left_pressed:
                    stage -= 1
                    zombies_to_kill = stage * 2
                    zombies_killed = 0
                    zombies_spawned_count = 0
                    zombies.clear()
                    balls.clear()
                    zombies_spawned = False
                    key_left_pressed = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    key_right_pressed = False
                elif event.key == pygame.K_LEFT:
                    key_left_pressed = False

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
        if keys[pygame.K_e] and not tornado_mode:
            tornado_mode = True
            tornado_start_time = pygame.time.get_ticks()
            throw_tornado_balls()

        if tornado_mode and pygame.time.get_ticks() - tornado_start_time > 10000:
            tornado_mode = False
            
        if speed_boost_active and pygame.time.get_ticks() - speed_boost_start_time < speed_boost_duration:
            player_speed = player_speed_boost
        elif pygame.time.get_ticks() - speed_boost_start_time < speed_boost_duration:
            speed_boost_active = False
        else:
            player_speed = 3

        px = max(0, min(px, bg.get_width() - playerImage.get_width()))
        py = max(0, min(py, bg.get_height() - playerImage.get_height()))
        position_queue.append((px, py))

        current_time = pygame.time.get_ticks()
        zombies_to_kill = stage * 2

        if not zombies_spawned and zombies_to_kill > zombies_spawned_count:
            if current_time - zombie_last_spawn_time > zombie_spawn_interval:
                spawn_zombie()
                zombies_spawned_count += 1
                zombie_last_spawn_time = current_time
                zombie_spawn_interval = random.randint(0, 500)
        else:
            zombies_spawned = True

        if stage % 10 == 0 and boss is None:
            spawn_boss()

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
                tkinter.messagebox.showerror("Game Over", f"보스에게 잡혔어요! {stage}스테이지 {total_time:.2f}초 동안 살아남았어요")
                exit()
            screen.blit(bossImage, (boss['position'][0], boss['position'][1]))
            
        if player_hp <= 0:
            end_time = pygame.time.get_ticks()
            total_time = (end_time - start_time) / 1000
            print(f"Game Over! The zombie caught you. You survived for {total_time:.2f} seconds.")
            pygame.quit()
            tkinter.messagebox.showerror("Game Over", f"좀비에게 잡혔어요! {stage}스테이지 {total_time:.2f}초 동안 살아남았어요")
            exit()

        for zombie in zombies[:]:
            move_zombie(zombie)
            zombie_rect = pygame.Rect(zombie['position'][0], zombie['position'][1], zombieImage.get_width(), zombieImage.get_height())
            if player_rect.colliderect(zombie_rect):
                player_hp -= 1
                if player_hp < 0:
                    end_time = pygame.time.get_ticks()
                    total_time = (end_time - start_time) / 1000
                    print(f"Game Over! The zombie caught you. You survived for {total_time:.2f} seconds.")
                    pygame.quit()
                    exit()
                else:
                    if len(zombies) == 1:
                        if not boss:
                            show_stage_clear(stage)
                            zombies_to_kill = stage * 2
                            zombies_killed = 0
                            zombies_spawned_count = 0
                            stage += 1
                            zombies.clear()
                            balls.clear()
                            zombies_spawned = False
                            
                        break
                            
                    zombies.remove(zombie)
                    zombies_killed += 1
            screen.blit(zombieImage, (zombie['position'][0], zombie['position'][1]))

        for ball in balls[:]:
            ball['position'][0] += ball['direction'][0] * ball_speed
            ball['position'][1] += ball['direction'][1] * ball_speed
            ball_rect = pygame.Rect(ball['position'][0], ball['position'][1], ballImage.get_width(), ballImage.get_height())
            for zombie in zombies[:]:
                zombie_rect = pygame.Rect(zombie['position'][0], zombie['position'][1], zombieImage.get_width(), zombieImage.get_height())
                if ball_rect.colliderect(zombie_rect):
                    zombies.remove(zombie)
                    balls.remove(ball)
                    zombies_killed += 1
                    if zombies_to_kill - zombies_killed == 0:
                        if not boss:
                            show_stage_clear(stage)
                            zombies_to_kill = stage * 2
                            zombies_killed = 0
                            zombies_spawned_count = 0
                            stage += 1
                            zombies.clear()
                            balls.clear()
                            zombies_spawned = False
                    break
            if boss:
                boss_rect = pygame.Rect(boss['position'][0], boss['position'][1], bossImage.get_width(), bossImage.get_height())
                if ball_rect.colliderect(boss_rect):
                    boss['health'] -= 1
                    balls.remove(ball)
                    if boss['health'] <= 0:
                        boss = None
                        show_stage_clear(stage)
                        zombies_to_kill = stage * 2
                        zombies_killed = 0
                        zombies_spawned_count = 0
                        stage += 1
                        zombies.clear()
                        balls.clear()
                        zombies_spawned = False
                    break
            if 0 <= ball['position'][0] <= screen.get_width() and 0 <= ball['position'][1] <= screen.get_height():
                screen.blit(ballImage, ball['position'])
            else:
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
                    bats.remove(bat)
            if boss:
                boss_rect = pygame.Rect(boss['position'][0], boss['position'][1], bossImage.get_width(), bossImage.get_height())
                if bat_rect.colliderect(boss_rect):
                    boss['health'] -= 1
                    bats.remove(bat)
                    if boss['health'] <= 0:
                        boss = None
                        show_stage_clear(stage)
                        zombies_to_kill = stage * 2
                        zombies_killed = 0
                        zombies_spawned_count = 0
                        stage += 1
                        zombies.clear()
                        bats.clear()
                        zombies_spawned = False
                    break
            if 0 <= bat['position'][0] <= screen.get_width() and 0 <= bat['position'][1] <= screen.get_height():
                screen.blit(batImage, bat['position'])
            else:
                bats.remove(bat)
                
        if stage > 30:
            clear_time = pygame.time.get_ticks()
            pygame.quit()
            tkinter.messagebox.showinfo("Game Clear!", f"게임을 클리어했어요! {stage - 1}스테이지 {clear_time / 1000:.2f}초 동안 살아남았어요")
            tkinter.messagebox.showinfo("Zombie BaseBall", "플레이 해주셔서 감사합니다")
            exit()

        current_survival_time = (pygame.time.get_ticks() - start_time) / 1000
        time_text = font.render(f"Time: {current_survival_time:.2f} s", True, (255, 255, 255))
        screen.blit(time_text, (50, 50))

        zombies_remaining = zombies_to_kill - zombies_killed
        zombies_needed_text = font.render(f"Zombies to Kill: {zombies_remaining}", True, (255, 255, 255))
        screen.blit(zombies_needed_text, (50, 100))
        
        hp_text = font.render(f"HP: {player_hp}", True, (255, 255, 255))
        screen.blit(hp_text, (50, 150))

        mouse_x, mouse_y = pygame.mouse.get_pos()
        pygame.draw.line(screen, (255, 255, 255), (mouse_x - 10, mouse_y), (mouse_x + 10, mouse_y), 5)
        pygame.draw.line(screen, (0, 0, 0), (mouse_x, mouse_y - 10), (mouse_x, mouse_y + 10), 5)

        pygame.display.update()
        clock.tick(60)
    except:
        continue