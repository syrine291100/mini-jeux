import pygame
import random
import time
import json
import os

# Sliding Puzzle (Taquin)
BG = (25, 25, 60)
TILE_COLOR = (100, 180, 255)
EMPTY_COLOR = (30, 30, 60)
TEXT_COLOR = (240, 240, 240)
BORDER_COLOR = (200, 200, 200)
FONT_SIZE = 28
PADDING = 10

SCORES_FILE = os.path.join(os.path.dirname(__file__), '..', 'best_scores.json')

DIFFICULTIES = {
    '1': ('Facile', 3),   # 3x3
    '2': ('Moyen', 4),    # 4x4
    '3': ('Difficile', 5),# 5x5
}


class SlidingPuzzleGame:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.size = 4  # default
        self.board = []
        self.empty = None  # index of empty tile
        self.tile_size = 0
        self.margin_top = 120
        self.start_time = 0
        self.moves = 0
        self.best_scores = self.load_scores()
        self.difficulty_name = ''

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
            title = self.font.render("Taquin : Choisis la difficulté", True, TEXT_COLOR)
            self.screen.blit(title, title.get_rect(center=(self.width // 2, 60)))
            for key, (name, sz) in DIFFICULTIES.items():
                txt = self.font.render(f"{key}. {name} ({sz}x{sz})", True, TEXT_COLOR)
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
                        self.difficulty_name, self.size = DIFFICULTIES[event.unicode]
                        return True
        return False

    def index_to_pos(self, idx):
        row = idx // self.size
        col = idx % self.size
        return row, col

    def pos_to_index(self, row, col):
        return row * self.size + col

    def is_solved(self):
        # last tile is empty
        return self.board == list(range(1, self.size * self.size)) + [0]

    def valid_moves(self):
        row, col = self.index_to_pos(self.empty)
        moves = []
        if row > 0:
            moves.append(self.pos_to_index(row - 1, col))
        if row < self.size - 1:
            moves.append(self.pos_to_index(row + 1, col))
        if col > 0:
            moves.append(self.pos_to_index(row, col - 1))
        if col < self.size - 1:
            moves.append(self.pos_to_index(row, col + 1))
        return moves

    def shuffle(self, steps=1000):
        # start from solved, do random legal moves to guarantee solvability
        self.board = list(range(1, self.size * self.size)) + [0]
        self.empty = len(self.board) - 1
        for _ in range(steps):
            move = random.choice(self.valid_moves())
            self.board[self.empty], self.board[move] = self.board[move], self.board[self.empty]
            self.empty = move

        if self.is_solved():
            # rare, reshuffle
            self.shuffle(steps)

    def draw(self):
        self.screen.fill(BG)
        # Title and stats
        title = self.font.render(f"Taquin {self.difficulty_name} ({self.size}x{self.size})", True, TEXT_COLOR)
        self.screen.blit(title, (20, 10))
        elapsed = int(time.time() - self.start_time)
        timer_txt = self.font.render(f"Temps: {elapsed}s", True, TEXT_COLOR)
        moves_txt = self.font.render(f"Mouvements: {self.moves}", True, TEXT_COLOR)
        best_time_key = f"SlidingPuzzle_{self.size}x{self.size}_time"
        best_moves_key = f"SlidingPuzzle_{self.size}x{self.size}_moves"
        best_time = self.best_scores.get(best_time_key)
        best_moves = self.best_scores.get(best_moves_key)
        best_txt = self.font.render(f"Meilleur temps: {best_time if best_time else '-'}s  /  meilleurs coups: {best_moves if best_moves else '-'}", True, TEXT_COLOR)
        self.screen.blit(timer_txt, (20, 50))
        self.screen.blit(moves_txt, (20, 80))
        self.screen.blit(best_txt, (20, 110))
        # Compute tile layout
        board_area = min(self.width, self.height - self.margin_top) - 2 * PADDING
        self.tile_size = board_area // self.size
        offset_x = (self.width - (self.tile_size * self.size)) // 2
        offset_y = self.margin_top
        # Draw tiles
        for idx, val in enumerate(self.board):
            row, col = self.index_to_pos(idx)
            x = offset_x + col * self.tile_size
            y = offset_y + row * self.tile_size
            rect = pygame.Rect(x + 2, y + 2, self.tile_size - 4, self.tile_size - 4)
            if val == 0:
                pygame.draw.rect(self.screen, EMPTY_COLOR, rect)
            else:
                pygame.draw.rect(self.screen, TILE_COLOR, rect)
                pygame.draw.rect(self.screen, BORDER_COLOR, rect, 2)
                num_txt = self.font.render(str(val), True, TEXT_COLOR)
                self.screen.blit(num_txt, num_txt.get_rect(center=rect.center))
        pygame.display.flip()

    def swap_with_empty(self, idx):
        if idx in self.valid_moves():
            self.board[self.empty], self.board[idx] = self.board[idx], self.board[self.empty]
            self.empty = idx
            self.moves += 1

    def run(self):
        if not self.choose_difficulty():
            return
        self.shuffle(steps=500 + self.size * 200)
        self.start_time = time.time()
        self.moves = 0
        running = True
        clock = pygame.time.Clock()

        while running:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    # arrow keys move tile into empty if adjacent
                    if event.key == pygame.K_UP:
                        # tile below empty moves up
                        erow, ecol = self.index_to_pos(self.empty)
                        target = (erow + 1, ecol)
                        if target[0] < self.size:
                            self.swap_with_empty(self.pos_to_index(*target))
                    elif event.key == pygame.K_DOWN:
                        erow, ecol = self.index_to_pos(self.empty)
                        target = (erow - 1, ecol)
                        if target[0] >= 0:
                            self.swap_with_empty(self.pos_to_index(*target))
                    elif event.key == pygame.K_LEFT:
                        erow, ecol = self.index_to_pos(self.empty)
                        target = (erow, ecol + 1)
                        if target[1] < self.size:
                            self.swap_with_empty(self.pos_to_index(*target))
                    elif event.key == pygame.K_RIGHT:
                        erow, ecol = self.index_to_pos(self.empty)
                        target = (erow, ecol - 1)
                        if target[1] >= 0:
                            self.swap_with_empty(self.pos_to_index(*target))
                    elif event.key == pygame.K_q:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    # compute clicked tile
                    board_area = min(self.width, self.height - self.margin_top) - 2 * PADDING
                    self.tile_size = board_area // self.size
                    offset_x = (self.width - (self.tile_size * self.size)) // 2
                    offset_y = self.margin_top
                    if offset_y <= my <= offset_y + self.tile_size * self.size:
                        col = (mx - offset_x) // self.tile_size
                        row = (my - offset_y) // self.tile_size
                        if 0 <= row < self.size and 0 <= col < self.size:
                            idx = self.pos_to_index(row, col)
                            if idx in self.valid_moves():
                                self.swap_with_empty(idx)

            if self.is_solved():
                elapsed = time.time() - self.start_time
                size_key = f"{self.size}x{self.size}"
                time_key = f"SlidingPuzzle_{size_key}_time"
                moves_key = f"SlidingPuzzle_{size_key}_moves"
                prev_time = self.best_scores.get(time_key)
                prev_moves = self.best_scores.get(moves_key)
                updated = False
                if (prev_time is None) or (elapsed < prev_time):
                    self.best_scores[time_key] = int(elapsed)
                    updated = True
                if (prev_moves is None) or (self.moves < prev_moves):
                    self.best_scores[moves_key] = self.moves
                    updated = True
                if updated:
                    self.save_scores()
                # Victoire écran
                self.screen.fill(BG)
                win_txt = self.font.render("Bravo! Puzzle résolu.", True, TEXT_COLOR)
                stats_txt = self.font.render(f"Temps: {int(elapsed)}s  Mouvements: {self.moves}", True, TEXT_COLOR)
                prompt = self.font.render("Appuie sur Entrée pour revenir", True, TEXT_COLOR)
                self.screen.blit(win_txt, win_txt.get_rect(center=(self.width // 2, self.height // 2 - 30)))
                self.screen.blit(stats_txt, stats_txt.get_rect(center=(self.width // 2, self.height // 2 + 10)))
                self.screen.blit(prompt, prompt.get_rect(center=(self.width // 2, self.height // 2 + 60)))
                pygame.display.flip()
                waiting = True
                while waiting:
                    for e in pygame.event.get():
                        if e.type == pygame.QUIT:
                            waiting = False
                            running = False
                        elif e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                            waiting = False
                            running = False
            clock.tick(60)
