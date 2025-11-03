import pygame
import os

# --- INITIALISATION ---
pygame.init()
pygame.mixer.init()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Jeu de Plateforme")

clock = pygame.time.Clock()
FPS = 60

# --- CHEMINS D'ACCÈS ABSOLUS ---
script_dir = os.path.dirname(os.path.abspath(__file__))
assets_path = os.path.join(script_dir, "assets")
sounds_path = os.path.join(script_dir, "sounds")

# --- FONCTIONS UTILITAIRES ---
def load_image_or_create_fallback(filename, size, color, is_background=False):
    filepath = os.path.join(assets_path, filename)
    try:
        image = pygame.image.load(filepath)
        if is_background: return image.convert()
        else: return image.convert_alpha()
    except (pygame.error, FileNotFoundError):
        print(f"Avertissement: L'image '{filename}' n'a pas été trouvée. Placeholder utilisé.")
        surface = pygame.Surface(size); surface.fill(color)
        return surface

def load_sound_or_dummy(filename):
    filepath = os.path.join(sounds_path, filename)
    try:
        return pygame.mixer.Sound(filepath)
    except (pygame.error, FileNotFoundError):
        print(f"Avertissement: Le son '{filename}' n'a pas été trouvé.")
        class DummySound:
            def play(self): pass
        return DummySound()

def draw_text_with_outline(surface, text, font, pos, text_color, outline_color):
    x, y = pos; outline_thickness = 2
    outline_surface = font.render(text, True, outline_color)
    for dx in range(-outline_thickness, outline_thickness + 1):
        for dy in range(-outline_thickness, outline_thickness + 1):
            if dx != 0 or dy != 0: surface.blit(outline_surface, (x + dx, y + dy))
    text_surface = font.render(text, True, text_color); surface.blit(text_surface, pos)

# --- CHARGEMENT DES ASSETS ET SONS ---
player_image = load_image_or_create_fallback("player.png", (40, 50), (255, 0, 0))
platform_image = load_image_or_create_fallback("platform.png", (40, 40), (0, 255, 0))
coin_image = load_image_or_create_fallback("coin.png", (30, 30), (255, 223, 0))
background_image = load_image_or_create_fallback("background.png", (screen_width, screen_height), (0, 0, 0), True)
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

jump_sound = load_sound_or_dummy("jump.ogg") # Mise à jour en .ogg
coin_sound = load_sound_or_dummy("coin.ogg") # Mise à jour en .ogg
try:
    pygame.mixer.music.load(os.path.join(sounds_path, "music.mp3"))
    pygame.mixer.music.play(-1)
except pygame.error:
    print("Avertissement: La musique 'music.mp3' n'a pas été trouvée.")

# --- ÉLÉMENTS DU JEU ---
player_rect = player_image.get_rect(topleft=((screen_width - player_image.get_width()) / 2, 0))
player_speed = 4; gravity = 0.8; jump_strength = -18; player_y_velocity = 0

platforms_data = [(0, screen_height - 40, screen_width, 40), (200, 450, 160, 40), (450, 350, 120, 40), (100, 250, 120, 40)]
platform_rects = [pygame.Rect(p[0], p[1], p[2], p[3]) for p in platforms_data]

# Pièces (plusieurs maintenant)
coin_start_positions = [(125, 220), (250, 420), (485, 320)]
coin_rects = []

# Score
score = 0
score_font = pygame.font.Font(None, 40)

# Polices de fin de partie
font = pygame.font.Font(None, 74); small_font = pygame.font.Font(None, 36)
game_state = "playing"

def reset_game():
    global player_y_velocity, game_state, score, coin_rects
    player_rect.topleft = ((screen_width - player_rect.width) / 2, 0)
    player_y_velocity = 0
    score = 0
    # Recréer la liste des pièces
    coin_rects = [coin_image.get_rect(topleft=pos) for pos in coin_start_positions]
    game_state = "playing"

# Initialisation du premier jeu
reset_game()

# --- BOUCLE PRINCIPALE ---
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
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
                player_y_velocity = 0; is_on_ground = True; break

        if keys[pygame.K_SPACE] and is_on_ground:
            player_y_velocity = jump_strength
            jump_sound.play()

        # Collision avec les pièces
        coin_index = player_rect.collidelist(coin_rects)
        if coin_index != -1:
            coin_rects.pop(coin_index)
            score += 1
            coin_sound.play()

        if player_rect.top > screen_height: game_state = "lost"
        # Condition de victoire: toutes les pièces sont collectées
        if not coin_rects:
            game_state = "won"

    # --- DESSIN ---
    screen.blit(background_image, (0, 0))
    if game_state == "playing":
        for plat_rect in platform_rects:
            for x in range(plat_rect.left, plat_rect.right, platform_image.get_width()):
                screen.blit(platform_image, (x, plat_rect.top))

        for coin in coin_rects:
            screen.blit(coin_image, coin)

        screen.blit(player_image, player_rect)
        # Afficher le score
        draw_text_with_outline(screen, f"Score: {score}", score_font, (10, 10), (255, 255, 255), (0, 0, 0))

    elif game_state == "won":
        win_rect = font.render("Gagné !", True, (0,0,0)).get_rect(center=(screen_width / 2, screen_height / 2 - 20))
        draw_text_with_outline(screen, "Gagné !", font, win_rect.topleft, (255, 255, 255), (0, 0, 0))
        restart_rect = small_font.render("Appuyez sur R pour recommencer", True, (0,0,0)).get_rect(center=(screen_width / 2, screen_height / 2 + 30))
        draw_text_with_outline(screen, "Appuyez sur R pour recommencer", small_font, restart_rect.topleft, (255, 255, 255), (0, 0, 0))
    elif game_state == "lost":
        lose_rect = font.render("Perdu !", True, (0,0,0)).get_rect(center=(screen_width / 2, screen_height / 2 - 20))
        draw_text_with_outline(screen, "Perdu !", font, lose_rect.topleft, (255, 255, 255), (0, 0, 0))
        restart_rect = small_font.render("Appuyez sur R pour recommencer", True, (0,0,0)).get_rect(center=(screen_width / 2, screen_height / 2 + 30))
        draw_text_with_outline(screen, "Appuyez sur R pour recommencer", small_font, restart_rect.topleft, (255, 255, 255), (0, 0, 0))

    pygame.display.flip()
pygame.quit()
