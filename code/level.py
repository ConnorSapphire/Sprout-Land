import pygame 
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Barrier, VerticalBarrier, HorizontalBarrier, Water, WildFlower, Tree, Interaction, Particle
from support import *
from transition import Transition
from soil import SoilLayer
from sky import Rain, Sky
from menu import Menu
from pytmx.util_pygame import load_pygame
from random import randint

class Level:
	def __init__(self):

		# get the display surface
		self.display_surface = pygame.display.get_surface()

		# sprite groups
		self.all_sprites = CameraGroup()
		self.collision_sprites = CameraGroup()
		self.tree_sprites = pygame.sprite.Group()
		self.interaction_sprites = pygame.sprite.Group()
		
  		# sky
		self.rain = Rain(self.all_sprites)
		self.raining = randint(0,10) > 7
		self.sky = Sky()
  
		# setup everything
		self.wheel = 0
		self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites, self.raining)
		self.setup()
		self.overlay = Overlay(self.player)
		self.transition = Transition(self.reset, self.player)
  
		# shop
		self.shop_active = False
		self.menu = Menu(self.player, self.toggle_shop, self.player.timers['interaction'])
  
		# audio
		self.success = pygame.mixer.Sound('../audio/success.wav')
		self.success.set_volume(0.3)
  
		self.music = pygame.mixer.Sound('../audio/music.mp3')
		self.music.set_volume(0.3)
		self.music.play(loops=-1)
  
	def setup(self):
		tmx_data = load_pygame('../data/map.tmx')
  
		# house
		# bottom
		for layer in ['HouseFloor', 'HouseFurnitureBottom']:
			for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
				Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])
		# main
		for layer in ['HouseWalls', 'HouseFurnitureTop']:
			for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
				Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites)
    
		# fence 
		for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
			Generic((x * TILE_SIZE, y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprites])
   
		# water
		water_frames = import_folder('../graphics/water')
		for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
			Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites)

		# wild flower
		for obj in tmx_data.get_layer_by_name('Decoration'):
			WildFlower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])
	
		# trees
		for obj in tmx_data.get_layer_by_name('Trees'):
			Tree(pos=(obj.x, obj.y),
        surf=obj.image,groups=[self.all_sprites, self.collision_sprites, self.tree_sprites],
        camera_group=self.all_sprites,
        name=obj.name,
        player_add=self.player_add)
  
		# ground
		Generic(
			pos = (0,0),
			surf = pygame.image.load('../graphics/world/ground.png').convert_alpha(),
			groups = self.all_sprites,
			z = LAYERS['ground']
		)

		# collision tiles
		for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
			Barrier((x * TILE_SIZE, y * TILE_SIZE), surf, self.collision_sprites)
		for x, y, surf in tmx_data.get_layer_by_name('CollisionVertical').tiles():
			VerticalBarrier((x * TILE_SIZE, y * TILE_SIZE), surf, self.collision_sprites)
		for x, y, surf in tmx_data.get_layer_by_name('CollisionVerticalLeft').tiles():
			VerticalBarrier((x * TILE_SIZE, y * TILE_SIZE), surf, self.collision_sprites, alignment='right')
		for x, y, surf in tmx_data.get_layer_by_name('CollisionVerticalRight').tiles():
			VerticalBarrier((x * TILE_SIZE, y * TILE_SIZE), surf, self.collision_sprites, alignment='left')
		for x, y, surf in tmx_data.get_layer_by_name('CollisionHorizontal').tiles():
			HorizontalBarrier((x * TILE_SIZE, y * TILE_SIZE), surf, self.collision_sprites)
		for x, y, surf in tmx_data.get_layer_by_name('CollisionHorizontalLeft').tiles():
			HorizontalBarrier((x * TILE_SIZE, y * TILE_SIZE), surf, self.collision_sprites, alignment='right')
		for x, y, surf in tmx_data.get_layer_by_name('CollisionHorizontalRight').tiles():
			HorizontalBarrier((x * TILE_SIZE, y * TILE_SIZE), surf, self.collision_sprites, alignment='left')

		# player
		for obj in tmx_data.get_layer_by_name('Player'):
			if obj.name == 'Start':
				self.player = Player(pos=(obj.x,obj.y),
                         group=self.all_sprites,
                         collision_sprites=self.collision_sprites,
                         tree_sprites=self.tree_sprites,
                         interaction_sprites=self.interaction_sprites,
                         soil_layer=self.soil_layer,
                         toggle_shop=self.toggle_shop)
    
			if obj.name == 'Bed':
				Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)
    
			if obj.name == 'Trader':
				Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)

	def player_add(self, item):   
		self.player.item_inventory[item] += 1
  
		self.success.play()

	def plant_collision(self):
		if self.soil_layer.plant_sprites:
			for plant in self.soil_layer.plant_sprites.sprites():
				if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
					self.player_add(plant.plant_type)
					Particle(plant.rect.topleft, plant.image, self.all_sprites, LAYERS['main'])
					row = plant.rect.centery // TILE_SIZE
					col = plant.rect.centerx // TILE_SIZE
					self.soil_layer.grid[row][col].remove('P')
					plant.kill()
	
	def toggle_shop(self):
		self.shop_active = not self.shop_active
		self.player.timers['interaction'].activate()
  
	def update_wheel(self):
		self.player.wheel = self.wheel
		self.menu.wheel = self.wheel
    
	def reset(self):
		# plants
		self.soil_layer.update_plants()
		
		# watered soil
		self.soil_layer.remove_water()
  
		# randomise rain
		self.raining = randint(0,10) > 7
		self.soil_layer.raining = self.raining
		if self.raining:
			self.soil_layer.water_all()
   
		# sky
		self.sky.reset()
     
		# apples on trees
		for tree in self.tree_sprites.sprites():
			tree.destroy_fruit()
			tree.create_fruit()
   
		# player direction
		self.player.status = 'down_idle'

	def run(self,dt):
		
		# drawing logic
		self.display_surface.fill('black')
		self.all_sprites.custom_draw(self.player)
		# self.all_sprites.draw_analytics(self.player)
		# self.collision_sprites.draw_analytics(self.player)
  
		# updates
		if self.shop_active:
			self.menu.update()
			self.player.timers['interaction'].update()
		else:
			# game updates
			self.all_sprites.update(dt)
			self.plant_collision()

			# weather
			if self.raining:
				self.rain.update(dt)
			self.sky.display(dt)
		self.update_wheel()
		
		# transition and overlay
		self.overlay.display()
		if self.player.sleep:
			self.transition.play()
  
class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()
        
    def custom_draw(self, player):
        # calculate offset
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2
        
        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key = lambda sprite: sprite.hitbox.bottom if sprite == player else sprite.rect.bottom):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)
    
    def draw_analytics(self, player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2
        
        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key = lambda sprite: sprite.hitbox.bottom if sprite == player else sprite.rect.bottom):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    
                    # analytics
                    if sprite == player:
                        pygame.draw.rect(self.display_surface, 'red', offset_rect, 5)
                        hitbox_rect = player.hitbox.copy()
                        hitbox_rect.center -= self.offset
                        pygame.draw.rect(self.display_surface, 'green', hitbox_rect, 5)
                        target_pos = offset_rect.center + PLAYER_TOOL_OFFSET[player.status.split('_')[0]]
                        pygame.draw.circle(self.display_surface, 'blue', target_pos, 5)
                    
                    else:
                        pygame.draw.rect(self.display_surface, 'purple', offset_rect, 5)
                        if hasattr(sprite, 'hitbox'):
                            hitbox_rect = sprite.hitbox.copy()
                            hitbox_rect.center -= self.offset
                            pygame.draw.rect(self.display_surface, 'pink', hitbox_rect, 5)