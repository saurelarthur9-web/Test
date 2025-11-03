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
player_rect = pygame.Rect(
    (screen_width - player_width) / 2, 0, player_width, player_height
)
player_color = (255, 0, 0)
player_speed = 4
gravity = 0.8
jump_strength = -18
player_y_velocity = 0
is_on_ground = False

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
coin_rect = pygame.Rect(125, 250 - coin_size, coin_size, coin_size)
coin_color = (255, 223, 0) # Jaune/Or
coin_collected = False

# Police et message de victoire
font = pygame.font.Font(None, 74) # Utilise la police par défaut de Pygame
win_text = font.render("Gagné !", True, (255, 255, 255)) # Texte blanc
win_text_rect = win_text.get_rect(center=(screen_width / 2, screen_height / 2))

# --- BOUCLE PRINCIPALE ---
running = True
while running:
    clock.tick(FPS)

    # --- GESTION DES ÉVÉNEMENTS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- LOGIQUE DU JEU (seulement si le jeu n'est pas gagné) ---
    if not coin_collected:
        keys = pygame.key.get_pressed()

        # Mouvement Horizontal
        if keys[pygame.K_LEFT]:
            player_rect.x -= player_speed
        if keys[pygame.K_RIGHT]:
            player_rect.x += player_speed

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

        # Collision avec la pièce
        if player_rect.colliderect(coin_rect):
            coin_collected = True

    # --- DESSIN ---
    screen.fill((0, 0, 0))

    # Dessiner les plateformes
    for plat_rect in platform_rects:
        pygame.draw.rect(screen, platform_color, plat_rect)

    # Dessiner la pièce si elle n'est pas collectée
    if not coin_collected:
        pygame.draw.rect(screen, coin_color, coin_rect)

    # Dessiner le joueur
    pygame.draw.rect(screen, player_color, player_rect)

    # Afficher le message de victoire si la pièce est collectée
    if coin_collected:
        screen.blit(win_text, win_text_rect)

    pygame.display.flip()

pygame.quit()
