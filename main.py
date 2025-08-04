# Structure du projet :
# jeux/
# ├── .venv/
# ├── main.py
# ├── best_scores.json       # Stocke les meilleurs scores/temps pour tous les jeux
# ├── mini_games/
# │   ├── __init__.py
# │   ├── pong.py
# │   ├── guess_number.py
# │   ├── memory.py
# │   └── high_scores.py     # Affichage des meilleurs scores
# └── .gitignore

# -------------------------
# main.py
# -------------------------
import pygame
import sys
from mini_games.pong import PongGame
from mini_games.guess_number import GuessNumberGame
from mini_games.memory import MemoryGame
from mini_games.high_scores import HighScores
from mini_games.snake import SnakeGame
from mini_games.tic_tac_toe import TicTacToeGame
from mini_games.breakout import BreakoutGame
from mini_games.whack_a_mole import WhackAMoleGame
from mini_games.sliding_puzzle import SlidingPuzzleGame
from mini_games.simon_says import SimonSaysGame
from mini_games.reaction_timer import ReactionTimerGame
from mini_games.math_quiz import MathQuizGame
from mini_games.pendu import PenduGame
from mini_games.sudoku import SudokuGame



# Couleurs et paramètres du menu
BG_COLOR = (30, 30, 60)
HIGHLIGHT = (100, 200, 255)
TEXT_COLOR = (240, 240, 240)
FONT_SIZE = 36

MENU_OPTIONS = [
    ("Pong", PongGame),
    ("Snake", SnakeGame),
    ("Casse-briques", BreakoutGame),
    ("Morpion", TicTacToeGame),
    ("Devinez le nombre", GuessNumberGame),
    ("Jeu de mémoire", MemoryGame),
    ("Taquin", SlidingPuzzleGame),
    ("La taupe", WhackAMole),
    ("Simon Says", SimonSaysGame),
    ("Reaction Timer", ReactionTimerGame),
    ("Math Quiz", MathQuizGame),
    ("Pendu", Pendu),
    ("Sudoku", Sudoku),
    ("Meilleurs scores", HighScores)
    
]


def draw_menu(screen, font, selected_index):
    screen.fill(BG_COLOR)
    title = font.render("Collection de Mini-Jeux", True, TEXT_COLOR)
    screen.blit(title, title.get_rect(center=(320, 80)))
    for idx, (name, _) in enumerate(MENU_OPTIONS):
        color = HIGHLIGHT if idx == selected_index else TEXT_COLOR
        text = font.render(name, True, color)
        x = 320 - text.get_width() // 2
        y = 180 + idx * (FONT_SIZE + 20)
        screen.blit(text, (x, y))
    info = font.render("Q: Quitter | ↑↓: Naviguer | Entrée: Valider", True, TEXT_COLOR)
    screen.blit(info, info.get_rect(center=(320, 450)))
    pygame.display.flip()


def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Collection de Mini-Jeux")
    font = pygame.font.Font(None, FONT_SIZE)
    selected = 0

    while True:
        draw_menu(screen, font, selected)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(MENU_OPTIONS)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(MENU_OPTIONS)
                elif event.key == pygame.K_RETURN:
                    # Lance le mini-jeu ou l'affichage
                    MENU_OPTIONS[selected][1](screen).run()

if __name__ == "__main__":
    main()







