# mini_games/flappy.py
import pygame
import random
import time
import json
import os

# Couleurs / paramètres
BG = (30, 180, 230)
BIRD_COLOR = (255, 240, 60)
PIPE_COLOR = (50, 180, 60)
GROUND_COLOR = (170, 100, 40)
TEXT_COLOR = (15, 15, 15)
FONT_SIZE = 28

GRAVITY = 0.5
FLAP_STRENGTH = -8

SCORES_FILE = os.path.join(os.path.dirname(__file__), '..', 'best_scores.json')

DIFFICULTIES = {
    '1': ('Facile', 160, 2.0, 1500),    # (nom, gap, vitesse, intervalle_ms)
    '2': ('Moyen', 130, 2.5, 1300),
    '3': ('Difficile', 100, 3.0, 1100),
}


class FlappyGame:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.difficulty = None
        self.pipe_gap = 150
        self.pipe_speed = 2.0
        self.spawn_interval = 1500  # en ms
        self.bird = None
        self.bird_vel = 0
        self.pipes = []  # liste de tuples (x, top_height)
        self.last_spawn = 0
        self.score = 0
        self.best_scores = self.load_scores()
        self.ground_height = 50

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
            title = self.font.render("Flappy : Choisis la difficulté", True, TEXT_COLOR)
            self.screen.blit(title, title.get_rect(center=(self.width // 2, 80)))
            for key, (name, gap, speed, interval) in DIFFICULTIES.items():
                desc = f"{key}. {name} - Écart: {gap}px, vitesse: {speed:.1f}"
                txt = self.font.render(desc, True, TEXT_COLOR)
                self.screen.blit(txt, (40, 160 + int(key) * 50))
            info = self.font.render("1/2/3 pour choisir, Echap pour quitter", True, TEXT_COLOR)
            self.screen.blit(info, (40, self.height - 50))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False
                    if event.unicode in DIFFICULTIES:
                        name, gap, speed, interval = DIFFICULTIES[event.unicode]
                        self.difficulty = name
                        self.pipe_gap = gap
                        self.pipe_speed = speed
                        self.spawn_interval = interval
                        return True
        return False

    def reset(self):
        # Oiseau : carré simple ou cercle
        self.bird = [self.width // 4, self.height // 2]
        self.bird_vel = 0
        self.pipes = []
        self.last_spawn = pygame.time.get_ticks()
        self.score = 0

    def spawn_pipe(self):
        # hauteur aléatoire pour le haut entre 50 et height - gap - ground - 50
        min_top = 50
        max_top = self.height - self.pipe_gap - self.ground_height - 50
        top_height = random.randint(min_top, max_top)
        x = self.width
        self.pipes.append([x, top_height])

    def draw(self):
        self.screen.fill(BG)
        # Pipes
        for px, top_h in self.pipes:
            # haut
            pygame.draw.rect(self.screen, PIPE_COLOR, pygame.Rect(px, 0, 60, top_h))
            # bas
            pygame.draw.rect(
                self.screen,
                PIPE_COLOR,
                pygame.Rect(px, top_h + self.pipe_gap, 60, self.height - top_h - self.pipe_gap - self.ground_height)
            )
        # Sol
        pygame.draw.rect(self.screen, GROUND_COLOR, pygame.Rect(0, self.height - self.ground_height, self.width, self.ground_height))
        # Oiseau
        bird_rect = pygame.Rect(int(self.bird[0]) - 12, int(self.bird[1]) - 12, 24, 24)
        pygame.draw.ellipse(self.screen, BIRD_COLOR, bird_rect)
        # Score
        score_txt = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_txt, (10, 10))
        best_key = f"Flappy_{self.difficulty}"
        best = self.best_scores.get(best_key, 0)
        best_txt = self.font.render(f"Meilleur: {best}", True, TEXT_COLOR)
        self.screen.blit(best_txt, (10, 40))
        diff_txt = self.font.render(f"Difficulté: {self.difficulty}", True, TEXT_COLOR)
        self.screen.blit(diff_txt, (self.width - 220, 10))

    def check_collision(self):
        # Oiseau
        bx, by = self.bird
        bird_rect = pygame.Rect(int(bx) - 12, int(by) - 12, 24, 24)
        # Sol / plafond
        if by - 12 <= 0 or by + 12 >= self.height - self.ground_height:
            return True
        # Pipes
        for px, top_h in self.pipes:
            top_rect = pygame.Rect(px, 0, 60, top_h)
            bottom_rect = pygame.Rect(px, top_h + self.pipe_gap, 60, self.height - top_h - self.pipe_gap - self.ground_height)
            if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
                return True
        return False

    def run(self):
        if not self.choose_difficulty():
            return
        self.reset()
        clock = pygame.time.Clock()
        running = True
        passed_pipes = set()

        while running:
            dt = clock.tick(60)
            now = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_SPACE, pygame.K_UP):
                        self.bird_vel = FLAP_STRENGTH
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.bird_vel = FLAP_STRENGTH

            # Physique
            self.bird_vel += GRAVITY
            self.bird[1] += self.bird_vel

            # Pipes mouvement
            for pipe in self.pipes:
                pipe[0] -= self.pipe_speed

            # Génération de pipe
            if now - self.last_spawn >= self.spawn_interval:
                self.spawn_pipe()
                self.last_spawn = now

            # Retirer pipes passées
            self.pipes = [p for p in self.pipes if p[0] + 60 > 0]

            # Score : quand l'oiseau passe un pipe (x de pipe+largeur passe sous bird)
            for i, (px, top_h) in enumerate(self.pipes):
                if px + 60 < self.bird[0] and i not in passed_pipes:
                    passed_pipes.add(i)
                    self.score += 1

            # Dessin
            self.draw()
            pygame.display.flip()

            # Collision
            if self.check_collision():
                break

        # Mise à jour du meilleur score
        key = f"Flappy_{self.difficulty}"
        prev = self.best_scores.get(key, 0)
        if self.score > prev:
            self.best_scores[key] = self.score
            self.save_scores()

        # Écran de fin
        self.screen.fill(BG)
        end_txt = self.font.render(f"Fin! Score: {self.score}", True, TEXT_COLOR)
        best_txt = self.font.render(f"Meilleur ({self.difficulty}): {self.best_scores.get(key)}", True, TEXT_COLOR)
        prompt = self.font.render("Appuie sur Entrée pour revenir", True, TEXT_COLOR)
        self.screen.blit(end_txt, end_txt.get_rect(center=(self.width // 2, self.height // 2 - 30)))
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
