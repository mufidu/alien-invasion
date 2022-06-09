class GameStats:
    """Statisktik game"""

    def __init__(self, ai_game):
        """Inisiasi"""
        self.settings = ai_game.settings
        self.reset_stats()

        #Start
        self.game_active = False

        self.high_score = 0
    
    def reset_stats(self):
        """Inisiasi"""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1