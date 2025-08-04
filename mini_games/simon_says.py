import pygame
import random
import time
import json
import os

# Simon Says
BG = (20, 20, 40)
BUTTON_COLORS = [
    (200, 50, 50),   # rouge
    (50, 200, 50),   # vert
    (50, 50, 200),   # bleu
    (200, 200, 50),  # jaune
]
HIGHLIGHT_COLORS = [
    (255, 100, 100),
    (100, 255, 100),
    (100, 100, 255),
    (255, 255, 150),
]
TEXT_COLOR = (240, 240, 240)
FONT_SIZE = 32

SCORES_FILE = os.path.join(os.path.dirname(__file__), '..', 'best_scores.json')

DIFFICULTIES = {
    '1': ('Facile', 0.8),   # délai entre flashs
    '2': ('Moyen', 0.5),
    '3': ('Difficile', 0.3),
}


class SimonSaysGame:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.sequence = []
        self.user_input = []
        self.flash_delay = 0.7
        self.difficulty_name = ''
        self.best_scores = self.load_scores()
        self.round = 0
        self.input_timeout = 5  # secondes sans appui = game over

        # Zones 2x2
        w2 = self.width // 2
        h2 = self.height // 2
        self.button_rects = [
            pygame.Rect(0, 0, w2, h2),
            pygame.Rect(w2, 0, w2, h2),
            pygame.Rect(0, h2, w2, h2),
            pygame.Rect(w2, h2, w2, h2),
        ]

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
            title = self.font.render("Simon Says : Choisis la difficulté", True, TEXT_COLOR)
            self.screen.blit(title, title.get_rect(center=(self.width // 2, 60)))
            for key, (name, delay) in DIFFICULTIES.items():
                txt = self.font.render(f"{key}. {name} (vitesse: {1/delay:.1f})", True, TEXT_COLOR)
                self.screen.blit(txt, (80, 160 + int(key) * 50))
            info = self.font.render("1/2/3 pour choisir, Q pour quitter", True, TEXT_COLOR)
            self.screen.blit(info, (80, self.height - 60))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        return False
                    if event.unicode in DIFFICULTIES:
                        self.difficulty_name, self.flash_delay = DIFFICULTIES[event.unicode]
                        return True
        return False

    def flash_sequence(self):
        for idx in self.sequence:
            # Highlight button
            start = time.time()
            while time.time() - start < self.flash_delay:
                self.screen.fill(BG)
                self.draw_buttons(highlight=idx)
                self.draw_status(f"Round {self.round} - Observe", show_best=True)
                pygame.display.flip()
                pygame.event.pump()
            # gap
            gap_start = time.time()
            while time.time() - gap_start < 0.2:
                self.screen.fill(BG)
                self.draw_buttons()
                self.draw_status(f"Round {self.round} - Observe", show_best=True)
                pygame.display.flip()
                pygame.event.pump()

    def draw_buttons(self, highlight=None, press_idx=None):
        for i, rect in enumerate(self.button_rects):
            color = BUTTON_COLORS[i]
            if i == highlight:
                color = HIGHLIGHT_COLORS[i]
            if press_idx is not None and i == press_idx:
                # brief press effect
                color = HIGHLIGHT_COLORS[i]
            pygame.draw.rect(self.screen, color, rect)
            # border
            pygame.draw.rect(self.screen, (30, 30, 30), rect, 4)

    def draw_status(self, msg, show_best=False):
        info = self.font.render(msg, True, TEXT_COLOR)
        self.screen.blit(info, (10, self.height - 100))
        diff = self.font.render(f"Difficulté: {self.difficulty_name}", True, TEXT_COLOR)
        self.screen.blit(diff, (10, self.height - 70))
        round_txt = self.font.render(f"Round: {self.round}", True, TEXT_COLOR)
        self.screen.blit(round_txt, (10, self.height - 40))
        if show_best:
            key = f"SimonSays_{self.difficulty_name}"
            best = self.best_scores.get(key, 0)
            best_txt = self.font.render(f"Meilleur round: {best}", True, TEXT_COLOR)
            self.screen.blit(best_txt, (self.width - 300, 10))

    def run(self):
        if not self.choose_difficulty():
            return
        pygame.display.set_caption("Simon Says")
        clock = pygame.time.Clock()
        playing = True
        self.sequence = []
        self.round = 0

        while playing:
            self.round += 1
            self.sequence.append(random.randrange(0, 4))
            # montrer la séquence
            self.flash_sequence()
            self.user_input = []
            input_start_time = time.time()
            correct = True

            while len(self.user_input) < len(self.sequence) and correct:
                self.screen.fill(BG)
                self.draw_buttons()
                self.draw_status("Reproduis la séquence", show_best=True)
                pygame.display.flip()

                event = None
                for e in pygame.event.get():
                    event = e
                    if e.type == pygame.QUIT:
                        playing = False
                        correct = False
                    elif e.type == pygame.KEYDOWN and e.key == pygame.K_q:
                        playing = False
                        correct = False
                    elif e.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = pygame.mouse.get_pos()
                        for i, rect in enumerate(self.button_rects):
                            if rect.collidepoint(mx, my):
                                # feedback visuel
                                self.screen.fill(BG)
                                self.draw_buttons(press_idx=i)
                                self.draw_status("Reproduis la séquence", show_best=True)
                                pygame.display.flip()
                                pygame.time.delay(150)
                                self.user_input.append(i)
                                if self.user_input[-1] != self.sequence[len(self.user_input) - 1]:
                                    correct = False
                                input_start_time = time.time()  # reset timeout after input
                # timeout si trop lent
                if time.time() - input_start_time > self.input_timeout:
                    correct = False
                clock.tick(60)

            if not correct:
                # game over
                key = f"SimonSays_{self.difficulty_name}"
                prev = self.best_scores.get(key, 0)
                achieved = self.round - 1
                if achieved > prev:
                    self.best_scores[key] = achieved
                    self.save_scores()
                # écran fin
                self.screen.fill(BG)
                over_txt = self.font.render(f"Game Over! Round atteint: {achieved}", True, TEXT_COLOR)
                best_txt = self.font.render(f"Meilleur (à {self.difficulty_name}): {self.best_scores.get(key)}", True, TEXT_COLOR)
                prompt = self.font.render("Appuie sur Entrée pour revenir", True, TEXT_COLOR)
                self.screen.blit(over_txt, over_txt.get_rect(center=(self.width // 2, self.height // 2 - 30)))
                self.screen.blit(best_txt, best_txt.get_rect(center=(self.width // 2, self.height // 2 + 10)))
                self.screen.blit(prompt, prompt.get_rect(center=(self.width // 2, self.height // 2 + 50)))
                pygame.display.flip()
                waiting = True
                while waiting:
                    for e in pygame.event.get():
                        if e.type == pygame.QUIT:
                            waiting = False
                        elif e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                            waiting = False
                break
            else:
                # succès de round, petit retour visuel
                self.screen.fill(BG)
                self.draw_buttons()
                success_txt = self.font.render("Bien joué !", True, TEXT_COLOR)
                self.screen.blit(success_txt, success_txt.get_rect(center=(self.width // 2, self.height // 2)))
                pygame.display.flip()
                pygame.time.delay(600)
        # fin de la partie
