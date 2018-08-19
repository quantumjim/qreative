import pygame

import numpy

pygame.init()

Lx = 1000
Ly = 250
delta = 3

size = (Lx,Ly)

screen = pygame.display.set_mode(size)
pygame.display.set_caption("Quantum Game")
render_buffer = pygame.Surface(size)


clock = pygame.time.Clock()

def character(x,y):
    render_buffer.blit(pygame.image.load('butterfly.png'), (x,y))
    
x = Lx/20
y = Ly/2
dx = 0
dy = 0
character(x,y)
while True:


    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                dx = -delta
            if event.key == pygame.K_RIGHT:
                dx = delta
            if event.key == pygame.K_UP:
                dy = -delta
            if event.key == pygame.K_DOWN:
                dy = delta
        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT,pygame.K_RIGHT]:
                dx = 0
            if event.key in [pygame.K_UP,pygame.K_DOWN]:
                dy = 0 
                
    x += dx
    y += dy
    
    render_buffer.fill((0, 0, 0)) 

    character(x,y)

    screen.blit(pygame.transform.scale(render_buffer, size), (0, 0))

    pygame.display.flip()
    
    clock.tick(60)

pygame.quit()
