# mini_games/breakout.py
import pygame
import random
import time
import json
import os

# Couleurs
BG = (10, 10, 30)
PADDLE_COLOR = (180, 180, 255)
BALL_COLOR = (255, 220, 100)
BRICK_COLORS = [(200, 50, 50), (200, 120, 50), (200, 200, 50)]
TEXT_COLOR = (240, 240, 240)

# Tailles
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
BALL_RADIUS = 8
BRICK_WIDTH = 60
BRICK_HEIGHT = 20
BRICK_PADDING = 5
TOP_OFFSET = 80

FONT_SIZE = 28
SCORES_FILE = os.path.join(os.path.dirname(__file__), '..', 'best_scores.json')

DIFFICULTIES = {
    '1': ('Facile', 4, 5, 1.5),    # (nom, colonnes de briques, rangées, vitesse de balle)
    '2': ('Moyen', 7, 6, 2.0),
    '3': ('Difficile', 9, 7, 2.5),
}


class BreakoutGame:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.difficulty = None
        self.cols = 7
        self.rows = 5
        self.ball_speed = 2.0
        self.paddle = pygame.Rect(
            (self.width - PADDLE_WIDTH) // 2,
            self.height - 50,
            PADDLE_WIDTH,
            PADDLE_HEIGHT,
        )
        self.ball_pos = [self.width // 2, self.height // 2]
        self.ball_vel = [self.ball_speed, -self.ball_speed]
        self.bricks = []
        self.lives = 3
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
            title = self.font.render("Casse-briques : Choisis la difficulté", True, TEXT_COLOR)
            self.screen.blit(title, title.get_rect(center=(self.width // 2, 80)))
            for key, (name, cols, rows, speed) in DIFFICULTIES.items():
                desc = f"{key}. {name} - {cols}x{rows} briques, vitesse {speed:.1f}"
                txt = self.font.render(desc, True, TEXT_COLOR)
                self.screen.blit(txt, (40, 160 + int(key) * 50))
            info = self.font.render("1/2/3 pour choisir, Q pour quitter", True, TEXT_COLOR)
            self.screen.blit(info, (40, self.height - 50))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        return False
                    if event.unicode in DIFFICULTIES:
                        name, cols, rows, speed = DIFFICULTIES[event.unicode]
                        self.difficulty = name
                        self.cols = cols
                        self.rows = rows
                        self.ball_speed = speed
                        return True
        return False

    def setup(self):
        # Paddle
        self.paddle.width = PADDLE_WIDTH
        self.paddle.x = (self.width - PADDLE_WIDTH) // 2
        # Ball
        self.ball_pos = [self.width // 2, self.height - 60]
        self.ball_vel = [self.ball_speed, -self.ball_speed]
        # Bricks
        self.bricks = []
        total_width = self.cols * (BRICK_WIDTH + BRICK_PADDING) - BRICK_PADDING
        start_x = (self.width - total_width) // 2
        for row in range(self.rows):
            for col in range(self.cols):
                x = start_x + col * (BRICK_WIDTH + BRICK_PADDING)
                y = TOP_OFFSET + row * (BRICK_HEIGHT + BRICK_PADDING)
                rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
                # assign color tier by row (top rows worth more)
                color = BRICK_COLORS[min(row, len(BRICK_COLORS) - 1)]
                self.bricks.append({'rect': rect, 'color': color, 'hit': False})
        self.lives = 3
        self.score = 0

    def draw(self):
        self.screen.fill(BG)
        # Bricks
        for b in self.bricks:
            if not b['hit']:
                pygame.draw.rect(self.screen, b['color'], b['rect'])
                pygame.draw.rect(self.screen, (30, 30, 30), b['rect'], 2)
        # Paddle
        pygame.draw.rect(self.screen, PADDLE_COLOR, self.paddle)
        # Ball
        pygame.draw.circle(self.screen, BALL_COLOR, (int(self.ball_pos[0]), int(self.ball_pos[1])), BALL_RADIUS)
        # UI
        score_txt = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        lives_txt = self.font.render(f"Vies: {self.lives}", True, TEXT_COLOR)
        best_key = f"Breakout_{self.difficulty}"
        best = self.best_scores.get(best_key, 0)
        best_txt = self.font.render(f"Meilleur: {best}", True, TEXT_COLOR)
        diff_txt = self.font.render(f"Difficulté: {self.difficulty}", True, TEXT_COLOR)
        self.screen.blit(score_txt, (10, 10))
        self.screen.blit(lives_txt, (10, 40))
        self.screen.blit(diff_txt, (self.width - 220, 10))
        self.screen.blit(best_txt, (self.width - 220, 40))

    def run(self):
        if not self.choose_difficulty():
            return
        self.setup()
        clock = pygame.time.Clock()
        running = True
        while running:
            dt = clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Input paddle
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.paddle.x -= 6
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.paddle.x += 6
            # Clamp paddle
            if self.paddle.left < 0:
                self.paddle.left = 0
            if self.paddle.right > self.width:
                self.paddle.right = self.width

            # Move ball
            self.ball_pos[0] += self.ball_vel[0]
            self.ball_pos[1] += self.ball_vel[1]

            # Collisions murs
            if self.ball_pos[0] - BALL_RADIUS <= 0 or self.ball_pos[0] + BALL_RADIUS >= self.width:
                self.ball_vel[0] *= -1
            if self.ball_pos[1] - BALL_RADIUS <= 0:
                self.ball_vel[1] *= -1

            # Collision paddle
            paddle_rect = self.paddle
            ball_rect = pygame.Rect(int(self.ball_pos[0] - BALL_RADIUS), int(self.ball_pos[1] - BALL_RADIUS),
                                    BALL_RADIUS * 2, BALL_RADIUS * 2)
            if ball_rect.colliderect(paddle_rect) and self.ball_vel[1] > 0:
                self.ball_vel[1] *= -1
                # ajuster direction selon position sur la raquette
                offset = (self.ball_pos[0] - (paddle_rect.x + paddle_rect.width / 2)) / (paddle_rect.width / 2)
                self.ball_vel[0] = self.ball_speed * offset

            # Collision briques
            for b in self.bricks:
                if not b['hit'] and ball_rect.colliderect(b['rect']):
                    b['hit'] = True
                    self.score += 10
                    # rebond approximatif
                    if abs(ball_rect.bottom - b['rect'].top) < 10 and self.ball_vel[1] > 0:
                        self.ball_vel[1] *= -1
                    elif abs(ball_rect.top - b['rect'].bottom) < 10 and self.ball_vel[1] < 0:
                        self.ball_vel[1] *= -1
                    else:
                        self.ball_vel[0] *= -1
                    break

            # Ball out bottom
            if self.ball_pos[1] - BALL_RADIUS > self.height:
                self.lives -= 1
                if self.lives <= 0:
                    running = False
                else:
                    # reset position
                    self.ball_pos = [self.width // 2, self.height - 60]
                    self.ball_vel = [self.ball_speed * random.choice((1, -1)), -self.ball_speed]

            # Victoire
            if all(b['hit'] for b in self.bricks):
                running = False

            self.draw()
            pygame.display.flip()

        # Fin de partie : sauvegarde meilleur score
        key = f"Breakout_{self.difficulty}"
        prev = self.best_scores.get(key, 0)
        if self.score > prev:
            self.best_scores[key] = self.score
            self.save_scores()

        # Écran de fin
        self.screen.fill(BG)
        if all(b['hit'] for b in self.bricks):
            end_msg = "Gagné !"
        else:
            end_msg = "Perdu..."
        end_txt = self.font.render(end_msg, True, TEXT_COLOR)
        score_txt = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        best_txt = self.font.render(f"Meilleur ({self.difficulty}): {self.best_scores.get(key)}", True, TEXT_COLOR)
        prompt = self.font.render("Appuie sur Entrée pour revenir", True, TEXT_COLOR)
        self.screen.blit(end_txt, end_txt.get_rect(center=(self.width // 2, self.height // 2 - 40)))
        self.screen.blit(score_txt, score_txt.get_rect(center=(self.width // 2, self.height // 2)))
        self.screen.blit(best_txt, best_txt.get_rect(center=(self.width // 2, self.height // 2 + 40)))
        self.screen.blit(prompt, prompt.get_rect(center=(self.width // 2, self.height // 2 + 90)))
        pygame.display.flip()
        waiting = True
        while waiting:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    waiting = False
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                    waiting = False
