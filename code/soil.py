import pygame
from pygame.sprite import AbstractGroup
from settings import *
from support import *
from random import choice
from pytmx.util_pygame import load_pygame

class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['soil']

class WaterTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS['soil water']

class Plant(pygame.sprite.Sprite):
    def __init__(self, plant_type, groups, soil, check_watered):
        super().__init__(groups)
        
        # setup
        self.plant_type = plant_type
        self.frames = import_folder(f'../graphics/fruit/{self.plant_type}')
        self.soil = soil
        
        # plant growth
        self.age = 0
        self.max_age = len(self.frames) - 1
        self.grow_speed = GROW_SPEED[self.plant_type]
        self.harvestable = False
        
        # sprite setup
        self.image = self.frames[self.age]
        self.y_offset = -16 if plant_type == 'corn' else -8
        self.rect = self.image.get_rect(midbottom=self.soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))
        self.z = LAYERS['ground plant']
        self.check_watered = check_watered
        
    def grow(self):
        if self.check_watered(self.rect.center):
            self.age += self.grow_speed
            
            if int(self.age) > 0:
                self.z = LAYERS['main']
                
            if self.age >= self.max_age:
                self.age = self.max_age
                self.harvestable = True
                self.hitbox = self.rect.copy().inflate(-26, -self.rect.height * 0.4)
            
            self.image = self.frames[int(self.age)]
            self.rect = self.image.get_rect(midbottom=self.soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))

class SoilLayer:
    def __init__(self, all_sprites, collision_sprites, raining):
        
        # sprite groups
        self.all_sprites = all_sprites
        self.collision_sprites = collision_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.plant_sprites = pygame.sprite.Group()
        
        # graphics
        self.soil_surfs = import_folder_dict('../graphics/soil')
        self.water_surfs = import_folder('../graphics/soil_water')
        
        # setup
        self.raining = raining
        self.create_soil_grid()
        self.create_hit_rects()
        
        # audio
        self.hoe_sound = pygame.mixer.Sound('../audio/hoe.wav')
        self.hoe_sound.set_volume(0.3)
        
        self.plant_sound = pygame.mixer.Sound('../audio/plant.wav')
        self.plant_sound.set_volume(0.2)
        
    def create_soil_grid(self):
        ground = pygame.image.load('../graphics/world/ground.png')
        h_tiles, v_tiles = ground.get_width() // TILE_SIZE, ground.get_height() // TILE_SIZE
        
        self.grid = [ [[] for col in range(h_tiles)] for row in range(v_tiles) ]
        for x, y, _ in load_pygame('../data/map.tmx').get_layer_by_name('Farmable').tiles():
            self.grid[y][x].append('F')
        
    def create_hit_rects(self):
        self.hit_rects = []
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'F' in cell:
                    x = index_col * TILE_SIZE
                    y = index_row * TILE_SIZE
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    self.hit_rects.append(rect)
                    
    def get_hit(self, point):
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE
                
                if 'F' in self.grid[y][x]:
                    self.grid[y][x].append('X')
                    self.create_soil_tiles()
                    if self.raining:
                        self.water(point)
                        
                    self.hoe_sound.play()

    def create_soil_tiles(self):
        self.soil_sprites.empty()
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell:
                    
                    # tile options
                    left = False if index_col == 0 else 'X' in self.grid[index_row][index_col - 1]
                    right = False if index_col == len(self.grid[index_row]) - 1 else 'X' in self.grid[index_row][index_col + 1]
                    top = False if index_col == 0 else 'X' in self.grid[index_row - 1][index_col]
                    bottom = False if index_col == len(self.grid) - 1 else 'X' in self.grid[index_row + 1][index_col]
                    
                    tile_key = 'o'
                    
                    if (left and right and bottom and top):
                        tile_key = 'x'
                    elif (left and right and bottom):
                        tile_key = 'tm'
                    elif (left and right and top):
                        tile_key = 'bm'
                    elif (left and top and bottom):
                        tile_key = 'rm'
                    elif (right and top and bottom):
                        tile_key = 'lm'
                    elif (left and right):
                        tile_key = 'lr'
                    elif (left and top):
                        tile_key = 'br'
                    elif (left and bottom):
                        tile_key = 'tr'
                    elif (right and top):
                        tile_key = 'bl'
                    elif (right and bottom):
                        tile_key = 'tl'
                    elif (top and bottom):
                        tile_key = 'tb'
                    elif left:
                        tile_key = 'r'
                    elif right:
                        tile_key = 'l'
                    elif top:
                        tile_key = 'b'
                    elif bottom:
                        tile_key = 't'
                    
                    x = index_col * TILE_SIZE
                    y = index_row * TILE_SIZE
                    SoilTile((x,y), self.soil_surfs[tile_key], [self.all_sprites, self.soil_sprites])
                    
    def water(self, point):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(point):
                
                # add an entry to the soil grid
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE
                if 'W' not in self.grid[y][x]:
                    self.grid[y][x].append('W')
                    
                    # create water sprite
                    pos = soil_sprite.rect.topleft
                    surf = choice(self.water_surfs)
                    WaterTile(pos, surf, [self.all_sprites, self.water_sprites])
    
    def water_all(self):
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell and not 'W' in cell:
                    # add an entry to the soil grid
                    self.grid[index_row][index_col].append('W')
                    
                    # create water sprite
                    pos = (index_col * TILE_SIZE, index_row * TILE_SIZE)
                    surf = choice(self.water_surfs)
                    WaterTile(pos, surf, [self.all_sprites, self.water_sprites])
    
    def remove_water(self):
        
        # remove all sprites
        for water in self.water_sprites:
            water.kill()
        
        # remove from grid
        for row in self.grid:
            for cell in row:
                if 'W' in cell:
                    cell.remove('W')
    
    def check_watered(self, point):
        x = point[0] // TILE_SIZE
        y = point[1] // TILE_SIZE
        cell = self.grid[y][x]
        is_watered = 'W' in cell
        return is_watered 
    
    def plant_seed(self, point, seed):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(point):
                
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE
                if 'P' not in self.grid[y][x]:
                    self.grid[y][x].append('P')

                    Plant(seed, [self.all_sprites, self.plant_sprites, self.collision_sprites], soil_sprite, self.check_watered)
                    
                    self.plant_sound.play()
                    return True
        return False
    
    def update_plants(self):
        for plant in self.plant_sprites.sprites():
            plant.grow()