import pygame

# Initialisation de Pygame
pygame.init()

# Définition des dimensions de la fenêtre
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Titre de la fenêtre
pygame.display.set_caption("Jeu de Plateforme")

# Horloge pour contrôler le FPS
clock = pygame.time.Clock()
FPS = 60

# --- ÉLÉMENTS DU JEU ---

# Joueur
player_width = 40
player_height = 50
player_start_pos = ((screen_width - player_width) / 2, 0)
player_rect = pygame.Rect(player_start_pos[0], player_start_pos[1], player_width, player_height)
player_color = (255, 0, 0)
player_speed = 4
gravity = 0.8
jump_strength = -18
player_y_velocity = 0

# Plateformes
platforms_data = [
    (0, screen_height - 40, screen_width, 40), # Le sol
    (200, 450, 150, 20),
    (450, 350, 100, 20),
    (100, 250, 100, 20)
]
platform_rects = [pygame.Rect(p[0], p[1], p[2], p[3]) for p in platforms_data]
platform_color = (0, 255, 0)

# Pièce
coin_size = 30
coin_start_pos = (125, 250 - coin_size)
coin_rect = pygame.Rect(coin_start_pos[0], coin_start_pos[1], coin_size, coin_size)
coin_color = (255, 223, 0)

# Police et messages
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)
win_text = font.render("Gagné !", True, (255, 255, 255))
lose_text = font.render("Perdu !", True, (255, 255, 255))
restart_text = small_font.render("Appuyez sur R pour recommencer", True, (255, 255, 255))
win_text_rect = win_text.get_rect(center=(screen_width / 2, screen_height / 2 - 20))
lose_text_rect = lose_text.get_rect(center=(screen_width / 2, screen_height / 2 - 20))
restart_text_rect = restart_text.get_rect(center=(screen_width / 2, screen_height / 2 + 30))

# --- VARIABLES D'ÉTAT DU JEU ---
game_state = "playing" # Peut être "playing", "won", "lost"

def reset_game():
    global player_y_velocity, game_state
    player_rect.topleft = player_start_pos
    coin_rect.topleft = coin_start_pos
    player_y_velocity = 0
    game_state = "playing"

# --- BOUCLE PRINCIPALE ---
running = True
while running:
    clock.tick(FPS)

    # --- GESTION DES ÉVÉNEMENTS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: # Touche R pour recommencer
                if game_state in ["won", "lost"]:
                    reset_game()

    # --- LOGIQUE DU JEU ---
    if game_state == "playing":
        keys = pygame.key.get_pressed()

        # Mouvement Horizontal
        if keys[pygame.K_LEFT]: player_rect.x -= player_speed
        if keys[pygame.K_RIGHT]: player_rect.x += player_speed

        if player_rect.left < 0: player_rect.left = 0
        if player_rect.right > screen_width: player_rect.right = screen_width

        # Mouvement Vertical et Collisions
        player_y_velocity += gravity
        player_rect.y += player_y_velocity

        is_on_ground = False
        for plat_rect in platform_rects:
            if player_rect.colliderect(plat_rect) and player_y_velocity > 0:
                player_rect.bottom = plat_rect.top
                player_y_velocity = 0
                is_on_ground = True
                break

        # Saut
        if keys[pygame.K_SPACE] and is_on_ground:
            player_y_velocity = jump_strength

        # Condition de défaite (tomber dans le vide)
        if player_rect.top > screen_height:
            game_state = "lost"

        # Condition de victoire (collecter la pièce)
        if player_rect.colliderect(coin_rect):
            game_state = "won"

    # --- DESSIN ---
    screen.fill((0, 0, 0))

    for plat_rect in platform_rects:
        pygame.draw.rect(screen, platform_color, plat_rect)

    if game_state != "won": # Ne pas dessiner la pièce si on a déjà gagné
        pygame.draw.rect(screen, coin_color, coin_rect)

    pygame.draw.rect(screen, player_color, player_rect)

    # Affichage des messages de fin de partie
    if game_state == "won":
        screen.blit(win_text, win_text_rect)
        screen.blit(restart_text, restart_text_rect)
    elif game_state == "lost":
        screen.blit(lose_text, lose_text_rect)
        screen.blit(restart_text, restart_text_rect)

    pygame.display.flip()

pygame.quit()
