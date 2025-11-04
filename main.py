import pygame
import os

# --- INITIALISATION ---
pygame.init()
try:
    pygame.mixer.init()
except pygame.error as e:
    print(f"Avertissement: Impossible d'initialiser le mixer audio : {e}")

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Loris L'Astronaute") # Titre de la fenêtre mis à jour

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
    try: return pygame.mixer.Sound(filepath)
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
enemy_image = load_image_or_create_fallback("enemy.png", (40, 40), (150, 0, 255))
background_image = load_image_or_create_fallback("background.png", (screen_width, screen_height), (0, 0, 0), True)
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

jump_sound = load_sound_or_dummy("jump.ogg"); coin_sound = load_sound_or_dummy("coin.ogg"); enemy_stomp_sound = load_sound_or_dummy("stomp.ogg")
try:
    pygame.mixer.music.load(os.path.join(sounds_path, "music.mp3"))
    pygame.mixer.music.play(-1)
except pygame.error:
    print("Avertissement: La musique 'music.mp3' n'a pas été trouvée.")

# --- CLASSES DU JEU ---
class Enemy:
    def __init__(self, x, y, speed, patrol_range):
        self.image = enemy_image; self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed; self.direction = 1; self.start_x = x; self.patrol_range = patrol_range
    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.x <= self.start_x or self.rect.x >= self.start_x + self.patrol_range: self.direction *= -1
    def draw(self, surface): surface.blit(self.image, self.rect)

class Button:
    def __init__(self, x, y, width, height, text, font, base_color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.current_color = base_color

    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=10)
        text_width, text_height = self.font.size(self.text)
        draw_text_with_outline(surface, self.text, self.font,
                               (self.rect.centerx - text_width / 2,
                                self.rect.centery - text_height / 2),
                               (255, 255, 255), (0, 0, 0))

    def check_hover(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
        else:
            self.current_color = self.base_color

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

# --- STRUCTURE DES NIVEAUX ---
levels = [
    {"platforms": [(0, 560, 800, 40), (200, 450, 160, 40), (450, 350, 120, 40), (150, 250, 120, 40)], "coins": [(475, 320), (250, 420), (175, 220)], "enemies": [(220, 410, 2, 100)]},
    {"platforms": [(0, 560, 800, 40), (100, 480, 120, 40), (300, 380, 120, 40), (500, 280, 120, 40), (250, 180, 120, 40)], "coins": [(130, 450), (330, 350), (530, 250), (280, 150)], "enemies": [(110, 440, 2, 80), (310, 340, 3, 80)]}
]

# --- VARIABLES DU JEU ---
player_hitbox = pygame.Rect(380, 0, 25, 45); player_speed = 4; gravity = 0.7; jump_strength = -19; player_y_velocity = 0; is_on_ground = False
bounce_strength = -10
platform_rects = []; coin_rects = []; enemies = []
score = 0; current_level_index = 0; start_time = 0; elapsed_time = 0
font = pygame.font.Font(None, 74); big_font = pygame.font.Font(None, 80) ; small_font = pygame.font.Font(None, 36); score_font = pygame.font.Font(None, 40)
game_state = "start_screen"

# --- Création des boutons ---
button_font = pygame.font.Font(None, 50)
play_button = Button(300, 250, 200, 50, "Jouer", button_font, (100, 100, 100), (150, 150, 150))
credits_button = Button(300, 320, 200, 50, "Crédits", button_font, (100, 100, 100), (150, 150, 150))
back_button = Button(300, 500, 200, 50, "Retour", button_font, (100, 100, 100), (150, 150, 150))
restart_button = Button(300, 250, 200, 50, "Recommencer", button_font, (100, 100, 100), (150, 150, 150))
main_menu_button = Button(300, 320, 200, 50, "Menu Principal", button_font, (100, 100, 100), (150, 150, 150))

def load_level(level_index):
    global platform_rects, coin_rects, enemies, player_y_velocity
    level_data = levels[level_index]
    platform_rects = [pygame.Rect(p[0], p[1], p[2], p[3]) for p in level_data["platforms"]]
    coin_rects = [coin_image.get_rect(topleft=pos) for pos in level_data["coins"]]
    enemies = [Enemy(e[0], e[1], e[2], e[3]) for e in level_data["enemies"]]
    player_hitbox.topleft = (380, 0); player_y_velocity = 0

def reset_game():
    global game_state, score, current_level_index, start_time
    score = 0; current_level_index = 0; load_level(0); game_state = "playing"
    start_time = pygame.time.get_ticks()

# --- BOUCLE PRINCIPALE ---
running = True
while running:
    clock.tick(FPS)
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

        if game_state == "start_screen":
            if play_button.check_click(event):
                reset_game()
            if credits_button.check_click(event):
                game_state = "credits_screen"
        elif game_state == "credits_screen":
            if back_button.check_click(event):
                game_state = "start_screen"
        elif game_state == "game_over":
            if restart_button.check_click(event):
                load_level(current_level_index)
                game_state = "playing"
            if main_menu_button.check_click(event):
                game_state = "start_screen"

        if event.type == pygame.KEYDOWN:
            if game_state == "won" and event.key == pygame.K_r:
                reset_game()

    if game_state == "playing":
        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
        keys = pygame.key.get_pressed()

        player_hitbox.x += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * player_speed
        for plat_rect in platform_rects:
            if player_hitbox.colliderect(plat_rect):
                if (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) > 0: player_hitbox.right = plat_rect.left
                elif (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) < 0: player_hitbox.left = plat_rect.right

        if keys[pygame.K_SPACE] and is_on_ground:
            player_y_velocity = jump_strength; jump_sound.play()

        player_y_velocity += gravity
        player_hitbox.y += player_y_velocity
        is_on_ground = False
        for plat_rect in platform_rects:
            if player_hitbox.colliderect(plat_rect):
                if player_y_velocity > 0:
                    player_hitbox.bottom = plat_rect.top; is_on_ground = True; player_y_velocity = 0
                elif player_y_velocity < 0:
                    player_hitbox.top = plat_rect.bottom; player_y_velocity = 0

        for i, enemy in reversed(list(enumerate(enemies))):
            enemy.update()
            if player_hitbox.colliderect(enemy.rect):
                if player_y_velocity > 0 and player_hitbox.bottom < enemy.rect.centery:
                    enemies.pop(i); enemy_stomp_sound.play(); player_y_velocity = bounce_strength
                else: game_state = "game_over"

        coin_index = player_hitbox.collidelist(coin_rects)
        if coin_index != -1:
            coin_rects.pop(coin_index); score += 1; coin_sound.play()

        if player_hitbox.top > screen_height: game_state = "game_over"

        if not coin_rects:
            current_level_index += 1
            if current_level_index < len(levels): load_level(current_level_index)
            else: game_state = "won"

    # --- DESSIN ---
    screen.blit(background_image, (0, 0))
    if game_state == "start_screen":
        title_rect = big_font.render("Loris L'Astronaute", True, (0,0,0)).get_rect(center=(screen_width / 2, screen_height / 2 - 100))
        draw_text_with_outline(screen, "Loris L'Astronaute", big_font, title_rect.topleft, (255, 255, 255), (0, 0, 0))

        play_button.check_hover(mouse_pos)
        play_button.draw(screen)
        credits_button.check_hover(mouse_pos)
        credits_button.draw(screen)

    elif game_state == "credits_screen":
        credits_title_rect = big_font.render("Crédits", True, (0,0,0)).get_rect(center=(screen_width / 2, 100))
        draw_text_with_outline(screen, "Crédits", big_font, credits_title_rect.topleft, (255, 255, 255), (0, 0, 0))

        credits_text = [
            "Jeu développé par : Vous !",
            "Idée originale : Loris",
            "Moteur de jeu : Pygame"
        ]

        for i, line in enumerate(credits_text):
            line_rect = small_font.render(line, True, (0,0,0)).get_rect(center=(screen_width / 2, 250 + i * 40))
            draw_text_with_outline(screen, line, small_font, line_rect.topleft, (255, 255, 255), (0, 0, 0))

        back_button.check_hover(mouse_pos)
        back_button.draw(screen)

    elif game_state == "playing":
        for plat_rect in platform_rects:
            for x in range(plat_rect.left, plat_rect.right, platform_image.get_width()):
                screen.blit(platform_image, (x, plat_rect.top))
        for coin in coin_rects: screen.blit(coin_image, coin)
        for enemy in enemies: enemy.draw(screen)

        image_rect = player_image.get_rect(centerx=player_hitbox.centerx, bottom=player_hitbox.bottom)
        screen.blit(player_image, image_rect)

        draw_text_with_outline(screen, f"Score: {score}", score_font, (10, 10), (255,255,255), (0,0,0))
        draw_text_with_outline(screen, f"Niveau: {current_level_index + 1}", score_font, (screen_width - 150, 10), (255,255,255), (0,0,0))
        timer_text = f"Temps: {elapsed_time}"; timer_rect = score_font.render(timer_text, True, (0,0,0)).get_rect(centerx=screen_width/2); timer_rect.top = 10
        draw_text_with_outline(screen, timer_text, score_font, timer_rect.topleft, (255,255,255), (0,0,0))

    elif game_state == "game_over":
        game_over_rect = big_font.render("Game Over", True, (0,0,0)).get_rect(center=(screen_width / 2, screen_height / 2 - 100))
        draw_text_with_outline(screen, "Game Over", big_font, game_over_rect.topleft, (255, 0, 0), (0, 0, 0))

        restart_button.check_hover(mouse_pos)
        restart_button.draw(screen)
        main_menu_button.check_hover(mouse_pos)
        main_menu_button.draw(screen)

    elif game_state == "won":
        win_rect = font.render("Gagné !", True, (0,0,0)).get_rect(center=(screen_width / 2, screen_height / 2 - 20))
        draw_text_with_outline(screen, "Gagné !", font, win_rect.topleft, (255, 255, 255), (0, 0, 0))
        final_time_text = f"Votre temps: {elapsed_time}s"
        final_time_rect = small_font.render(final_time_text, True, (0,0,0)).get_rect(center=(screen_width / 2, screen_height / 2 + 30))
        draw_text_with_outline(screen, final_time_text, small_font, final_time_rect.topleft, (255, 255, 255), (0, 0, 0))
        restart_rect = small_font.render("Appuyez sur R pour recommencer", True, (0,0,0)).get_rect(center=(screen_width / 2, screen_height / 2 + 70))
        draw_text_with_outline(screen, "Appuyez sur R pour recommencer", small_font, restart_rect.topleft, (255,255,255), (0,0,0))

    pygame.display.flip()
pygame.quit()
