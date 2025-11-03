import pygame
import os

# --- INITIALISATION ---
pygame.init()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Jeu de Plateforme")

clock = pygame.time.Clock()
FPS = 60

# --- CHEMIN D'ACCÈS ABSOLU AUX ASSETS (pour plus de robustesse) ---
# Trouve le dossier dans lequel se trouve le script (main.py)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construit le chemin vers le dossier 'assets'
assets_path = os.path.join(script_dir, "assets")


# --- FONCTION DE CHARGEMENT SÉCURISÉE ---
def load_image_or_create_fallback(filename, size, color, is_background=False):
    """
    Tente de charger une image depuis le dossier 'assets' en utilisant un chemin absolu.
    Si l'image n'est pas trouvée, crée une surface de couleur unie à la place.
    """
    filepath = os.path.join(assets_path, filename)
    try:
        image = pygame.image.load(filepath)
        if is_background:
            return image.convert()
        else:
            return image.convert_alpha()
    except (pygame.error, FileNotFoundError):
        print(f"Avertissement: L'image '{filename}' n'a pas été trouvée. Utilisation d'un placeholder.")
        surface = pygame.Surface(size)
        surface.fill(color)
        return surface

# --- CHARGEMENT DES ASSETS ---
player_size = (40, 50)
platform_size = (100, 20)
coin_size = (30, 30)
background_size = (screen_width, screen_height)

player_image = load_image_or_create_fallback("player.png", player_size, (255, 0, 0))
platform_image = load_image_or_create_fallback("platform.png", platform_size, (0, 255, 0))
coin_image = load_image_or_create_fallback("coin.png", coin_size, (255, 223, 0))
background_image = load_image_or_create_fallback("background.png", background_size, (0, 0, 0), is_background=True)


# --- ÉLÉMENTS DU JEU ---
player_rect = player_image.get_rect(topleft=((screen_width - player_image.get_width()) / 2, 0))
player_speed = 4
gravity = 0.8
jump_strength = -18
player_y_velocity = 0

platforms_data = [(0, screen_height - 40, screen_width, 40), (200, 450, 150, 20), (450, 350, 100, 20), (100, 250, 100, 20)]
platform_rects = [pygame.Rect(p[0], p[1], p[2], p[3]) for p in platforms_data]

coin_rect = coin_image.get_rect(topleft=(125, 250 - coin_image.get_height()))

font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)
win_text = font.render("Gagné !", True, (255, 255, 255))
lose_text = font.render("Perdu !", True, (255, 255, 255))
restart_text = small_font.render("Appuyez sur R pour recommencer", True, (255, 255, 255))
win_text_rect = win_text.get_rect(center=(screen_width / 2, screen_height / 2 - 20))
lose_text_rect = lose_text.get_rect(center=(screen_width / 2, screen_height / 2 - 20))
restart_text_rect = restart_text.get_rect(center=(screen_width / 2, screen_height / 2 + 30))

game_state = "playing"

def reset_game():
    global player_y_velocity, game_state
    player_rect.topleft = ((screen_width - player_rect.width) / 2, 0)
    coin_rect.topleft = (125, 250 - coin_rect.height)
    player_y_velocity = 0
    game_state = "playing"

# --- BOUCLE PRINCIPALE ---
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r and game_state in ["won", "lost"]:
            reset_game()

    if game_state == "playing":
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]: player_rect.x -= player_speed
        if keys[pygame.K_RIGHT]: player_rect.x += player_speed

        if player_rect.left < 0: player_rect.left = 0
        if player_rect.right > screen_width: player_rect.right = screen_width

        player_y_velocity += gravity
        player_rect.y += player_y_velocity

        is_on_ground = False
        for plat_rect in platform_rects:
            if player_rect.colliderect(plat_rect) and player_y_velocity > 0:
                player_rect.bottom = plat_rect.top
                player_y_velocity = 0
                is_on_ground = True
                break

        if keys[pygame.K_SPACE] and is_on_ground:
            player_y_velocity = jump_strength

        if player_rect.top > screen_height: game_state = "lost"
        if player_rect.colliderect(coin_rect): game_state = "won"

    # --- DESSIN ---
    screen.blit(background_image, (0, 0))

    for plat_rect in platform_rects:
        scaled_platform = pygame.transform.scale(platform_image, (plat_rect.width, plat_rect.height))
        screen.blit(scaled_platform, plat_rect)

    if game_state != "won":
        screen.blit(coin_image, coin_rect)

    screen.blit(player_image, player_rect)

    if game_state == "won":
        screen.blit(win_text, win_text_rect)
        screen.blit(restart_text, restart_text_rect)
    elif game_state == "lost":
        screen.blit(lose_text, lose_text_rect)
        screen.blit(restart_text, restart_text_rect)

    pygame.display.flip()

pygame.quit()
