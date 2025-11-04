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

jump_sound = load_sound_or_dummy("jump.ogg")
coin_sound = load_sound_or_dummy("coin.ogg")
try:
    pygame.mixer.music.load(os.path.join(sounds_path, "music.mp3"))
    pygame.mixer.music.play(-1)
except pygame.error:
    print("Avertissement: La musique 'music.mp3' n'a pas été trouvée.")

# --- STRUCTURE DES NIVEAUX ---
levels = [
    { # Niveau 1
        "platforms": [(0, 560, 800, 40), (200, 450, 160, 40), (450, 350, 120, 40), (100, 250, 120, 40)],
        "coins": [(475, 320), (250, 420), (125, 220)] # Position de la pièce ajustée
    },
    { # Niveau 2
        "platforms": [(0, 560, 800, 40), (100, 480, 120, 40), (300, 380, 120, 40), (500, 280, 120, 40), (250, 180, 120, 40)],
        "coins": [(130, 450), (330, 350), (530, 250), (280, 150)]
    }
]

# --- VARIABLES DU JEU ---
player_hitbox = pygame.Rect(380, 0, 25, 45)
player_speed = 4; gravity = 0.8; jump_strength = -18; player_y_velocity = 0; is_on_ground = False
platform_rects = []; coin_rects = []
score = 0; current_level_index = 0
start_time = 0; elapsed_time = 0
font = pygame.font.Font(None, 74); small_font = pygame.font.Font(None, 36); score_font = pygame.font.Font(None, 40)
game_state = "menu"

def load_level(level_index):
    global platform_rects, coin_rects, player_y_velocity, start_time
    level_data = levels[level_index]
    platform_rects = [pygame.Rect(p[0], p[1], p[2], p[3]) for p in level_data["platforms"]]
    coin_rects = [coin_image.get_rect(topleft=pos) for pos in level_data["coins"]]
    player_hitbox.topleft = (380, 0); player_y_velocity = 0
    start_time = pygame.time.get_ticks() # Réinitialise le timer

def reset_game():
    global game_state, score, current_level_index
    score = 0; current_level_index = 0; load_level(0); game_state = "playing"

def main_menu():
    menu_font = pygame.font.Font(None, 100)
    button_font = pygame.font.Font(None, 50)

    title_rect = menu_font.render("Platformer", True, (0,0,0)).get_rect(center=(screen_width / 2, screen_height / 2 - 100))
    play_button = pygame.Rect(screen_width / 2 - 100, screen_height / 2, 200, 50)
    quit_button = pygame.Rect(screen_width / 2 - 100, screen_height / 2 + 70, 200, 50)

    menu_running = True
    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    return "playing"
                if quit_button.collidepoint(event.pos):
                    return "quit"

        screen.blit(background_image, (0, 0))

        draw_text_with_outline(screen, "Platformer", menu_font, title_rect.topleft, (255, 255, 255), (0, 0, 0))

        pygame.draw.rect(screen, (0, 200, 0), play_button)
        pygame.draw.rect(screen, (200, 0, 0), quit_button)

        play_text_rect = button_font.render("Jouer", True, (0,0,0)).get_rect(center=play_button.center)
        draw_text_with_outline(screen, "Jouer", button_font, play_text_rect.topleft, (255, 255, 255), (0, 0, 0))

        quit_text_rect = button_font.render("Quitter", True, (0,0,0)).get_rect(center=quit_button.center)
        draw_text_with_outline(screen, "Quitter", button_font, quit_text_rect.topleft, (255, 255, 255), (0, 0, 0))

        pygame.display.flip()
        clock.tick(FPS)

# --- BOUCLE PRINCIPALE ---
running = True
while running:
    if game_state == "menu":
        game_state = main_menu()
        if game_state == "quit":
            running = False
        elif game_state == "playing":
            reset_game()

    if not running:
        break

    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r and game_state in ["won", "lost"]:
            reset_game()

    if game_state == "playing":
        # Mise à jour du timer
        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000

        keys = pygame.key.get_pressed()
        player_hitbox.x += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * player_speed
        for plat_rect in platform_rects:
            if player_hitbox.colliderect(plat_rect):
                if (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) > 0: player_hitbox.right = plat_rect.left
                elif (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) < 0: player_hitbox.left = plat_rect.right

        if keys[pygame.K_SPACE] and is_on_ground:
            player_y_velocity = jump_strength
            jump_sound.play()

        player_y_velocity += gravity
        player_hitbox.y += player_y_velocity
        is_on_ground = False
        for plat_rect in platform_rects:
            if player_hitbox.colliderect(plat_rect):
                if player_y_velocity > 0:
                    player_hitbox.bottom = plat_rect.top
                    is_on_ground = True
                    player_y_velocity = 0
                elif player_y_velocity < 0:
                    player_hitbox.top = plat_rect.bottom
                    player_y_velocity = 0

        coin_index = player_hitbox.collidelist(coin_rects)
        if coin_index != -1:
            coin_rects.pop(coin_index); score += 1; coin_sound.play()

        if player_hitbox.top > screen_height: load_level(current_level_index)

        if not coin_rects:
            current_level_index += 1
            if current_level_index < len(levels):
                load_level(current_level_index)
            else:
                game_state = "menu"

    # --- DESSIN ---
    screen.blit(background_image, (0, 0))
    if game_state == "playing":
        for plat_rect in platform_rects:
            for x in range(plat_rect.left, plat_rect.right, platform_image.get_width()):
                screen.blit(platform_image, (x, plat_rect.top))
        for coin in coin_rects: screen.blit(coin_image, coin)

        image_rect = player_image.get_rect(centerx=player_hitbox.centerx, bottom=player_hitbox.bottom)
        screen.blit(player_image, image_rect)

        draw_text_with_outline(screen, f"Score: {score}", score_font, (10, 10), (255, 255, 255), (0, 0, 0))
        draw_text_with_outline(screen, f"Niveau: {current_level_index + 1}", score_font, (screen_width - 150, 10), (255, 255, 255), (0, 0, 0))

        # Afficher le timer
        timer_text = f"Temps: {elapsed_time}"
        timer_rect = score_font.render(timer_text, True, (0,0,0)).get_rect(centerx=screen_width/2)
        timer_rect.top = 10
        draw_text_with_outline(screen, timer_text, score_font, timer_rect.topleft, (255, 255, 255), (0, 0, 0))

    elif game_state == "won":
        win_rect = font.render("Gagné !", True, (0,0,0)).get_rect(center=(screen_width / 2, screen_height / 2 - 20))
        draw_text_with_outline(screen, "Gagné !", font, win_rect.topleft, (255, 255, 255), (0, 0, 0))
        restart_rect = small_font.render("Appuyez sur R pour recommencer", True, (0,0,0)).get_rect(center=(screen_width / 2, screen_height / 2 + 30))
        draw_text_with_outline(screen, "Appuyez sur R pour recommencer", small_font, restart_rect.topleft, (255, 255, 255), (0, 0, 0))

    pygame.display.flip()
pygame.quit()
