import pygame
import random
import time
import json
import os

# Configurations
CELL_SIZE = 20
BG = (15, 15, 40)
SNAKE_COLOR = (100, 255, 100)
FRUIT_COLOR = (255, 80, 80)
OBSTACLE_COLOR = (200, 100, 50)
TEXT_COLOR = (240, 240, 240)
FONT_SIZE = 24
SCORES_FILE = os.path.join(os.path.dirname(__file__), '..', 'best_scores.json')

DIFFICULTIES = {
    '1': ('Facile', 0.15, 60, 5),   # (name, move_interval sec, time_limit sec, obstacles)
    '2': ('Moyen', 0.1, 45, 10),
    '3': ('Difficile', 0.07, 30, 15),
}


class SnakeGame:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.cols = self.width // CELL_SIZE
        self.rows = self.height // CELL_SIZE
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.difficulty = None
        self.move_interval = 0.1
        self.time_limit = 60
        self.obstacle_count = 5
        self.snake = []
        self.direction = (1, 0)
        self.fruit = None
        self.obstacles = []
        self.last_move = 0
        self.start_time = 0
        self.score = 0
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

    def choose_difficulty(self):
        choosing = True
        while choosing:
            self.screen.fill(BG)
            title = self.font.render("Snake : Choisis la difficulté", True, TEXT_COLOR)
            self.screen.blit(title, title.get_rect(center=(self.width // 2, 80)))
            for key, (name, interval, tlimit, obs) in DIFFICULTIES.items():
                desc = f"{key}. {name} - Temps: {tlimit}s Objets: {obs}"
                txt = self.font.render(desc, True, TEXT_COLOR)
                self.screen.blit(txt, (50, 160 + int(key) * 50))
            info = self.font.render("1/2/3 pour choisir, Q pour quitter", True, TEXT_COLOR)
            self.screen.blit(info, (50, self.height - 50))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        return False
                    if event.unicode in DIFFICULTIES:
                        name, interval, tlimit, obs = DIFFICULTIES[event.unicode]
                        self.difficulty = name
                        self.move_interval = interval
                        self.time_limit = tlimit
                        self.obstacle_count = obs
                        return True
        return False

    def random_cell(self):
        return (random.randint(0, self.cols - 1), random.randint(0, self.rows - 1))

    def position_to_rect(self, pos):
        x, y = pos
        return pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

    def place_obstacles(self):
        self.obstacles = []
        forbidden = set(self.snake)
        while len(self.obstacles) < self.obstacle_count:
            cell = self.random_cell()
            if cell in forbidden:
                continue
            if cell == self.fruit:
                continue
            if cell in self.obstacles:
                continue
            self.obstacles.append(cell)

    def place_fruit(self):
        while True:
            candidate = self.random_cell()
            if candidate in self.snake:
                continue
            if candidate in self.obstacles:
                continue
            self.fruit = candidate
            break

    def reset(self):
        mid = (self.cols // 2, self.rows // 2)
        self.snake = [mid, (mid[0] - 1, mid[1]), (mid[0] - 2, mid[1])]
        self.direction = (1, 0)
        self.score = 0
        self.fruit = None
        self.place_obstacles()
        self.place_fruit()
        self.last_move = time.time()
        self.start_time = time.time()

    def run(self):
        if not self.choose_difficulty():
            return
        # initial placement
        self.reset()
        running = True
        clock = pygame.time.Clock()

        while running:
            now = time.time()
            elapsed = now - self.start_time
            remaining = max(0, int(self.time_limit - elapsed))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_w) and self.direction != (0, 1):
                        self.direction = (0, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s) and self.direction != (0, -1):
                        self.direction = (0, 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a) and self.direction != (1, 0):
                        self.direction = (-1, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d) and self.direction != (-1, 0):
                        self.direction = (1, 0)
                    elif event.key == pygame.K_q:
                        running = False

            if now - self.last_move >= self.move_interval:
                self.last_move = now
                # move snake
                head = self.snake[0]
                new_head = (head[0] + self.direction[0], head[1] + self.direction[1])

                # Check collisions: murs
                if not (0 <= new_head[0] < self.cols and 0 <= new_head[1] < self.rows):
                    running = False  # mort contre le mur
                # self-collision
                elif new_head in self.snake:
                    running = False
                # obstacle
                elif new_head in self.obstacles:
                    running = False
                else:
                    self.snake.insert(0, new_head)
                    if new_head == self.fruit:
                        self.score += 1
                        # repositionner fruit et éventuellement obstacles (on garde fixes)
                        self.place_fruit()
                    else:
                        self.snake.pop()  # avance sans grandir

            # Fin si timer est écoulé
            if elapsed >= self.time_limit:
                running = False

            # Affichage
            self.screen.fill(BG)
            # Obstacles
            for o in self.obstacles:
                pygame.draw.rect(self.screen, OBSTACLE_COLOR, self.position_to_rect(o))
            # Fruit
            if self.fruit:
                pygame.draw.rect(self.screen, FRUIT_COLOR, self.position_to_rect(self.fruit))
            # Snake
            for segment in self.snake:
                pygame.draw.rect(self.screen, SNAKE_COLOR, self.position_to_rect(segment))
            # UI
            info_txt = self.font.render(f"Difficulté: {self.difficulty}", True, TEXT_COLOR)
            score_txt = self.font.render(f"Fruits: {self.score}", True, TEXT_COLOR)
            timer_txt = self.font.render(f"Temps restant: {remaining}s", True, TEXT_COLOR)
            best_key = f"Snake_{self.difficulty}"
            best = self.best_scores.get(best_key, 0)
            best_txt = self.font.render(f"Meilleur (fruits): {best}", True, TEXT_COLOR)
            self.screen.blit(info_txt, (10, 10))
            self.screen.blit(score_txt, (10, 40))
            self.screen.blit(timer_txt, (10, 70))
            self.screen.blit(best_txt, (10, 100))

            pygame.display.flip()
            clock.tick(60)

        # Fin de partie : mise à jour du meilleur score si besoin
        key = f"Snake_{self.difficulty}"
        prev = self.best_scores.get(key, 0)
        if self.score > prev:
            self.best_scores[key] = self.score
            self.save_scores()

        # Message de fin
        self.screen.fill(BG)
        end_msg = self.font.render(f"Fin! Fruits mangés: {self.score}", True, TEXT_COLOR)
        record_msg = self.font.render(f"Meilleur pour {self.difficulty}: {self.best_scores.get(key)}", True, TEXT_COLOR)
        prompt = self.font.render("Appuie sur Entrée pour revenir", True, TEXT_COLOR)
        self.screen.blit(end_msg, end_msg.get_rect(center=(self.width // 2, self.height // 2 - 30)))
        self.screen.blit(record_msg, record_msg.get_rect(center=(self.width // 2, self.height // 2 + 10)))
        self.screen.blit(prompt, prompt.get_rect(center=(self.width // 2, self.height // 2 + 50)))
        pygame.display.flip()
        waiting = True
        while waiting:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    waiting = False
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                    waiting = False
