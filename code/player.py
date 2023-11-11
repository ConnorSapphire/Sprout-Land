import pygame
from settings import *
from support import *
from timer import Timer

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, collision_sprites, tree_sprites, interaction_sprites, soil_layer, toggle_shop):
        super().__init__(group)
        
        # animation and image setup
        self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0
        
        # general setup
        self.wheel = 0
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.z = LAYERS['main']
        
        # movement attributes
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200
        
        # collision
        self.collision_sprites = collision_sprites
        self.hitbox = pygame.Rect(self.rect.x + 62, self.rect.y + 88, 47, 25)
        
        # timers
        self.timers = {
            'tool_use': Timer(600, self.use_tool),
            'tool_switch': Timer(150),
            'seed_use': Timer(200, self.use_seed),
            'seed_switch': Timer(200),
            'interaction': Timer(200),
            'sleep': Timer(1000)
        }
        
        # tools
        self.tools = ['hoe', 'axe', 'water']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]
        
        # seeds
        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]
        
        # inventory
        self.item_inventory = {
            'wood':     0,
            'apple':    0,
            'corn':     0,
            'tomato':   0
        }
        self.seed_inventory = {
            'corn':     5,
            'tomato':   5
        }
        self.money = 0
        
        # interactions
        self.tree_sprites = tree_sprites
        self.interaction = interaction_sprites
        self.sleep = False
        self.soil_layer = soil_layer
        self.toggle_shop = toggle_shop
        
        # audio
        self.watering = pygame.mixer.Sound('../audio/water.mp3')
        self.watering.set_volume(0.2)
        
    def import_assets(self):
        self.animations = {'up':[], 'down':[], 'left':[], 'right':[],
                           'up_idle':[], 'down_idle':[], 'left_idle':[], 'right_idle':[],
                           'up_hoe':[], 'down_hoe':[], 'left_hoe':[], 'right_hoe':[],
                           'up_axe':[], 'down_axe':[], 'left_axe':[], 'right_axe':[],
                           'up_water':[], 'down_water':[], 'left_water':[], 'right_water':[]}
        for animation in self.animations.keys():
            full_path = '../graphics/character/' + animation
            self.animations[animation] = import_folder(full_path)
        
    def animate(self, dt):
        
        # update frame
        frame_rate = 8
        if '_' in self.status:
            frame_rate = 4
        self.frame_index += frame_rate * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0
            
        # update image
        self.image = self.animations[self.status][int(self.frame_index)]
    
    def input(self):
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
                
        if mouse[0] or mouse[2]:
            pygame.mouse.set_visible(False)
            
        if keys[pygame.K_ESCAPE] and not self.timers['interaction'].active:
            pygame.mouse.set_visible(True)
        
        if not (self.timers['tool_use'].active or self.sleep):
            # directions
            # move player up or down
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0
            
            # move player left or right
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.direction.x = -1
                self.status = 'left'
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.direction.x = 1
                self.status = 'right'
            else:
                self.direction.x = 0
                
            # tool use
            if keys[pygame.K_SPACE] or mouse[0]:
                self.timers['tool_use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0 
                
            # change tool
            if (keys[pygame.K_q] or self.wheel < 0) and not self.timers['tool_switch'].active:
                self.timers['tool_switch'].activate()
                self.tool_index += 1
                if self.tool_index >= len(self.tools):
                    self.tool_index = 0
                self.selected_tool = self.tools[self.tool_index]
            elif self.wheel > 0 and not self.timers['tool_switch'].active:
                self.timers['tool_switch'].activate()
                self.tool_index -= 1
                if self.tool_index <= 0:
                    self.tool_index = len(self.tools) - 1
                self.selected_tool = self.tools[self.tool_index]
                
            # seed use
            if keys[pygame.K_LSHIFT] or mouse[2]:
                self.timers['seed_use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0
            
            # change seed
            if keys[pygame.K_e] and not self.timers['seed_switch'].active:
                self.timers['seed_switch'].activate()
                self.seed_index += 1
                if self.seed_index >= len(self.seeds):
                    self.seed_index = 0
                self.selected_seed = self.seeds[self.seed_index]
                
            # interact
            if not self.timers['interaction'].active:
                if keys[pygame.K_RETURN] or mouse[2]:
                    collided_interaction_sprite = pygame.sprite.spritecollide(self, self.interaction, False)
                    if collided_interaction_sprite:
                        self.timers['interaction'].activate()
                        if collided_interaction_sprite[0].name == 'Trader':
                            self.toggle_shop()
                        if collided_interaction_sprite[0].name == 'Bed' and not self.timers['sleep'].active:
                            self.timers['sleep'].activate()
                            self.status = 'left_idle'
                            self.sleep = True
            
    def get_status(self):
        
        # idle
        if self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_idle'
            
        # tool use
        if self.timers['tool_use'].active:
            self.status = self.status.split('_')[0] + '_' + self.selected_tool
            
    def move(self, dt):
        
        # normalising the vector
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
        
        # horizontal movement
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.centerx = self.pos.x
        self.hitbox.centerx = round(self.pos.x)
        self.collision('horizontal')
        
        # vertical movement
        self.pos.y += self.direction.y * self.speed * dt
        self.rect.centery = self.pos.y
        self.hitbox.centery = round(self.pos.y) + PLAYER_HITBOX_OFFSET['vertical']
        self.collision('vertical')
    
    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        if self.direction.x > 0: # moving right
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0: # moving left
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx
                        
                    if direction == 'vertical':
                        if self.direction.y > 0: # moving down
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0: # moving up
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery - PLAYER_HITBOX_OFFSET['vertical']
                        self.pos.y = self.hitbox.centery - PLAYER_HITBOX_OFFSET['vertical']
                        
    def get_target_position(self):
        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]
        
    def use_tool(self):
        if self.selected_tool == 'hoe':
            self.soil_layer.get_hit(self.target_pos)
        
        if self.selected_tool == 'water':
            self.soil_layer.water(self.target_pos)
            
            self.watering.play()
        
        if self.selected_tool == 'axe':
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()
        
    def use_seed(self):
        if self.seed_inventory[self.selected_seed] > 0:
            planted = self.soil_layer.plant_seed(self.target_pos, self.selected_seed)
            self.seed_inventory[self.selected_seed] -= 1 if planted else 0

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def update(self, dt):
        self.input()
        self.get_status()
        self.move(dt)
        self.animate(dt)
        self.update_timers()
        self.get_target_position()
        