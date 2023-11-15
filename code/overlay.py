import pygame
from .settings import *

class Overlay:
    def __init__(self, player):
        
        # general setup
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font('./font/LycheeSoda.ttf', 30)
        self.player = player
        
        # imports
        overlay_path = './graphics/overlay/'
        self.tools_surf = {tool: pygame.image.load(f'{overlay_path}{tool}.png').convert_alpha() for tool in player.tools}
        self.seeds_surf = {seed: pygame.image.load(f'{overlay_path}{seed}.png').convert_alpha() for seed in player.seeds}
        
    def display(self):
        
        # tool
        tool_surf = self.tools_surf[self.player.selected_tool]
        tool_rect = tool_surf.get_rect(midbottom = OVERLAY_POSITIONS['tool'])
        self.display_surface.blit(tool_surf, tool_rect)
        
        # seed
        seed_surf = self.seeds_surf[self.player.selected_seed]
        seed_rect = seed_surf.get_rect(midbottom = OVERLAY_POSITIONS['seed'])
        seed_text_surf = self.font.render(f'{self.player.seed_inventory[self.player.selected_seed]}', False, 'Black')
        seed_text_rect = seed_text_surf.get_rect(midbottom = (OVERLAY_POSITIONS['seed'][0] + 20, OVERLAY_POSITIONS['seed'][1] + 10))
        if self.player.seed_inventory[self.player.selected_seed] > 0:
            self.display_surface.blit(seed_surf, seed_rect)
            self.display_surface.blit(seed_text_surf, seed_text_rect)