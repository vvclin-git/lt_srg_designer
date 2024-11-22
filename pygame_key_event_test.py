import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((640, 480))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_KP_PLUS:
                print("按下了 '+' 鍵")
        # elif event.type == pygame.KEYUP:
        #     if event.key == pygame.K_a:
        #         print("釋放了 '+' 鍵")
