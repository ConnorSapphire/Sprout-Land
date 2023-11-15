import pygame
from .settings import *
from .timer import Timer
from random import randint, choice

class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, z = LAYERS['main']):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.copy().inflate(self.rect.width * -0.5, 0)
        self.z = z
        
class Barrier(Generic):
    def __init__(self, pos, surf, groups, z = LAYERS['main']):
        super().__init__(pos, surf, groups, z)
        self.hitbox = self.rect.copy().inflate(self.rect.width * 0.4, self.rect.height * 0.4)
        
class VerticalBarrier(Generic):
    def __init__(self, pos, surf, groups, z = LAYERS['main'], alignment = 'center'):
        super().__init__(pos, surf, groups, z)
        self.hitbox = self.rect.copy().inflate(self.rect.width * -0.5, 0)
        self.hitbox.bottom = self.rect.bottom
        if alignment == 'left':
            self.hitbox.left = self.rect.left
        if alignment == 'right':
            self.hitbox.right = self.rect.right
        
class HorizontalBarrier(Generic):
    def __init__(self, pos, surf, groups, z = LAYERS['main'], alignment = 'center'):
        super().__init__(pos, surf, groups, z)
        self.hitbox = self.rect.copy().inflate(self.rect.width * -0.5, self.rect.height * -0.7)
        self.hitbox.bottom = self.rect.bottom
        if alignment == 'left':
            self.hitbox.left = self.rect.left
        if alignment == 'right':
            self.hitbox.right = self.rect.right
        
class Water(Generic):
    def __init__(self, pos, frames, groups):
        
        # animation setup
        self.frames = frames
        self.frame_index = 0
        
        # sprite setup
        super().__init__(pos = pos,
                         surf = self.frames[self.frame_index],
                         groups = groups,
                         z = LAYERS['water'])
    
    def animate(self, dt):
        
        # update frame
        self.frame_index += 5 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        
        # update sprite
        self.image = self.frames[int(self.frame_index)]
        
    def update(self, dt):
        self.animate(dt)
        
class WildFlower(Generic):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups)
        self.hitbox = pygame.Rect(0, 0, 16, 16)
        self.hitbox.centerx = self.rect.centerx
        self.hitbox.bottom = self.rect.bottom
        
class Tree(Generic):
    def __init__(self, pos, surf, groups, camera_group, name, player_add):
        super().__init__(pos, surf, groups)
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.5, -self.rect.height * 0.75)
        self.hitbox.bottom = self.rect.bottom
        self.camera_group = camera_group
        
        # tree attributes
        self.health = 5
        self.alive = True
        stump_path = f'./graphics/stumps/{"small" if name == "Small" else "large"}.png'
        self.stump_surf = pygame.image.load(stump_path).convert_alpha()
        
        # apples
        self.apples_surf = pygame.image.load('./graphics/fruit/apple.png')
        self.apple_pos = APPLE_POS[name]
        self.apple_sprites = pygame.sprite.Group()
        self.create_fruit()
        
        # player add
        self.player_add = player_add
        
        # sounds
        self.axe_sound = pygame.mixer.Sound('./audio/axe.mp3')
        
    def create_fruit(self):
        for pos in self.apple_pos:
            if randint(0,10) < 2:
                x = self.rect.left + pos[0]
                y = self.rect.top + pos[1]
                Generic(pos=(x, y), 
                        surf=self.apples_surf, 
                        groups=[self.apple_sprites, self.camera_group],
                        z=LAYERS['fruit'])
    
    def destroy_fruit(self):
        for apple in self.apple_sprites.sprites():
            apple.kill()
    
    def damage(self):
        
        # play sound
        self.axe_sound.play()
        
        # damaging the tree
        self.health -= 1
        
        # remove an apple
        if len(self.apple_sprites.sprites()) > 0:
            random_apple = choice(self.apple_sprites.sprites())
            Particle(random_apple.rect.topleft, random_apple.image, self.camera_group, LAYERS['fruit'])
            random_apple.kill()
            
            #give player apple
            self.player_add('apple')
            
    def check_death(self):
        if self.health <= 0:
            self.alive = False
            
            # display death particle
            Particle(self.rect.topleft, self.image, self.camera_group, LAYERS['fruit'], 300)
            
            # display stump
            self.image = self.stump_surf
            self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
            # self.hitbox = self.rect.copy().inflate(0, -self.rect.height * 0.4)
            # self.hitbox.bottom = self.rect.bottom
            
            
            # give player wood
            self.player_add('wood')
    
    def update(self, dt):
        if self.alive:
            self.check_death()
            
class Particle(Generic):
    def __init__(self, pos, surf, groups, z, duration = 200):
        super().__init__(pos, surf, groups, z)
        self.timer = Timer(duration, self.remove_particle)
        self.timer.activate()
        
        # white surface
        mask_surf = pygame.mask.from_surface(self.image)
        new_surf = mask_surf.to_surface()
        new_surf.set_colorkey((0, 0, 0))
        self.image = new_surf
        
    def remove_particle(self):
        self.kill()
    
    def update(self, dt):
        self.timer.update()
        
class Interaction(Generic):
    def __init__(self, pos, size, groups, name):
        surf = pygame.Surface(size)
        super().__init__(pos, surf, groups)
        self.name = name