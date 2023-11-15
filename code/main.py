import pygame, sys
from .settings import *
from .level import Level

class Game:
	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
		pygame.display.set_caption('Sprout Land')
		self.clock = pygame.time.Clock()
		self.level = Level()
		pygame.mouse.set_visible(False)

	def run(self):
		while True:
			self.level.wheel = 0
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.MOUSEWHEEL:
					self.level.wheel = event.y
  
			dt = self.clock.tick() / 1000
			self.level.run(dt)
			pygame.display.update()
