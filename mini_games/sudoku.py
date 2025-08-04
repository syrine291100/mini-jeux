# mini_games/sudoku.py
import pygame
import random
import time
import json
import os
import copy

# Sudoku avec trois niveaux de difficulté et meilleur temps
BG = (25, 25, 60)
GRID_COLOR = (200, 200, 200)
GIVEN_COLOR = (240, 240, 240)
INPUT_COLOR = (100, 200, 255)
CONFLICT_COLOR = (255, 100, 100)
HIGHLIGHT_COLOR = (80, 80, 140)
TEXT_COLOR = (240, 240, 240)
FONT_SIZE = 28

SCORES_FILE = os.path.join(os.path.dirname(__file__), '..', 'best_scores.json')

DIFFICULTIES = {
    '1': ('Facile', 40),   # nombre de cases données
    '2': ('Moyen', 32),
    '3': ('Difficile', 24),
}


class SudokuGame:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.difficulty_name = ''
        self.givens = [[0] * 9 for _ in range(9)]
        self.grid = [[0] * 9 for _ in range(9)]  # joueur
        self.solution = [[0] * 9 for _ in range(9)]
        self.selected = (0, 0)
        self.start_time = 0
        self.finished = False
        self.best_scores = self.load_scores()

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

    # Génération solution complète par backtracking
    def fill_full(self, board=None):
        if board is None:
            board = [[0] * 9 for _ in range(9)]
        # cherche cellule vide
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    nums = list(range(1, 10))
                    random.shuffle(nums)
                    for n in nums:
                        if self.is_safe(board, i, j, n):
                            board[i][j] = n
                            if self.fill_full(board):
                                return True
                            board[i][j] = 0
                    return False
        return True

    def is_safe(self, board, row, col, val):
        # ligne et colonne
        if any(board[row][c] == val for c in range(9)):
            return False
        if any(board[r][col] == val for r in range(9)):
            return False
        br = (row // 3) * 3
        bc = (col // 3) * 3
        for r in range(br, br + 3):
            for c in range(bc, bc + 3):
                if board[r][c] == val:
                    return False
        return True

    # compte solutions (limite à 2)
    def count_solutions(self, board, limit=2):
        # cherche vide
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    count = 0
                    for n in range(1, 10):
                        if self.is_safe(board, i, j, n):
                            board[i][j] = n
                            cnt = self.count_solutions(board, limit)
                            if cnt:
                                count += cnt
                            board[i][j] = 0
                            if count >= limit:
                                return count
                    return count
        # complet
        return 1

    def dig_holes(self, clues):
        # partir de la solution self.solution et retirer jusqu'à avoir "clues" donnés
        board = copy.deepcopy(self.solution)
        cells = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(cells)
        to_remove = 81 - clues
        for (r, c) in cells:
            if to_remove <= 0:
                break
            backup = board[r][c]
            board[r][c] = 0
            board_copy = copy.deepcopy(board)
            # vérifier unicité
            if self.count_solutions(board_copy, limit=2) == 1:
                to_remove -= 1
            else:
                board[r][c] = backup  # remettre
        self.givens = board
        self.grid = copy.deepcopy(board)

    def choose_difficulty(self):
        choosing = True
        while choosing:
            self.screen.fill(BG)
            title = self.font.render("Sudoku : Choisis la difficulté", True, TEXT_COLOR)
            self.screen.blit(title, title.get_rect(center=(self.width // 2, 60)))
            for key, (name, clues) in DIFFICULTIES.items():
                desc = f"{key}. {name} ({clues} indices donnés)"
                txt = self.font.render(desc, True, TEXT_COLOR)
                self.screen.blit(txt, (80, 150 + int(key) * 50))
            info = self.font.render("1/2/3 pour choisir, R: refaire, Q pour quitter", True, TEXT_COLOR)
            self.screen.blit(info, (40, self.height - 60))
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return False
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_q:
                        return False
                    if e.unicode in DIFFICULTIES:
                        self.difficulty_name, clues = DIFFICULTIES[e.unicode]
                        # générer grille
                        full = [[0] * 9 for _ in range(9)]
                        self.fill_full(full)
                        self.solution = full
                        self.dig_holes(clues)
                        self.start_time = time.time()
                        self.finished = False
                        return True
                    elif e.key == pygame.K_r:
                        return False  # remonter pour relancer si déjà en jeu
        return False

    def draw(self):
        self.screen.fill(BG)
        # titre + timer
        title = self.font.render(f"Sudoku - {self.difficulty_name}", True, TEXT_COLOR)
        self.screen.blit(title, (20, 10))
        if not self.finished:
            elapsed = int(time.time() - self.start_time)
        else:
            elapsed = int(self.end_time - self.start_time)
        timer = self.font.render(f"Temps: {elapsed}s", True, TEXT_COLOR)
        self.screen.blit(timer, (self.width - 180, 10))
        # meilleure
        key = f"Sudoku_{self.difficulty_name}"
        best = self.best_scores.get(key)
        if best:
            best_txt = self.font.render(f"Meilleur: {best}s", True, TEXT_COLOR)
            self.screen.blit(best_txt, (self.width - 180, 40))

        # grille
        grid_origin = (50, 100)
        cell_size = min((self.width - 100) // 9, (self.height - 180) // 9)
        ox, oy = grid_origin

        # surligner sélection
        sr, sc = self.selected
        sel_rect = pygame.Rect(ox + sc * cell_size, oy + sr * cell_size, cell_size, cell_size)
        pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, sel_rect)

        # dessiner lignes épaisses par blocs
        for i in range(10):
            thickness = 3 if i % 3 == 0 else 1
            pygame.draw.line(self.screen, GRID_COLOR,
                             (ox + i * cell_size, oy),
                             (ox + i * cell_size, oy + 9 * cell_size), thickness)
            pygame.draw.line(self.screen, GRID_COLOR,
                             (ox, oy + i * cell_size),
                             (ox + 9 * cell_size, oy + i * cell_size), thickness)

        # dessiner chiffres
        for r in range(9):
            for c in range(9):
                val = self.grid[r][c]
                if val == 0:
                    continue
                x = ox + c * cell_size + cell_size // 2
                y = oy + r * cell_size + cell_size // 2
                is_given = self.givens[r][c] != 0
                color = GIVEN_COLOR if is_given else INPUT_COLOR
                # conflit ?
                if not is_given and val != 0 and not self.is_valid_move(self.grid, r, c, val):
                    color = CONFLICT_COLOR
                txt = self.font.render(str(val), True, color)
                rect = txt.get_rect(center=(x, y))
                self.screen.blit(txt, rect)

        # instructions
        inst = self.font.render("Flèches: déplacer | 1-9: entrer | Effacer: Backspace | Entrée: vérifier | Q: quitter", True, TEXT_COLOR)
        self.screen.blit(inst, (20, self.height - 30))

    def is_valid_move(self, board, row, col, val):
        # Vérifie que la valeur respecte les règles en ignorant la cellule elle-même
        for c in range(9):
            if c != col and board[row][c] == val:
                return False
        for r in range(9):
            if r != row and board[r][col] == val:
                return False
        br = (row // 3) * 3
        bc = (col // 3) * 3
        for r in range(br, br + 3):
            for c in range(bc, bc + 3):
                if (r != row or c != col) and board[r][c] == val:
                    return False
        return True

    def check_complete(self):
        # completude + validité
        for r in range(9):
            for c in range(9):
                v = self.grid[r][c]
                if v == 0 or not self.is_valid_move(self.grid, r, c, v):
                    return False
        return True

    def run(self):
        running = True
        while running:
            if not self.choose_difficulty():
                return
            clock = pygame.time.Clock()
            while running:
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        return
                    elif e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_q:
                            return
                        elif e.key == pygame.K_UP:
                            r, c = self.selected
                            self.selected = ((r - 1) % 9, c)
                        elif e.key == pygame.K_DOWN:
                            r, c = self.selected
                            self.selected = ((r + 1) % 9, c)
                        elif e.key == pygame.K_LEFT:
                            r, c = self.selected
                            self.selected = (r, (c - 1) % 9)
                        elif e.key == pygame.K_RIGHT:
                            r, c = self.selected
                            self.selected = (r, (c + 1) % 9)
                        elif e.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                            r, c = self.selected
                            if self.givens[r][c] == 0:
                                self.grid[r][c] = 0
                        elif e.unicode in '123456789':
                            r, c = self.selected
                            if self.givens[r][c] == 0:
                                self.grid[r][c] = int(e.unicode)
                        elif e.key == pygame.K_RETURN:
                            if self.check_complete():
                                self.finished = True
                                self.end_time = time.time()
                                duration = int(self.end_time - self.start_time)
                                key = f"Sudoku_{self.difficulty_name}"
                                prev = self.best_scores.get(key)
                                if (prev is None) or (duration < prev):
                                    self.best_scores[key] = duration
                                    self.save_scores()
                            else:
                                # petit feedback visuel: rien de spécial, les conflits sont en rouge
                                pass

                if self.finished:
                    # écran de victoire
                    self.draw()
                    win_txt = self.font.render("Bravo ! Tu as résolu le Sudoku.", True, INPUT_COLOR)
                    prompt = self.font.render("Appuie sur Entrée pour continuer", True, TEXT_COLOR)
                    self.screen.blit(win_txt, (self.width // 2 - win_txt.get_width() // 2, 60))
                    self.screen.blit(prompt, (self.width // 2 - prompt.get_width() // 2, 100))
                    pygame.display.flip()
                    for e in pygame.event.get():
                        if e.type == pygame.QUIT:
                            return
                        elif e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                            self.finished = False
                            break
                else:
                    self.draw()
                    pygame.display.flip()
                clock.tick(60)
