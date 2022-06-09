import sys
from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien

class AlienInvasion:
    """Class Game"""
    def __init__(self):
        """Inisiasi"""
        pygame.init()
        self.settings = Settings()
        """Setting Screen Size untuk Gamenya"""
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")
        
        #stat game dan scoreboard
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        #Tombol Play
        self.play_button = Button(self, "Play")


    def run_game(self):
        """mulai game"""
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self.bullets.update()
                self._update_bullets()
                self._update_aliens()
            
            self._update_screen()
    
    def _check_events(self):
        """Respon ke tombol"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        """Mulai game ketika pemain pencet tombol Play"""
        button_click = self.play_button.rect.collidepoint(mouse_pos)
        if button_click and not self.stats.game_active:
            #Reset stat game
            self.settings.initialize_dynamic_settings()
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()

            #Kosongin alien dan bullets
            self.aliens.empty()
            self.bullets.empty()

            #Buat fleet baru dan tengahin ship
            self._create_fleet()
            self.ship.center_ship()

            #Hide mouse cursor
            pygame.mouse.set_visible(False)

    def _check_keydown_events(self,event):
        """Respon ke tombol yang ditekan"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self,event):
        """Respon ke tombol yang dilepas"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False;
    
    def _fire_bullet(self):
        """Buat bullet baru, tambahkan ke bullet group"""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """Update posisi bullet"""
        self.bullets.update()

        # Hapus bullet kalo udah di luar layar
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                 self.bullets.remove(bullet)
        self._check_bullet_alien_collisions()
    
    def _check_bullet_alien_collisions(self):
        """Respon alien kalo kena tembak"""
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            #Hapus bullet, buat fleet baru
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            #Naikin level
            self.stats.level += 1
            self.sb.prep_level()
    

    def _update_aliens(self):
        """
        Cek kalo possisi alien udah diujung, lalu update posisi alien fleet yang ada.
        """
        self._check_fleet_edges()
        self.aliens.update()

        #Cek apakah ada alien yang menabrak ship
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
            print("Ship hit!!")

        #Cek apakah ada alien yang menabrak bawah layar
        self._check_aliens_bottom()
        
    def _ship_hit(self):
        """Responship yang ditabrak alien"""

        if self.stats.ships_left > 0:
            #Kurangi nyawa, update scoreboard
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            #Hapus sisa alien dan bullet yang ada
            self.aliens.empty()
            self.bullets.empty()

            #Buat fleet baru, tangahin ship
            self._create_fleet()
            self.ship.center_ship()

            #Pause
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _create_fleet(self):
        """
        Buat fleet aliens
        Cari jumlah alien per baris
        Kasih jarak antar alien

        """
        
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2*alien_width)
        number_aliens_x = available_space_x // (2*alien_width)

        
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3*alien_height) - ship_height)
        number_rows = available_space_y // (2*alien_height)
       
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)
    
    def _create_alien(self, alien_number, row_number):
        #Buat alien
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2*alien_width*alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)
    
    def _check_fleet_edges(self):
        """Respon kalo alien nyentuh ujung"""
        for alien in self.aliens.sprites():
            if  alien.check_edges():
                self._change_fleet_direction()
                break
    
    def _change_fleet_direction(self):
        """Turunin fleet"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_screen(self):
        """Update image"""
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)

        #Show score
        self.sb.show_score()

        #Buat play button kalo game lagi inactive
        if not self.stats.game_active:
            self.play_button.draw_button()

        pygame.display.flip()
    
    def _check_aliens_bottom(self):
        """Cek apakah ada alien yang sudah mencapai bagian bawah layar"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                #sama seperti kalau ship terkena alien
                self._ship_hit()
                break

if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()