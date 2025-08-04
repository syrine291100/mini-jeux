# mini_games/reaction_timer.py
import pygame
import random
import time
import json
import os

# Configuration visuelle
BG = (30, 30, 30)
WAIT_COLOR = (200, 200, 200)
GO_COLOR = (100, 220, 100)
TOO_SOON_COLOR = (220, 100, 100)
TEXT_COLOR = (240, 240, 240)
FONT_SIZE = 32

SCORES_FILE = os.path.join(os.path.dirname(__file__), '..', 'best_scores.json')

# Difficultés : (nom, max_delay, min_delay, trials)
DIFFICULTIES = {
    '1': ('Facile', 2.5, 1.0, 5),
    '2': ('Moyen', 2.0, 0.5, 7),
    '3': ('Difficile', 1.5, 0.3, 10),
}


class ReactionTimerGame:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.difficulty = None
        self.max_delay = 2.5
        self.min_delay = 1.0
        self.trials = 5
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
            title = self.font.render("Reaction Timer : Choisis la difficulté", True, TEXT_COLOR)
            self.screen.blit(title, title.get_rect(center=(self.width // 2, 60)))
            for key, (name, maxd, mind, trials) in DIFFICULTIES.items():
                desc = f"{key}. {name} - {trials} essais, attente aléatoire [{mind:.1f}-{maxd:.1f}]s"
                txt = self.font.render(desc, True, TEXT_COLOR)
                self.screen.blit(txt, (40, 140 + int(key) * 50))
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
                        name, maxd, mind, trials = DIFFICULTIES[event.unicode]
                        self.difficulty = name
                        self.max_delay = maxd
                        self.min_delay = mind
                        self.trials = trials
                        return True
        return False

    def run_trial(self):
        # Phase attente random puis signal
        wait_time = random.uniform(self.min_delay, self.max_delay)
        state = 'waiting'  # waiting -> go -> result
        start_wait = time.time()
        go_time = None
        reacted = False
        reaction = None
        early = False

        while True:
            now = time.time()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None, False  # abort
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if state == 'waiting':
                            # trop tôt
                            early = True
                            state = 'too_soon'
                            early_time = now
                        elif state == 'go':
                            reaction = now - go_time
                            return reaction, True
                    elif event.key == pygame.K_q:
                        return None, False

            # Transition
            if state == 'waiting' and now - start_wait >= wait_time:
                state = 'go'
                go_time = time.time()

            # Affichage
            if state == 'waiting':
                color = WAIT_COLOR
                message = "Prépare-toi... attends le signal (espace)"
            elif state == 'go':
                color = GO_COLOR
                message = "GO ! Appuie sur ESPACE !"
            elif state == 'too_soon':
                color = TOO_SOON_COLOR
                message = "Trop tôt ! Réessaye dans un instant"
                # bref délai pour punir
                if now - early_time > 1.0:
                    return None, True  # compte comme essai raté
            else:
                color = WAIT_COLOR
                message = ""

            self.screen.fill(color)
            txt = self.font.render(message, True, TEXT_COLOR)
            self.screen.blit(txt, txt.get_rect(center=(self.width // 2, self.height // 2)))
            pygame.display.flip()
            pygame.time.Clock().tick(60)

    def run(self):
        if not self.choose_difficulty():
            return
        pygame.display.set_caption("Reaction Timer")
        results = []
        running = True
        for i in range(1, self.trials + 1):
            # écran de préparation
            prep = True
            while prep:
                self.screen.fill(BG)
                info = self.font.render(f"Essai {i}/{self.trials} - Appuie sur ESPACE pour commencer", True, TEXT_COLOR)
                diff_txt = self.font.render(f"Difficulté: {self.difficulty}", True, TEXT_COLOR)
                self.screen.blit(info, info.get_rect(center=(self.width // 2, self.height // 2 - 20)))
                self.screen.blit(diff_txt, diff_txt.get_rect(center=(self.width // 2, self.height // 2 + 20)))
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        prep = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            prep = False
                        elif event.key == pygame.K_q:
                            running = False
                            prep = False
                if not running:
                    break
            if not running:
                break
            reaction, ok = self.run_trial()
            if reaction is None and not ok:
                # aborted completely
                return
            # si trop tôt, on peut enregistrer comme un grand temps (pénalité) ou ignorer ; on marque None
            results.append(reaction)
            # petit feedback
            self.screen.fill(BG)
            if reaction is None:
                msg = "Trop tôt ou raté"
            else:
                msg = f"Temps de réaction: {reaction*1000:.0f} ms"
            feedback = self.font.render(msg, True, TEXT_COLOR)
            self.screen.blit(feedback, feedback.get_rect(center=(self.width // 2, self.height // 2)))
            pygame.display.flip()
            pygame.time.delay(800)

        # Calcul des statistiques
        valid_times = [r for r in results if r is not None]
        avg = sum(valid_times) / len(valid_times) if valid_times else None
        best = min(valid_times) if valid_times else None
        worst = max(valid_times) if valid_times else None

        # Sauvegarde du meilleur (moyenne la plus basse) et meilleur simple
        key_avg = f"Reaction_{self.difficulty}_best_avg"
        key_single = f"Reaction_{self.difficulty}_best_single"
        prev_avg = self.best_scores.get(key_avg)
        prev_single = self.best_scores.get(key_single)
        updated = False
        if avg is not None:
            if (prev_avg is None) or (avg < prev_avg):
                self.best_scores[key_avg] = round(avg, 3)
                updated = True
            if (prev_single is None) or (best < prev_single):
                self.best_scores[key_single] = round(best, 3)
                updated = True
        if updated:
            self.save_scores()

        # Écran de résultat
        while True:
            self.screen.fill(BG)
            y = 80
            title = self.font.render("Résultats", True, TEXT_COLOR)
            self.screen.blit(title, title.get_rect(center=(self.width // 2, y)))
            y += 50
            if avg is not None:
                self.screen.blit(self.font.render(f"Temps moyen   : {avg*1000:.0f} ms", True, TEXT_COLOR), (60, y)); y += 30
                self.screen.blit(self.font.render(f"Meilleur      : {best*1000:.0f} ms", True, TEXT_COLOR), (60, y)); y += 30
                self.screen.blit(self.font.render(f"Pire          : {worst*1000:.0f} ms", True, TEXT_COLOR), (60, y)); y += 30
            else:
                self.screen.blit(self.font.render("Aucun temps valide enregistré.", True, TEXT_COLOR), (60, y)); y += 30
            self.screen.blit(self.font.render(f"Scores enregistrés ({self.difficulty}):", True, TEXT_COLOR), (60, y)); y += 30
            self.screen.blit(self.font.render(f"Meilleure moyenne : {self.best_scores.get(key_avg, '-')}", True, TEXT_COLOR), (60, y)); y += 30
            self.screen.blit(self.font.render(f"Meilleur simple   : {self.best_scores.get(key_single, '-')}", True, TEXT_COLOR), (60, y)); y += 40
            prompt = self.font.render("Appuie sur Entrée pour revenir", True, TEXT_COLOR)
            self.screen.blit(prompt, (self.width // 2 - prompt.get_width() // 2, self.height - 80))
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                    return
