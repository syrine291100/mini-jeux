# -------------------------
# mini_games/pong.py
# -------------------------
import pygame
import time
import json
import os

# Paramètres du jeu
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_SIZE = 15
PADDLE_SPEED = 5
PADDLE_SPEED_AI = 4
BALL_SPEED = 4
WIN_SCORE = 3
BG = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)
WIN_COLOR = (255, 200, 50)
SCORES_FILE = os.path.join(os.path.dirname(__file__), '..', 'best_scores.json')

class PongGame:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.paddle1 = pygame.Rect(20, (self.height-PADDLE_HEIGHT)//2, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.paddle2 = pygame.Rect(self.width-20-PADDLE_WIDTH, (self.height-PADDLE_HEIGHT)//2, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.ball = pygame.Rect((self.width-BALL_SIZE)//2, (self.height-BALL_SIZE)//2, BALL_SIZE, BALL_SIZE)
        self.ball_vel = [BALL_SPEED, BALL_SPEED]
        self.score1 = 0
        self.score2 = 0
        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()
        self.mode = None
        self.start_time = 0

    def load_scores(self):
        try:
            with open(SCORES_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def save_scores(self, scores):
        with open(SCORES_FILE, 'w') as f:
            json.dump(scores, f)

    def choose_mode(self):
        choosing = True
        while choosing:
            self.screen.fill(BG)
            title = self.font.render("Pong : choisissez le mode", True, TEXT_COLOR)
            self.screen.blit(title, title.get_rect(center=(self.width//2, 100)))
            m1 = self.font.render("1. 2 Joueurs (W/S vs ↑/↓)", True, TEXT_COLOR)
            m2 = self.font.render("2. Solo vs IA", True, TEXT_COLOR)
            self.screen.blit(m1, m1.get_rect(center=(self.width//2, 200)))
            self.screen.blit(m2, m2.get_rect(center=(self.width//2, 260)))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN and event.unicode in ('1', '2'):
                    self.mode = '2joueurs' if event.unicode == '1' else 'solo'
                    return True
        return False

    def reset_ball(self):
        self.ball.center = (self.width//2, self.height//2)
        self.ball_vel[0] = -self.ball_vel[0]

    def run(self):
        if not self.choose_mode():
            return
        scores = self.load_scores()
        mode_key = f"Pong_{self.mode}"
        self.start_time = time.time()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w] and self.paddle1.top > 0:
                self.paddle1.y -= PADDLE_SPEED
            if keys[pygame.K_s] and self.paddle1.bottom < self.height:
                self.paddle1.y += PADDLE_SPEED
            if self.mode == '2joueurs':
                if keys[pygame.K_UP] and self.paddle2.top > 0:
                    self.paddle2.y -= PADDLE_SPEED
                if keys[pygame.K_DOWN] and self.paddle2.bottom < self.height:
                    self.paddle2.y += PADDLE_SPEED
            else:
                if self.ball.centery < self.paddle2.centery and self.paddle2.top > 0:
                    self.paddle2.y -= PADDLE_SPEED_AI
                elif self.ball.centery > self.paddle2.centery and self.paddle2.bottom < self.height:
                    self.paddle2.y += PADDLE_SPEED_AI
            self.ball.x += self.ball_vel[0]
            self.ball.y += self.ball_vel[1]
            if self.ball.top <= 0 or self.ball.bottom >= self.height:
                self.ball_vel[1] = -self.ball_vel[1]
            if self.ball.colliderect(self.paddle1) or self.ball.colliderect(self.paddle2):
                self.ball_vel[0] = -self.ball_vel[0]
            if self.ball.left <= 0:
                self.score2 += 1
                self.reset_ball()
            if self.ball.right >= self.width:
                self.score1 += 1
                self.reset_ball()
            self.screen.fill(BG)
            pygame.draw.rect(self.screen, TEXT_COLOR, self.paddle1)
            pygame.draw.rect(self.screen, TEXT_COLOR, self.paddle2)
            pygame.draw.ellipse(self.screen, TEXT_COLOR, self.ball)
            score_txt = self.font.render(f"{self.score1} : {self.score2}", True, TEXT_COLOR)
            self.screen.blit(score_txt, (self.width//2 - score_txt.get_width()//2, 20))
            pygame.display.flip()
            if self.mode == 'solo':
                # Affiche temps actuel
                elapsed = int(time.time() - self.start_time)
                timer_txt = self.font.render(f"Temps: {elapsed}s", True, TEXT_COLOR)
                self.screen.blit(timer_txt, (10, self.height-30))
                pygame.display.flip()
            if (self.score1 >= WIN_SCORE or self.score2 >= WIN_SCORE):
                end_time = time.time()
                duration = end_time - self.start_time
                # Calcul du score à enregistrer
                if self.mode == 'solo':
                    record = scores.get(mode_key, 0)
                    if duration > record:
                        scores[mode_key] = int(duration)
                else:
                    record = scores.get(mode_key)
                    if record is None or duration < record:
                        scores[mode_key] = int(duration)
                self.save_scores(scores)
                winner = "Joueur 1" if self.score1 > self.score2 else "Joueur 2"
                win_txt = self.font.render(f"{winner} a gagné!", True, WIN_COLOR)
                self.screen.blit(win_txt, win_txt.get_rect(center=(self.width//2, self.height//2)))
                pygame.display.flip()
                pygame.time.wait(2000)
                running = False
            self.clock.tick(60)
        # Retour automatique au menu
