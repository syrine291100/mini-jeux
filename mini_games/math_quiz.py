import pygame
import random
import time
import json
import os

# mini_games/math_quiz.py
# Quiz de maths avec niveaux : Facile, Moyen, Difficile
# Stocke les meilleurs scores (nombre de bonnes réponses sur total) dans best_scores.json

# Couleurs / paramètres
BG = (25, 25, 50)
TEXT_COLOR = (240, 240, 240)
HIGHLIGHT = (100, 200, 255)
FONT_SIZE = 32

SCORES_FILE = os.path.join(os.path.dirname(__file__), '..', 'best_scores.json')

DIFFICULTIES = {
    '1': ('Facile', ['+', '-'], 0, 20, 10, 10),  # (nom, ops, min, max, questions, seconds/question)
    '2': ('Moyen', ['*'], 0, 12, 12, 8),
    '3': ('Difficile', ['+', '-', '*', '/'], 1, 20, 15, 6),
}

class MathQuizGame:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.difficulty = None
        self.ops = []
        self.min_val = 0
        self.max_val = 10
        self.total_questions = 10
        self.time_per_question = 10
        self.best_scores = self.load_scores()
        self.current_question = 0
        self.score = 0
        self.input_text = ''
        self.feedback = ''

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
            title = self.font.render("Quiz de Maths : Choisis la difficulté", True, TEXT_COLOR)
            self.screen.blit(title, title.get_rect(center=(self.width//2, 60)))
            for key, (name, ops, mini, maxi, qcount, tpu) in DIFFICULTIES.items():
                desc = f"{key}. {name} ({qcount} questions, {tpu}s/question)"
                txt = self.font.render(desc, True, TEXT_COLOR)
                self.screen.blit(txt, (80, 140 + int(key)*50))
            info = self.font.render("1/2/3 pour choisir, Q pour quitter", True, TEXT_COLOR)
            self.screen.blit(info, (80, self.height - 60))
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return False
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_q:
                        return False
                    if e.unicode in DIFFICULTIES:
                        self.difficulty, self.ops, self.min_val, self.max_val, self.total_questions, self.time_per_question = DIFFICULTIES[e.unicode]
                        return True
        return False

    def generate_problem(self):
        op = random.choice(self.ops)
        if op == '+':
            a = random.randint(self.min_val, self.max_val)
            b = random.randint(self.min_val, self.max_val)
            return f"{a} + {b}", a + b
        elif op == '-':
            a = random.randint(self.min_val, self.max_val)
            b = random.randint(self.min_val, a)
            return f"{a} - {b}", a - b
        elif op == '*':
            a = random.randint(self.min_val, self.max_val)
            b = random.randint(self.min_val, self.max_val)
            return f"{a} * {b}", a * b
        elif op == '/':
            b = random.randint(1, self.max_val)
            result = random.randint(self.min_val, self.max_val)
            a = b * result
            return f"{a} / {b}", result
        a = random.randint(self.min_val, self.max_val)
        b = random.randint(self.min_val, self.max_val)
        return f"{a} + {b}", a + b

    def run(self):
        if not self.choose_difficulty():
            return
        self.current_question = 0
        self.score = 0
        running = True
        clock = pygame.time.Clock()

        while running and self.current_question < self.total_questions:
            expr, answer = self.generate_problem()
            self.input_text = ''
            self.feedback = ''
            question_start = time.time()
            answered = False

            while not answered:
                now = time.time()
                elapsed = now - question_start
                remaining = max(0, int(self.time_per_question - elapsed))
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        running = False
                        answered = True
                    elif e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_RETURN:
                            try:
                                user_val = int(self.input_text.strip())
                                if user_val == answer:
                                    self.score += 1
                                    self.feedback = "Correct!"
                                else:
                                    self.feedback = f"Faux, c'etait {answer}"
                            except ValueError:
                                self.feedback = "Réponse invalide"
                            answered = True
                        elif e.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                        elif e.unicode.isdigit() or (e.unicode == '-' and len(self.input_text) == 0):
                            self.input_text += e.unicode
                        elif e.key == pygame.K_q:
                            running = False
                            answered = True
                if elapsed >= self.time_per_question:
                    self.feedback = f"Trop tard, réponse: {answer}"
                    answered = True
                self.screen.fill(BG)
                header = self.font.render(f"Difficulté: {self.difficulty}", True, TEXT_COLOR)
                self.screen.blit(header, (20, 20))
                qtxt = self.font.render(f"Question {self.current_question+1}/{self.total_questions}", True, TEXT_COLOR)
                self.screen.blit(qtxt, (20, 60))
                expr_txt = self.font.render(expr + " = ?", True, HIGHLIGHT)
                self.screen.blit(expr_txt, (20, 110))
                input_txt = self.font.render(self.input_text, True, TEXT_COLOR)
                self.screen.blit(input_txt, (20, 160))
                timer_txt = self.font.render(f"Temps restant: {remaining}s", True, TEXT_COLOR)
                self.screen.blit(timer_txt, (20, 200))
                feedback_txt = self.font.render(self.feedback, True, TEXT_COLOR)
                self.screen.blit(feedback_txt, (20, 240))
                pygame.display.flip()
                clock.tick(60)
            self.current_question += 1
            time.sleep(0.5)

        key = f"MathQuiz_{self.difficulty}"
        prev = self.best_scores.get(key, 0)
        if self.score > prev:
            self.best_scores[key] = self.score
            self.save_scores()

        while True:
            self.screen.fill(BG)
            result = self.font.render(f"Résultat: {self.score}/{self.total_questions}", True, TEXT_COLOR)
            best = self.font.render(f"Meilleur ({self.difficulty}): {self.best_scores.get(key)}", True, TEXT_COLOR)
            prompt = self.font.render("Appuie sur Entrée pour revenir", True, TEXT_COLOR)
            self.screen.blit(result, (self.width//2 - result.get_width()//2, 120))
            self.screen.blit(best, (self.width//2 - best.get_width()//2, 170))
            self.screen.blit(prompt, (self.width//2 - prompt.get_width()//2, 240))
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                    return
