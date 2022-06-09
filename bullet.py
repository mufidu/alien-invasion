import pygame
from pygame.sprite import Sprite

class Bullet(Sprite):
    """A class manage bullet"""
    def __init__(self, ai_game):
        """Buat bullet"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.bullet_color

        #buat bullet di (0,0)
        self.rect = pygame.Rect(0, 0, self.settings.bullet_width, self.settings.bullet_height)
        self.rect.midtop = ai_game.ship.rect.midtop

        #simpan posisi bullet sebagai desimal
        self.y = float(self.rect.y)
    
    def update(self):
        """Move bullet"""
        #update posisi bullet
        self.y -= self.settings.bullet_speed
        #update posisi rect
        self.rect.y = self.y

    def draw_bullet(self):
        """Gambar bullet ke dalam layar"""
        pygame.draw.rect(self.screen, self.color, self.rect)