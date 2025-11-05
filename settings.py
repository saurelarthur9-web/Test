# --- DIMENSIONS DE L'ÉCRAN ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# --- PHYSIQUE ET JEU ---
FPS = 60
GRAVITY = 0.7

# --- PARAMÈTRES DU JOUEUR ---
PLAYER_SPEED = 4
JUMP_STRENGTH = -19
BOUNCE_STRENGTH = -10

# --- COULEURS (pour les boutons et textes) ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BUTTON_BASE_COLOR = (100, 100, 100)
BUTTON_HOVER_COLOR = (150, 150, 150)
BUTTON_LOCKED_COLOR = (50, 50, 50)

# --- CHEMINS D'ACCÈS ---
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.join(SCRIPT_DIR, "assets")
SOUNDS_PATH = os.path.join(SCRIPT_DIR, "sounds")
SAVE_FILE = os.path.join(SCRIPT_DIR, "save.dat")
