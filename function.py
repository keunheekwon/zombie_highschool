import pygame

def loadImage(path, size):
    image = pygame.image.load(path)
    image = pygame.transform.scale(image, size)
    return image

def showImage(screen, source, place):
    screen.blit(source, place)