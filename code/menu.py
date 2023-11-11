import pygame
from settings import *
from timer import Timer

class Menu:
    def __init__(self, player, toggle_menu, toggle_timer):
        
        # setup
        self.wheel = 0
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font('../font/LycheeSoda.ttf', 30)
        self.player = player
        self.toggle_menu = toggle_menu
        self.toggle_timer = toggle_timer
        
        # options
        self.width = 400
        self.space = 10
        self.padding = 8
        self.total_height = 0
        
        # entries
        self.options = list(self.player.item_inventory.keys()) + list(self.player.seed_inventory.keys())
        self.sell_border = len(self.player.item_inventory) - 1
        self.setup()
        
        # movement
        self.index = 0
        self.timer = Timer(150)
        
        # audio
        self.success = pygame.mixer.Sound('../audio/success.wav')
        self.success.set_volume(0.3)
        
    def setup(self):
        
        # create text surfaces
        self.text_surfs = []
        for index, item in enumerate(self.options):
            text_surf = self.font.render(item + (' seeds' if index > self.sell_border else ''),False,'Black')
            self.text_surfs.append(text_surf)
            self.total_height += text_surf.get_height() + (self.padding * 2)
        self.total_height += (len(self.text_surfs) - 1) * self.space
        self.menu_top = SCREEN_HEIGHT / 2 - self.total_height / 2
        self.menu_left = SCREEN_WIDTH / 2 - self.width / 2
        self.main_rect = pygame.Rect(self.menu_left, self.menu_top, self.width, self.total_height)
        
        # sell/buy text surfaces
        self.buy_text = self.font.render('buy', False, 'Black')
        self.sell_text = self.font.render('sell', False, 'Black')
    
    def display_money(self):
        text_surf = self.font.render(f'${self.player.money}', False, 'Black')
        text_rect = text_surf.get_rect(midbottom = (SCREEN_WIDTH / 2, SCREEN_HEIGHT - 40))
        
        pygame.draw.rect(self.display_surface, 'White', text_rect.copy().inflate(20, 10), 0, 6)
        self.display_surface.blit(text_surf, text_rect)
        
    def display_entry(self, text_surf, amount, top, selected):
        
        # background
        bg_rect = pygame.Rect(self.main_rect.left, top, self.width, text_surf.get_height() + self.padding * 2)
        pygame.draw.rect(self.display_surface, 'White', bg_rect, 0, 6)
        
        # text
        text_rect = text_surf.get_rect(midleft = (self.main_rect.left + 20, bg_rect.centery))
        self.display_surface.blit(text_surf, text_rect)
        
        # amount
        amount_surf = self.font.render(f'{amount}', False, 'Black')
        amount_rect = amount_surf.get_rect(midright = (self.main_rect.right - 20, bg_rect.centery))
        self.display_surface.blit(amount_surf, amount_rect)
        
        # selected
        if selected:
            pygame.draw.rect(self.display_surface, 'Black', bg_rect, 4, 4)
            if self.index <= self.sell_border: # sell
                pos_rect = self.sell_text.get_rect(midleft = (self.main_rect.left + 225, bg_rect.centery))
                self.display_surface.blit(self.sell_text, pos_rect)
            else: # buy
                pos_rect = self.buy_text.get_rect(midleft = (self.main_rect.left + 225, bg_rect.centery))
                self.display_surface.blit(self.buy_text, pos_rect)
        
    def input(self):
        keys = pygame.key.get_pressed()
        self.timer.update()
        mouse = pygame.mouse.get_pressed()
        
        if (keys[pygame.K_ESCAPE] or mouse[2]) and not self.toggle_timer.active:
            self.toggle_menu()
        
        if not self.timer.active:
            if keys[pygame.K_UP] or keys[pygame.K_w] or self.wheel > 0:
                self.index -= 1
                self.timer.activate()
            if keys[pygame.K_DOWN] or keys[pygame.K_s] or self.wheel < 0:
                self.index += 1
                self.timer.activate()
            if keys[pygame.K_SPACE] or mouse[0]:
                self.timer.activate()
                
                # get item
                current_item = self.options[self.index]
                
                # sell
                if self.index <= self.sell_border:
                    if self.player.item_inventory[current_item] > 0:
                        self.player.item_inventory[current_item] -= 1
                        self.player.money += SALE_PRICES[current_item]
                        self.success.play()
                        
                #buy
                else:
                    seed_price = PURCHASE_PRICES[current_item]
                    if self.player.money >= seed_price:
                        self.player.money -= seed_price
                        self.player.seed_inventory[current_item] += 1
                        self.success.play()
        
        self.index = self.index % len(self.options)
        
    def update(self):
        self.input()
        self.display_money()
        for index, text_surf in enumerate(self.text_surfs):
            top = self.main_rect.top + index * (text_surf.get_height() + (self.padding * 2) + self.space)
            amount_list = list(self.player.item_inventory.values()) + list(self.player.seed_inventory.values())
            amount = amount_list[index]
            self.display_entry(text_surf, amount, top, index == self.index)
            