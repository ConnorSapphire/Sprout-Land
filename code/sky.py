import pygame
from .settings import *
from .support import *
from .sprites import Generic
from .timer import Timer
from random import randint, choice

class Sky:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.full_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.start_colour = [255, 255, 255]
        self.colour = self.start_colour.copy()
        self.end_colour = (38, 101, 189)
        
    def display(self, dt):
        for index, value in enumerate(self.end_colour):
            if self.colour[index] > value:
                self.colour[index] -= 2 * dt
        self.full_surf.fill(self.colour)
        self.display_surface.blit(self.full_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
    def reset(self):
        self.colour = self.start_colour.copy()

class Drops(Generic):
    def __init__(self, pos, surf, groups, z, moving):
        
        # general setup
        super().__init__(pos, surf, groups)
        self.lifetime = randint(400, 500)
        self.timer = Timer(self.lifetime, self.destroy)
        self.timer.activate()
        
        # moving
        self.moving = moving
        if self.moving:
            self.pos = pygame.math.Vector2(self.rect.topleft)
            self.direction = pygame.math.Vector2(-2, 4)
            self.speed = randint(200, 250)
        
    def destroy(self):
        self.kill()
    
    def animate(self, dt):
        if self.moving:
            self.pos += self.direction * self.speed * dt
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))
    
    def update(self, dt):
        self.timer.update()
        self.animate(dt)
    

class Rain:
    def __init__(self, all_sprites):
        self.all_sprites = all_sprites
        self.rain_drops = import_folder('./graphics/rain/drops')
        self.rain_floor = import_folder('./graphics/rain/floor')
        self.floor_w, self.floor_h = pygame.image.load('./graphics/world/ground.png').get_size()
        
    def create_floor(self):
        Drops(
            pos=(randint(0,self.floor_w),randint(0,self.floor_h)),
            surf=choice(self.rain_floor),
            groups=self.all_sprites,
            z=LAYERS['rain floor'],
            moving=False
        )
    
    def create_drops(self):
        Drops(
            pos=(randint(0,self.floor_w),randint(0,self.floor_h)),
            surf=choice(self.rain_drops),
            groups=self.all_sprites,
            z=LAYERS['rain drops'],
            moving=True
        )
        
    def update(self, dt):
        self.create_floor()
        self.create_drops()