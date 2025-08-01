import pygame
import random
import time

# Couleurs et paramètres
BG = (25, 25, 60)
LINE_COLOR = (200, 200, 200)
X_COLOR = (200, 80, 80)
O_COLOR = (80, 200, 200)
TEXT_COLOR = (240, 240, 240)
FONT_SIZE = 32
BOARD_SIZE = 3
CELL_SIZE = 140
PADDING = 20
WINDOW_SIZE = BOARD_SIZE * CELL_SIZE + PADDING * 2

DIFFICULTIES = {
    '1': 'Facile',
    '2': 'Moyen',
    '3': 'Difficile'
}


class TicTacToeGame:
    def __init__(self, screen):
        self.screen = screen
        self.width = WINDOW_SIZE
        self.height = WINDOW_SIZE + 80  # espace pour texte
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current = 'X'  # X commence
        self.mode = None  # '2joueurs' ou 'solo'
        self.difficulty = None  # nom de difficulté
        self.ai_symbol = 'O'
        self.human_symbol = 'X'

    def draw_board(self):
        self.screen.fill(BG)
        # Dessiner les lignes
        for i in range(1, BOARD_SIZE):
            # verticales
            x = PADDING + i * CELL_SIZE
            pygame.draw.line(self.screen, LINE_COLOR, (x, PADDING), (x, PADDING + BOARD_SIZE * CELL_SIZE), 4)
            # horizontales
            y = PADDING + i * CELL_SIZE
            pygame.draw.line(self.screen, LINE_COLOR, (PADDING, y), (PADDING + BOARD_SIZE * CELL_SIZE, y), 4)

        # Dessiner X et O
        for row in range(3):
            for col in range(3):
                val = self.board[row][col]
                center_x = PADDING + col * CELL_SIZE + CELL_SIZE // 2
                center_y = PADDING + row * CELL_SIZE + CELL_SIZE // 2
                if val == 'X':
                    # deux lignes croisées
                    offset = CELL_SIZE // 3
                    pygame.draw.line(self.screen, X_COLOR,
                                     (center_x - offset, center_y - offset),
                                     (center_x + offset, center_y + offset), 8)
                    pygame.draw.line(self.screen, X_COLOR,
                                     (center_x + offset, center_y - offset),
                                     (center_x - offset, center_y + offset), 8)
                elif val == 'O':
                    pygame.draw.circle(self.screen, O_COLOR, (center_x, center_y), CELL_SIZE // 3, 8)

    def check_winner(self):
        b = self.board
        lines = []

        # lignes et colonnes
        for i in range(3):
            lines.append(b[i][0] + b[i][1] + b[i][2])  # ligne
            lines.append(b[0][i] + b[1][i] + b[2][i])  # colonne

        # diagonales
        lines.append(b[0][0] + b[1][1] + b[2][2])
        lines.append(b[0][2] + b[1][1] + b[2][0])

        for line in lines:
            if line == 'XXX':
                return 'X'
            if line == 'OOO':
                return 'O'

        # égalité
        if all(b[r][c] != '' for r in range(3) for c in range(3)):
            return 'Draw'
        return None

    def minimax(self, board, depth, is_maximizing):
        winner = self._evaluate_board(board)
        if winner is not None:
            return winner

        if is_maximizing:
            best = -float('inf')
            for r in range(3):
                for c in range(3):
                    if board[r][c] == '':
                        board[r][c] = self.ai_symbol
                        score = self.minimax(board, depth + 1, False)
                        board[r][c] = ''
                        best = max(best, score)
            return best
        else:
            best = float('inf')
            for r in range(3):
                for c in range(3):
                    if board[r][c] == '':
                        board[r][c] = self.human_symbol
                        score = self.minimax(board, depth + 1, True)
                        board[r][c] = ''
                        best = min(best, score)
            return best

    def _evaluate_board(self, board):
        # retour: +1 si AI gagne, -1 si humain gagne, 0 si draw ou pas fini
        lines = []
        for i in range(3):
            lines.append(board[i][0] + board[i][1] + board[i][2])
            lines.append(board[0][i] + board[1][i] + board[2][i])
        lines.append(board[0][0] + board[1][1] + board[2][2])
        lines.append(board[0][2] + board[1][1] + board[2][0])

        for line in lines:
            if line == self.ai_symbol * 3:
                return 1
            if line == self.human_symbol * 3:
                return -1

        # draw?
        if all(board[r][c] != '' for r in range(3) for c in range(3)):
            return 0
        return None  # pas fini

    def ai_move(self):
        if self.difficulty == 'Facile':
            choices = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == '']
            return random.choice(choices) if choices else None

        elif self.difficulty == 'Moyen':
            # gagner si possible
            for r in range(3):
                for c in range(3):
                    if self.board[r][c] == '':
                        self.board[r][c] = self.ai_symbol
                        if self.check_winner() == self.ai_symbol:
                            self.board[r][c] = ''
                            return (r, c)
                        self.board[r][c] = ''
            # bloquer l'humain
            for r in range(3):
                for c in range(3):
                    if self.board[r][c] == '':
                        self.board[r][c] = self.human_symbol
                        if self.check_winner() == self.human_symbol:
                            self.board[r][c] = ''
                            return (r, c)
                        self.board[r][c] = ''
            # sinon aléatoire
            return self.ai_move_easy_fallback()

        else:  # Difficile
            best_score = -float('inf')
            best_move = None
            for r in range(3):
                for c in range(3):
                    if self.board[r][c] == '':
                        self.board[r][c] = self.ai_symbol
                        score = self.minimax(self.board, 0, False)
                        self.board[r][c] = ''
                        if score is None:
                            continue
                        if score > best_score:
                            best_score = score
                            best_move = (r, c)
            return best_move if best_move else self.ai_move_easy_fallback()

    def ai_move_easy_fallback(self):
        # fallback aléatoire
        choices = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == '']
        return random.choice(choices) if choices else None

    def choose_mode_and_difficulty(self):
        choosing = True
        while choosing:
            self.screen.fill(BG)
            title = self.font.render("Morpion : mode", True, TEXT_COLOR)
            self.screen.blit(title, title.get_rect(center=(self.width // 2, 60)))
            m1 = self.font.render("1. 2 Joueurs", True, TEXT_COLOR)
            m2 = self.font.render("2. Solo contre IA", True, TEXT_COLOR)
            self.screen.blit(m1, (100, 140))
            self.screen.blit(m2, (100, 190))
            info = self.font.render("1/2 pour choisir, Q pour quitter", True, TEXT_COLOR)
            self.screen.blit(info, (80, self.height - 60))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        return False
                    if event.unicode == '1':
                        self.mode = '2joueurs'
                        return True
                    elif event.unicode == '2':
                        self.mode = 'solo'
                        # choisir difficulté
                        return self.choose_difficulty()
        return False

    def choose_difficulty(self):
        choosing = True
        while choosing:
            self.screen.fill(BG)
            title = self.font.render("Choisis la difficulté IA", True, TEXT_COLOR)
            self.screen.blit(title, title.get_rect(center=(self.width // 2, 60)))
            for key, name in DIFFICULTIES.items():
                txt = self.font.render(f"{key}. {name}", True, TEXT_COLOR)
                self.screen.blit(txt, (120, 160 + int(key) * 50))
            info = self.font.render("1/2/3 pour choisir, Q pour revenir", True, TEXT_COLOR)
            self.screen.blit(info, (80, self.height - 60))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        return False
                    if event.unicode in DIFFICULTIES:
                        self.difficulty = DIFFICULTIES[event.unicode]
                        return True
        return False

    def run(self):
        # redimensionne l'écran si besoin
        self.screen = pygame.display.set_mode((self.width, self.height))
        if not self.choose_mode_and_difficulty():
            return

        # initialisation
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current = 'X'
        running = True
        clock = pygame.time.Clock()

        while running:
            self.draw_board()
            # info
            turn_txt = f"Tour: {self.current}" if self.mode == '2joueurs' or self.current == self.human_symbol else "IA joue..."
            info1 = self.font.render(turn_txt, True, TEXT_COLOR)
            self.screen.blit(info1, (10, self.height - 70))
            if self.mode == 'solo':
                diff_txt = self.font.render(f"Difficulté: {self.difficulty}", True, TEXT_COLOR)
                self.screen.blit(diff_txt, (10, self.height - 40))
            pygame.display.flip()

            winner = self.check_winner()
            if winner:
                # fin de partie
                if winner == 'Draw':
                    result_msg = "Égalité!"
                else:
                    result_msg = f"{winner} a gagné!"
                self.screen.fill(BG)
                self.draw_board()
                end_txt = self.font.render(result_msg, True, TEXT_COLOR)
                prompt = self.font.render("Appuie sur Entrée pour revenir", True, TEXT_COLOR)
                self.screen.blit(end_txt, end_txt.get_rect(center=(self.width // 2, self.height // 2 - 20)))
                self.screen.blit(prompt, prompt.get_rect(center=(self.width // 2, self.height // 2 + 30)))
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
                break

            if self.mode == 'solo' and self.current == self.ai_symbol:
                # tour de l'IA
                move = self.ai_move()
                if move:
                    r, c = move
                    self.board[r][c] = self.ai_symbol
                    self.current = self.human_symbol
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN and self.current != self.ai_symbol:
                        mx, my = pygame.mouse.get_pos()
                        # clique sur une case
                        col = (mx - PADDING) // CELL_SIZE
                        row = (my - PADDING) // CELL_SIZE
                        if 0 <= row < 3 and 0 <= col < 3 and self.board[row][col] == '':
                            self.board[row][col] = self.current
                            self.current = 'O' if self.current == 'X' else 'X'

            # Si mode solo et c'est au tour IA, small délai pour lisibilité
            if self.mode == 'solo' and self.current == self.ai_symbol:
                pygame.time.delay(200)

            clock.tick(60)
