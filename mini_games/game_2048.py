import pygame
import random
import json
import os
import time

# mini_games/game_2048.py
# Version avec choix de taille (3x3 = facile, 4x4 = standard, 5x5 = difficile)
# Score + meilleur score + meilleure tuile sont sauvegardés dans best_scores.json

# Couleurs
BG = (250, 248, 239)
EMPTY_COLOR = (205, 193, 180)
TILE_COLORS = {
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
}
TEXT_COLOR_DARK = (119, 110, 101)
TEXT_COLOR_LIGHT = (249, 246, 242)

FONT_NAME = None  # default font

SCORES_FILE = os.path.join(os.path.dirname(__file__), '..', 'best_scores.json')


def load_best():
    try:
        with open(SCORES_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}


def save_best(d):
    try:
        with open(SCORES_FILE, 'w') as f:
            json.dump(d, f)
    except Exception:
        pass


class Game2048:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.best_scores = load_best()
        self.font = pygame.font.Font(FONT_NAME, 24)
        self.big_font = pygame.font.Font(FONT_NAME, 48)
        self.reset()

    def choose_size(self):
        choosing = True
        while choosing:
            self.screen.fill(BG)
            title = self.big_font.render("2048 : Choisis la taille", True, TEXT_COLOR_DARK)
            self.screen.blit(title, title.get_rect(center=(self.width // 2, 80)))
            opts = [
                ("1. Facile (3x3)", 3),
                ("2. Standard (4x4)", 4),
                ("3. Difficile (5x5)", 5),
            ]
            for i, (text, _) in enumerate(opts):
                txt = self.font.render(text, True, TEXT_COLOR_DARK)
                self.screen.blit(txt, (self.width // 2 - 120, 160 + i * 50))
            info = self.font.render("1/2/3 pour choisir, Q pour quitter", True, TEXT_COLOR_DARK)
            self.screen.blit(info, (self.width // 2 - info.get_width() // 2, self.height - 60))
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return False
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_q:
                        return False
                    if e.unicode == '1':
                        self.size = 3
                        return True
                    if e.unicode == '2':
                        self.size = 4
                        return True
                    if e.unicode == '3':
                        self.size = 5
                        return True
        return False

    def reset(self):
        self.grid = []
        self.size = 4
        self.score = 0
        self.start_time = time.time()
        self.game_over = False
        self.win = False
        self.prev_board = None
        self.prev_score = 0
        # chosen later
        if hasattr(self, 'size'):
            sz = self.size
        else:
            sz = 4
        self.grid = [[0] * sz for _ in range(sz)]
        self.add_random()
        self.add_random()

    def rotate_left(self, mat):
        return [list(row) for row in zip(*mat[::-1])]

    def rotate_right(self, mat):
        return [list(row) for row in zip(*mat)][::-1]

    def move_row_left(self, row):
        """Compress and merge a single row to the left. Returns new row and points gained."""
        new = [v for v in row if v != 0]
        score_gain = 0
        i = 0
        while i < len(new) - 1:
            if new[i] == new[i + 1]:
                new[i] *= 2
                score_gain += new[i]
                new[i + 1] = 0
                i += 2
            else:
                i += 1
        new = [v for v in new if v != 0]
        new += [0] * (len(row) - len(new))
        return new, score_gain

    def move(self, direction):
        if self.game_over:
            return
        moved = False
        gain = 0
        board = [row[:] for row in self.grid]
        if direction == 'left':
            new_board = []
            for row in self.grid:
                new_row, s = self.move_row_left(row)
                new_board.append(new_row)
                gain += s
        elif direction == 'right':
            new_board = []
            for row in self.grid:
                reversed_row = row[::-1]
                moved_row, s = self.move_row_left(reversed_row)
                moved_row = moved_row[::-1]
                new_board.append(moved_row)
                gain += s
        elif direction == 'up':
            transposed = list(map(list, zip(*self.grid)))
            new_t = []
            for row in transposed:
                new_row, s = self.move_row_left(row)
                new_t.append(new_row)
                gain += s
            new_board = [list(row) for row in zip(*new_t)]
        elif direction == 'down':
            transposed = list(map(list, zip(*self.grid)))
            new_t = []
            for row in transposed:
                reversed_row = row[::-1]
                moved_row, s = self.move_row_left(reversed_row)
                moved_row = moved_row[::-1]
                new_t.append(moved_row)
                gain += s
            new_board = [list(row) for row in zip(*new_t)]
        else:
            return

        if new_board != self.grid:
            moved = True
        if moved:
            self.prev_board = [row[:] for row in self.grid]
            self.prev_score = self.score
            self.grid = new_board
            self.score += gain
            self.add_random()
            self.check_win()
            if not self.can_move():
                self.game_over = True
            self.update_best()

    def add_random(self):
        empties = [(r, c) for r in range(self.size) for c in range(self.size) if self.grid[r][c] == 0]
        if not empties:
            return
        r, c = random.choice(empties)
        self.grid[r][c] = 4 if random.random() < 0.1 else 2

    def can_move(self):
        # any zero?
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == 0:
                    return True
        # check neighbors
        for r in range(self.size):
            for c in range(self.size - 1):
                if self.grid[r][c] == self.grid[r][c + 1]:
                    return True
        for c in range(self.size):
            for r in range(self.size - 1):
                if self.grid[r][c] == self.grid[r + 1][c]:
                    return True
        return False

    def check_win(self):
        target = 2048 if self.size == 4 else (1024 if self.size == 3 else 4096)
        for row in self.grid:
            if any(v >= target for v in row):
                self.win = True

    def update_best(self):
        key_score = f"2048_{self.size}_best_score"
        key_tile = f"2048_{self.size}_best_tile"
        prev_score = self.best_scores.get(key_score, 0)
        if self.score > prev_score:
            self.best_scores[key_score] = self.score
        max_tile = max([v for row in self.grid for v in row])
        prev_tile = self.best_scores.get(key_tile, 0)
        if max_tile > prev_tile:
            self.best_scores[key_tile] = max_tile
        save_best(self.best_scores)

    def draw(self):
        self.screen.fill(BG)
        margin = 40
        board_size = min(self.width, self.height) - 2 * margin
        tile_size = board_size // self.size
        offset_x = (self.width - (tile_size * self.size)) // 2
        offset_y = 120

        # Title and scores
        title = self.big_font.render("2048", True, TEXT_COLOR_DARK)
        self.screen.blit(title, (20, 10))
        score_txt = self.font.render(f"Score: {self.score}", True, TEXT_COLOR_DARK)
        self.screen.blit(score_txt, (20, 70))
        best_key = f"2048_{self.size}_best_score"
        best_score = self.best_scores.get(best_key, 0)
        best_txt = self.font.render(f"Meilleur score: {best_score}", True, TEXT_COLOR_DARK)
        self.screen.blit(best_txt, (220, 70))
        best_tile_key = f"2048_{self.size}_best_tile"
        best_tile = self.best_scores.get(best_tile_key, 0)
        best_tile_txt = self.font.render(f"Meilleure tuile: {best_tile}", True, TEXT_COLOR_DARK)
        self.screen.blit(best_tile_txt, (20, 100))

        # Instructions
        inst = self.font.render("Flèches: déplacer | R: recommencer | Q: quitter", True, TEXT_COLOR_DARK)
        self.screen.blit(inst, (20, self.height - 40))

        # Draw grid background
        for r in range(self.size):
            for c in range(self.size):
                rect = pygame.Rect(offset_x + c * tile_size, offset_y + r * tile_size, tile_size - 5, tile_size - 5)
                value = self.grid[r][c]
                color = TILE_COLORS.get(value, (60, 58, 50)) if value != 0 else EMPTY_COLOR
                pygame.draw.rect(self.screen, color, rect, border_radius=8)
                if value != 0:
                    text_color = TEXT_COLOR_DARK if value <= 4 else TEXT_COLOR_LIGHT
                    txt = self.big_font.render(str(value), True, text_color)
                    txt_rect = txt.get_rect(center=rect.center)
                    # shrink if too big
                    if txt_rect.width > rect.width - 10:
                        scaled = pygame.transform.smoothscale(txt, (rect.width - 20, rect.height - 20))
                        scaled_rect = scaled.get_rect(center=rect.center)
                        self.screen.blit(scaled, scaled_rect)
                    else:
                        self.screen.blit(txt, txt_rect)

        # Game over / win overlay
        if self.game_over or self.win:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 180))
            self.screen.blit(overlay, (0, 0))
            msg = "Tu as gagné !" if self.win else "Game Over"
            sub = "Continue ou R pour recommencer" if self.win else "R pour recommencer"
            msg_txt = self.big_font.render(msg, True, (100, 100, 100))
            sub_txt = self.font.render(sub, True, (80, 80, 80))
            self.screen.blit(msg_txt, msg_txt.get_rect(center=(self.width // 2, self.height // 2 - 20)))
            self.screen.blit(sub_txt, sub_txt.get_rect(center=(self.width // 2, self.height // 2 + 30)))

        pygame.display.flip()

    def run(self):
        if not self.choose_size():
            return
        self.reset()
        clock = pygame.time.Clock()
        while True:
            self.draw()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_q:
                        return
                    if e.key == pygame.K_r:
                        self.reset()
                    if not (self.game_over or self.win):
                        if e.key == pygame.K_LEFT:
                            self.move('left')
                        elif e.key == pygame.K_RIGHT:
                            self.move('right')
                        elif e.key == pygame.K_UP:
                            self.move('up')
                        elif e.key == pygame.K_DOWN:
                            self.move('down')
                    else:
                        # si gagné, tu peux continuer (pas de blocage) ou reset
                        if self.win and e.key == pygame.K_RETURN:
                            self.win = False  # continuer la partie
            clock.tick(60)
