# -------------------------
# mini_games/high_scores.py
# -------------------------
import pygame
import json
import os

# Couleurs et paramètres
BG = (40, 20, 60)
TEXT_COLOR = (240, 240, 240)
FONT_SIZE = 28
SCORES_FILE = os.path.join(os.path.dirname(__file__), '..', 'best_scores.json')

class HighScores:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, FONT_SIZE)
        # Charge les scores
        try:
            with open(SCORES_FILE, 'r') as f:
                self.scores = json.load(f)
        except Exception:
            self.scores = {}

    def run(self):
        running = True
        while running:
            self.screen.fill(BG)
            title = self.font.render("Meilleurs Scores", True, TEXT_COLOR)
            self.screen.blit(title, title.get_rect(center=(320, 60)))
            # Affiche chaque entrée
            y = 120
            for key, val in self.scores.items():
                line = f"{key}: {val}"
                txt = self.font.render(line, True, TEXT_COLOR)
                self.screen.blit(txt, (50, y))
                y += FONT_SIZE + 10
                if y > 420:
                    break
            info = self.font.render("Press E pour revenir", True, TEXT_COLOR)
            self.screen.blit(info, (200, 450))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key in (pygame.K_e, pygame.K_RETURN):
                    running = False
        # Retour au menu
