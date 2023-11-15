import pygame
from .settings import *

class Transition():
    def __init__(self, reset, player):
        
        # setup
        self.display_surface = pygame.display.get_surface()
        self.reset = reset
        self.player = player

        # overlay image
        self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.colour = 255
        self.speed = -2
        
    def play(self):
        self.colour += self.speed
        if self.colour < 0:
            self.colour = 0
            self.speed *= -1
            self.reset()
        if self.colour < 255:
            self.image.fill((self.colour, self.colour, self.colour))
            self.display_surface.blit(self.image, (0,0), special_flags=pygame.BLEND_RGB_MULT)
        else:
            self.player.sleep = False
            self.speed = -2
            self.colour = 255