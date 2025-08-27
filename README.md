
# Mini-jeux (Python)

Petite collection de **mini-jeux** pour pratiquer Python (structures, boucles, I/O).

🔧 Prérequis

Python 3.10+

(si un jeu utilise une lib externe) pip install <lib> — ex. pygame

▶️ Lancer avec le menu
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
python main.py

▶️ Lancer un jeu directement
python snake.py
python "tic-tac-toe.py"   # guillemets recommandés sur Windows

🎮 Jeux inclus
Jeu	Fichier
2048	game_2048.py
Breakout	breackout.py (orthographe actuelle du fichier)
Flappy	flappy.py
Devine le nombre	guess_number.py
High scores (utilitaire)	high_scores.py
Quiz de math	math_quiz.py
Memory	memory.py
Pendu	pendu.py
Pong	pong.py
Réaction (timer)	reaction_timer.py
Simon Says	simon_says.py
Taquin / Sliding puzzle	slidding_puzzle.py
Snake	snake.py
Sudoku	sudoku.py
Tic-Tac-Toe (morpion)	tic-tac-toe.py
Whack-a-Mole	whack_a_mole.py

Dossier test/ : utilitaires/tests éventuels.

✅ TODO

Renommer plus tard breackout.py → breakout.py et slidding_puzzle.py → sliding_puzzle.py

Ajouter requirements.txt si certains jeux utilisent pygame/autres

Centraliser les scores (high_scores.py) + petits tests (pytest)
