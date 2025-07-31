# -------------------------
# mini_games/guess_number.py
# -------------------------
import pygame
import random
import json
import os

BG = (0, 0, 0)
TEXT = (255, 255, 255)
FEEDBACK = (255, 200, 50)
FONT_SIZE = 32
SCORES_FILE = os.path.join(os.path.dirname(__file__), '..', 'best_scores.json')
DIFFICULTIES = {
    '1': ('Facile', 50),
    '2': ('Moyen', 100),
    '3': ('Difficile', 200)
}

class GuessNumberGame:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.difficulty = None
        self.max_num = 100
        self.target = None
        self.input_text = ""
        self.feedback = ""
        self.attempts = 0
        self.best_scores = self.load_scores()

    def load_scores(self):
        try:
            with open(SCORES_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def save_scores(self):
        with open(SCORES_FILE, 'w') as f:
            json.dump(self.best_scores, f)

    def choose_difficulty(self):
        choosing = True
        while choosing:
            self.screen.fill(BG)
            title = self.font.render("Choisissez difficulté", True, TEXT)
            self.screen.blit(title, title.get_rect(center=(320, 100)))
            for key, (name, _) in DIFFICULTIES.items():
                txt = self.font.render(f"{key}. {name}", True, TEXT)
                self.screen.blit(txt, (200, 180 + int(key)*60))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN and event.unicode in DIFFICULTIES:
                    self.difficulty, self.max_num = DIFFICULTIES[event.unicode]
                    return True
        return False

    def run(self):
        if not self.choose_difficulty():
            return
        self.target = random.randint(1, self.max_num)
        self.attempts = 0
        running = True
        start = time.time()
        clock = pygame.time.Clock()
        while running:
            self.screen.fill(BG)
            prompt = self.font.render(f"Devinez (1-{self.max_num}):", True, TEXT)
            self.screen.blit(prompt, (50, 80))
            user_txt = self.font.render(self.input_text, True, TEXT)
            self.screen.blit(user_txt, (50, 140))
            fb_txt = self.font.render(self.feedback, True, FEEDBACK)
            self.screen.blit(fb_txt, (50, 200))
            # affiche meilleur score
            key = f"Guess_{self.difficulty}"
            best = self.best_scores.get(key)
            if best:
                best_txt = self.font.render(f"Meilleur: {best} coups", True, TEXT)
                self.screen.blit(best_txt, (50, 260))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        try:
                            guess = int(self.input_text)
                            self.attempts += 1
                            if guess < self.target:
                                self.feedback = "Plus haut"
                            elif guess > self.target:
                                self.feedback = "Plus bas"
                            else:
                                duration = time.time() - start
                                self.feedback = f"Gagné en {self.attempts} coups!"
                                prev = self.best_scores.get(key)
                                if prev is None or self.attempts < prev:
                                    self.best_scores[key] = self.attempts
                                    self.save_scores()
                                pygame.display.flip()
                                pygame.time.wait(1000)
                                running = False
                        except ValueError:
                            self.feedback = "Entrée invalide"
                        self.input_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    elif event.unicode.isdigit():
                        self.input_text += event.unicode
            clock.tick(30)