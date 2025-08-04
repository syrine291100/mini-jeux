import pygame
import random
import time
import json
import os

# Whack-a-Mole avec niveaux
# Fichier attendu : mini_games/whack_a_mole.py
# Intégration des meilleurs temps pour chaque niveau dans best_scores.json

# Paramètres d'affichage
BG = (30, 30, 50)
MOLE_COLOR = (200, 100, 60)
MOLE_HIT_COLOR = (100, 255, 100)
HOLE_COLOR = (50, 50, 80)
TEXT_COLOR = (240, 240, 240)
FONT_SIZE = 28

SCORES_FILE = os.path.join(os.path.dirname(__file__), '..', 'best_scores.json')

# Configuration des niveaux
LEVELS = [
    {"name": "Facile", "mole_interval": 1.2, "visible_time": 1.0, "simultaneous": 1, "target_hits": 10, "time_limit": 30},
    {"name": "Moyen", "mole_interval": 1.0, "visible_time": 0.8, "simultaneous": 2, "target_hits": 15, "time_limit": 30},
    {"name": "Difficile", "mole_interval": 0.7, "visible_time": 0.6, "simultaneous": 3, "target_hits": 20, "time_limit": 30},
    {"name": "Expert", "mole_interval": 0.5, "visible_time": 0.5, "simultaneous": 4, "target_hits": 25, "time_limit": 30},
]

class WhackAMoleGame:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.best_scores = self.load_scores()
        self.holes = []  # positions des trous
        self.moles = []  # moles actives

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

    def prepare_holes(self):
        # grille 4x3 de trous centrés
        cols = 4
        rows = 3
        margin_x = 80
        margin_y = 120
        spacing_x = (self.width - 2 * margin_x) // (cols - 1)
        spacing_y = (self.height - 250 - 2 * margin_y // 3) // (rows - 1)
        self.holes = []
        for r in range(rows):
            for c in range(cols):
                x = margin_x + c * spacing_x
                y = margin_y + r * spacing_y
                self.holes.append((x, y))

    def draw_holes(self):
        for pos in self.holes:
            x, y = pos
            pygame.draw.circle(self.screen, HOLE_COLOR, (x, y), 35)

    def spawn_moles(self, level_conf, now, last_spawn):
        # créer jusqu'à simultaneous moles si temps écoulé
        if now - last_spawn < level_conf["mole_interval"]:
            return last_spawn
        present = [m for m in self.moles if not m.get("removed")]
        possible_slots = [h for h in self.holes if all((h != m["pos"] or m.get("removed")) for m in self.moles)]
        to_create = level_conf["simultaneous"] - len(present)
        for _ in range(max(0, to_create)):
            if not possible_slots:
                break
            choice = random.choice(possible_slots)
            possible_slots.remove(choice)
            self.moles.append({
                "pos": choice,
                "spawn_time": now,
                "visible_until": now + level_conf["visible_time"],
                "hit": False,
                "removed": False,
            })
        return now

    def draw_moles(self, now):
        for m in self.moles:
            if m.get("removed"):
                continue
            if now > m["visible_until"] and not m.get("hit"):
                m["removed"] = True
                continue
            x, y = m["pos"]
            color = MOLE_HIT_COLOR if m.get("hit") else MOLE_COLOR
            pygame.draw.circle(self.screen, color, (x, y), 30)

    def run_level(self, level_index):
        level_conf = LEVELS[level_index]
        target = level_conf["target_hits"]
        time_limit = level_conf["time_limit"]
        hits = 0
        start = time.time()
        last_spawn = 0
        self.moles = []
        level_complete_time = None
        while True:
            now = time.time()
            elapsed = now - start
            remaining = max(0, int(time_limit - elapsed))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False, level_index, hits
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    for m in self.moles:
                        if m.get("removed") or m.get("hit"):
                            continue
                        x, y = m["pos"]
                        dist = ((mx - x) ** 2 + (my - y) ** 2) ** 0.5
                        if dist <= 30:
                            m["hit"] = True
                            hits += 1
                            # un petit feedback visuel, la mole disparaît
                            m["removed"] = True
                            if hits >= target and level_complete_time is None:
                                level_complete_time = now - start
            # spawn
            last_spawn = self.spawn_moles(level_conf, now, last_spawn)
            # dessin
            self.screen.fill(BG)
            # en-tête
            title = self.font.render(f"Whack-a-Mole - Niveau {level_conf['name']}", True, TEXT_COLOR)
            self.screen.blit(title, (20, 10))
            score_txt = self.font.render(f"Touches: {hits}/{target}", True, TEXT_COLOR)
            self.screen.blit(score_txt, (20, 40))
            timer_txt = self.font.render(f"Temps: {remaining}s", True, TEXT_COLOR)
            self.screen.blit(timer_txt, (20, 70))
            best_key_level = f"WhackAMole_{level_conf['name']}_time"
            best_time = self.best_scores.get(best_key_level)
            if best_time:
                best_txt = self.font.render(f"Meilleur temps: {best_time:.1f}s", True, TEXT_COLOR)
                self.screen.blit(best_txt, (20, 100))
            self.draw_holes()
            self.draw_moles(now)
            pygame.display.flip()
            # conditions de fin
            if hits >= target:
                # niveau terminé
                # enregistre temps si meilleur
                if level_complete_time is not None:
                    prev = self.best_scores.get(best_key_level)
                    if (prev is None) or (level_complete_time < prev):
                        self.best_scores[best_key_level] = round(level_complete_time, 1)
                        self.save_scores()
                return True, level_index + 1, hits
            if elapsed >= time_limit:
                return False, level_index, hits
            time.sleep(0.01)
        # fin boucle

    def run(self):
        self.prepare_holes()
        level_index = 0
        total_hits = 0
        progressed = True
        while level_index < len(LEVELS) and progressed:
            success, next_index, hits = self.run_level(level_index)
            total_hits += hits
            if success:
                # mise à jour de meilleur niveau atteint
                prev_lvl = self.best_scores.get("WhackAMole_MaxLevel", 0)
                if level_index + 1 > prev_lvl:
                    self.best_scores["WhackAMole_MaxLevel"] = level_index + 1
                    self.save_scores()
                # message de transition
                self.screen.fill(BG)
                msg = self.font.render(f"Niveau {LEVELS[level_index]['name']} réussi!", True, TEXT_COLOR)
                prompt = self.font.render("Appuie sur Entrée pour continuer", True, TEXT_COLOR)
                self.screen.blit(msg, msg.get_rect(center=(self.width//2, self.height//2 - 20)))
                self.screen.blit(prompt, prompt.get_rect(center=(self.width//2, self.height//2 + 20)))
                pygame.display.flip()
                waiting = True
                while waiting:
                    for e in pygame.event.get():
                        if e.type == pygame.QUIT:
                            waiting = False
                            progressed = False
                        elif e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                            waiting = False
                level_index = next_index
            else:
                progressed = False
        # fin jeu: écran résultat global
        self.screen.fill(BG)
        if level_index >= len(LEVELS):
            end_msg = f"Tu as fini tous les niveaux! Hits totaux: {total_hits}"
        else:
            lvlname = LEVELS[level_index]['name'] if level_index < len(LEVELS) else "-"
            end_msg = f"Game Over au niveau {lvlname}. Hits totaux: {total_hits}"
        txt = self.font.render(end_msg, True, TEXT_COLOR)
        best_lvl = self.best_scores.get("WhackAMole_MaxLevel", 0)
        best_lvl_txt = self.font.render(f"Meilleur niveau atteint: {best_lvl}", True, TEXT_COLOR)
        prompt = self.font.render("Appuie sur Entrée pour revenir", True, TEXT_COLOR)
        self.screen.blit(txt, txt.get_rect(center=(self.width//2, self.height//2 - 30)))
        self.screen.blit(best_lvl_txt, best_lvl_txt.get_rect(center=(self.width//2, self.height//2 + 10)))
        self.screen.blit(prompt, prompt.get_rect(center=(self.width//2, self.height//2 + 50)))
        pygame.display.flip()
        waiting = True
        while waiting:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    waiting = False
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                    waiting = False
```}
