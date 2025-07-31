# -------------------------
# mini_games/memory.py
# -------------------------
import pygame
import random
import time
import json
import os

ROWS = 3
COLS = 4
CARD_SIZE = (100, 100)
PADDING = 20
BG = (20, 60, 20)
CARD_BACK = (50, 100, 150)
CARD_BORDER = (240, 240, 240)
FONT_SIZE = 32
SCORES_FILE = os.path.join(os.path.dirname(__file__), '..', 'best_scores.json')

class MemoryGame:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, FONT_SIZE)
        values = list(range(1, ROWS*COLS//2 + 1)) * 2
        random.shuffle(values)
        self.cards = []
        for idx, val in enumerate(values):
            row = idx // COLS
            col = idx % COLS
            rect = pygame.Rect(
                PADDING + col*(CARD_SIZE[0]+PADDING),
                PADDING + row*(CARD_SIZE[1]+PADDING),
                CARD_SIZE[0], CARD_SIZE[1]
            )
            self.cards.append({"value": val, "rect": rect, "revealed": False, "matched": False})
        self.first = None
        self.locked = False

    def load_scores(self):
        try:
            with open(SCORES_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def save_scores(self, scores):
        with open(SCORES_FILE, 'w') as f:
            json.dump(scores, f)

    def run(self):
        scores = self.load_scores()
        start = time.time()
        running = True
        clock = pygame.time.Clock()
        pygame.time.set_timer(pygame.USEREVENT, 0)
        while running:
            self.screen.fill(BG)
            for c in self.cards:
                pygame.draw.rect(self.screen, CARD_BORDER, c["rect"], 2)
                if c["revealed"] or c["matched"]:
                    txt = self.font.render(str(c["value"]), True, CARD_BORDER)
                    self.screen.blit(txt, txt.get_rect(center=c["rect"].center))
                else:
                    pygame.draw.rect(self.screen, CARD_BACK, c["rect"])
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.locked:
                    pos = pygame.mouse.get_pos()
                    for c in self.cards:
                        if c["rect"].collidepoint(pos) and not c["matched"]:
                            c["revealed"] = True
                            if not self.first:
                                self.first = c
                            else:
                                self.locked = True
                                self.second = c
                                pygame.time.set_timer(pygame.USEREVENT, 1000)
                elif event.type == pygame.USEREVENT:
                    pygame.time.set_timer(pygame.USEREVENT, 0)
                    if self.first and self.second:
                        if self.first["value"] == self.second["value"]:
                            self.first["matched"] = True
                            self.second["matched"] = True
                        else:
                            self.first["revealed"] = False
                            self.second["revealed"] = False
                    self.first = None
                    self.second = None
                    self.locked = False
            if all(c["matched"] for c in self.cards):
                duration = time.time() - start
                mode_key = "Memory"
                record = scores.get(mode_key)
                if record is None or duration < record:
                    scores[mode_key] = int(duration)
                    self.save_scores(scores)
                txt = self.font.render("Bravo! Temps: %ds" % int(duration), True, CARD_BORDER)
                self.screen.blit(txt, txt.get_rect(center=(320,240)))
                pygame.display.flip()
                pygame.time.wait(2000)
                running = False
            clock.tick(30)
