import pygame
import random
import time
import json
import os

# mini_games/hangman.py (Pendu)
# Sauvegarde des meilleurs scores dans best_scores.json :
# - Meilleure vie restante (plus c'est haut, mieux c'est)
# - Meilleur temps (le plus court) pour réussir

BG = (25, 25, 50)
TEXT_COLOR = (240, 240, 240)
HIGHLIGHT = (100, 200, 255)
WRONG_COLOR = (220, 100, 100)
CORRECT_COLOR = (100, 255, 100)
FONT_SIZE = 32

SCORES_FILE = os.path.join(os.path.dirname(__file__), '..', 'best_scores.json')

DIFFICULTIES = {
    '1': ('Facile', 4, 5, 8),    # nom, min_len, max_len, vies
    '2': ('Moyen', 6, 7, 6),
    '3': ('Difficile', 8, 20, 5),
}

WORD_POOL = [
    # liste de mots (tu peux étoffer ou charger depuis un fichier)
    "pomme", "chat", "chien", "maison", "ordinateur", "python", "programmation",
    "éléphant", "avion", "bic", "livre", "fenetre", "montagne", "voiture",
    "bouteille", "fleur", "soleil", "lune", "etoile", "ordinateur", "revolution",
    "tortue", "pyramide", "serpent", "galaxie", "musique", "arc-en-ciel"
]

class HangmanGame:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.best_scores = self.load_scores()
        self.difficulty = None
        self.word = ""
        self.masked = []
        self.guessed = set()
        self.wrong = set()
        self.max_lives = 6
        self.remaining = 0
        self.start_time = 0

    def load_scores(self):
        try:
            with open(SCORES_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def save_scores(self):
        try:
            with open(SCORES_FILE, 'w') as f:
                json.dump(self.best_scores, f)
        except Exception:
            pass

    def choose_difficulty(self):
        choosing = True
        while choosing:
            self.screen.fill(BG)
            title = self.font.render("Pendu : Choisis la difficulté", True, TEXT_COLOR)
            self.screen.blit(title, title.get_rect(center=(self.width // 2, 60)))
            for key, (name, mn, mx, lives) in DIFFICULTIES.items():
                desc = f"{key}. {name} ({mn}-{mx} lettres), {lives} vies"
                txt = self.font.render(desc, True, TEXT_COLOR)
                self.screen.blit(txt, (60, 140 + int(key) * 50))
            info = self.font.render("1/2/3 pour choisir, Q pour quitter", True, TEXT_COLOR)
            self.screen.blit(info, (60, self.height - 60))
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return False
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_q:
                        return False
                    if e.unicode in DIFFICULTIES:
                        self.difficulty, minlen, maxlen, lives = DIFFICULTIES[e.unicode]
                        self.max_lives = lives
                        self.remaining = lives
                        self.pick_word(minlen, maxlen)
                        return True
        return False

    def pick_word(self, min_len, max_len):
        candidates = [w.lower() for w in WORD_POOL if min_len <= len(w) <= max_len]
        if not candidates:
            candidates = [w.lower() for w in WORD_POOL]
        self.word = random.choice(candidates)
        self.masked = ['_' if c.isalpha() else c for c in self.word]
        self.guessed = set()
        self.wrong = set()
        self.remaining = self.max_lives
        self.start_time = time.time()

    def update_masked(self, letter):
        updated = False
        for i, c in enumerate(self.word):
            if c == letter:
                self.masked[i] = letter
                updated = True
        return updated

    def draw_hangman(self):
        # dessine une version simplifiée du pendu selon les erreurs
        base_x = self.width - 200
        base_y = 150
        # poteau
        pygame.draw.line(self.screen, TEXT_COLOR, (base_x, base_y), (base_x, base_y + 200), 5)
        pygame.draw.line(self.screen, TEXT_COLOR, (base_x, base_y), (base_x - 100, base_y), 5)
        pygame.draw.line(self.screen, TEXT_COLOR, (base_x - 100, base_y), (base_x - 100, base_y + 30), 5)
        # cordel
        pygame.draw.line(self.screen, TEXT_COLOR, (base_x - 100, base_y + 30), (base_x - 80, base_y + 30), 5)

        errors = self.max_lives - self.remaining
        # tête
        if errors >= 1:
            pygame.draw.circle(self.screen, TEXT_COLOR, (base_x - 80, base_y + 50), 20, 3)
        # corps
        if errors >= 2:
            pygame.draw.line(self.screen, TEXT_COLOR, (base_x - 80, base_y + 70), (base_x - 80, base_y + 120), 3)
        # bras
        if errors >= 3:
            pygame.draw.line(self.screen, TEXT_COLOR, (base_x - 80, base_y + 80), (base_x - 100, base_y + 100), 3)
        if errors >= 4:
            pygame.draw.line(self.screen, TEXT_COLOR, (base_x - 80, base_y + 80), (base_x - 60, base_y + 100), 3)
        # jambes
        if errors >= 5:
            pygame.draw.line(self.screen, TEXT_COLOR, (base_x - 80, base_y + 120), (base_x - 100, base_y + 150), 3)
        if errors >= 6:
            pygame.draw.line(self.screen, TEXT_COLOR, (base_x - 80, base_y + 120), (base_x - 60, base_y + 150), 3)

    def run(self):
        if not self.choose_difficulty():
            return
        running = True
        clock = pygame.time.Clock()
        won = False

        while running:
            self.screen.fill(BG)
            elapsed = int(time.time() - self.start_time)
            # Affichage de l'état
            title = self.font.render(f"Pendu - {self.difficulty}", True, TEXT_COLOR)
            self.screen.blit(title, (20, 20))
            word_txt = self.font.render(" ".join(self.masked), True, HIGHLIGHT)
            self.screen.blit(word_txt, (20, 80))
            info = self.font.render(f"Vies restantes : {self.remaining}", True, TEXT_COLOR)
            self.screen.blit(info, (20, 120))
            guessed_txt = self.font.render(f"Lettres tentées : {' '.join(sorted(self.guessed | self.wrong))}", True, TEXT_COLOR)
            self.screen.blit(guessed_txt, (20, 160))
            time_txt = self.font.render(f"Temps: {elapsed}s", True, TEXT_COLOR)
            self.screen.blit(time_txt, (20, 200))
            self.draw_hangman()

            prompt = self.font.render("Tape une lettre (A-Z), Q pour quitter", True, TEXT_COLOR)
            self.screen.blit(prompt, (20, self.height - 60))

            # Vérifie victoire / défaite
            if '_' not in self.masked:
                won = True
                running = False
            if self.remaining <= 0:
                won = False
                running = False

            pygame.display.flip()

            # Événements
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_q:
                        running = False
                    else:
                        c = e.unicode.lower()
                        if len(c) == 1 and c.isalpha():
                            if c in self.guessed or c in self.wrong:
                                continue
                            if self.update_masked(c):
                                self.guessed.add(c)
                            else:
                                self.wrong.add(c)
                                self.remaining -= 1

            clock.tick(60)

        # Fin de partie : enregistrement
        key_score = f"Hangman_{self.difficulty}_best_lives"
        key_time = f"Hangman_{self.difficulty}_best_time"
        duration = time.time() - self.start_time
        if won:
            prev_lives = self.best_scores.get(key_score, -1)
            if self.remaining > prev_lives:
                self.best_scores[key_score] = self.remaining
            prev_time = self.best_scores.get(key_time)
            if (prev_time is None) or (duration < prev_time):
                self.best_scores[key_time] = round(duration, 1)
            self.save_scores()

        # Écran de fin
        self.screen.fill(BG)
        if won:
            msg = self.font.render(f"Bravo ! Tu as trouvé : {self.word}", True, CORRECT_COLOR)
        else:
            msg = self.font.render(f"Perdu... Le mot était : {self.word}", True, WRONG_COLOR)
        stats = self.font.render(f"Vies restantes: {self.remaining}  Temps: {int(duration)}s", True, TEXT_COLOR)
        best_lives = self.best_scores.get(key_score, '-')
        best_time = self.best_scores.get(key_time, '-')
        best_txt = self.font.render(f"Meilleur vies ({self.difficulty}): {best_lives}  Meilleur temps: {best_time}s", True, TEXT_COLOR)
        prompt2 = self.font.render("Appuie sur Entrée pour revenir", True, TEXT_COLOR)
        self.screen.blit(msg, (self.width//2 - msg.get_width()//2, 120))
        self.screen.blit(stats, (self.width//2 - stats.get_width()//2, 170))
        self.screen.blit(best_txt, (self.width//2 - best_txt.get_width()//2, 220))
        self.screen.blit(prompt2, (self.width//2 - prompt2.get_width()//2, 280))
        pygame.display.flip()

        waiting = True
        while waiting:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    waiting = False
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                    waiting = False
