import pygame
from function import *

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()
run = True
pygame.display.set_caption("Zombie High School")

bg = loadImage("imgs/background.png", (2000 * 3, 2156 * 3))
player_f = loadImage("imgs/player/캐릭터.png", (421 / 3, 593 / 3))

px = -1000
py = -800
speed = 3

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            
    showImage(screen, bg, (px, py))

    keys = pygame.key.get_pressed()

    if keys[pygame.K_q]:
        run = False
    if keys[pygame.K_d]:
        px -= speed
    if keys[pygame.K_a]:
        px += speed
    if keys[pygame.K_w]:
        py += speed
    if keys[pygame.K_s]:
        py -= speed
        
    showImage(screen, player_f, ((screen.get_width() / 2) - (player_f.get_width() / 2), (screen.get_height() / 2) - (player_f.get_height() / 2)))
        

    pygame.display.update()

    clock.tick(60)


pygame.quit()