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

# Définition du joueur
player_width = 40
player_height = 50
# On utilise directement le Rect pour la position
player_rect = pygame.Rect(
    (screen_width - player_width) / 2,
    0, # Le joueur commence en haut de l'écran
    player_width,
    player_height
)
player_color = (255, 0, 0) # Rouge
player_speed = 4

# Physique du joueur
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
platform_color = (0, 255, 0) # Vert

# Boucle principale du jeu
running = True
while running:
    # Réguler le FPS
    clock.tick(FPS)

    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Le saut est maintenant géré avec `get_pressed` pour plus de réactivité

    # --- LOGIQUE DU JEU ---

    # Gestion du clavier
    keys = pygame.key.get_pressed()

    # --- Mouvement Horizontal ---
    if keys[pygame.K_LEFT]:
        player_rect.x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_rect.x += player_speed

    # Empêcher le joueur de sortir de l'écran (horizontalement)
    if player_rect.left < 0:
        player_rect.left = 0
    if player_rect.right > screen_width:
        player_rect.right = screen_width

    # --- Mouvement Vertical et Collisions ---
    # Appliquer la gravité
    player_y_velocity += gravity
    player_rect.y += player_y_velocity

    is_on_ground = False
    # Vérifier les collisions avec les plateformes après le mouvement vertical
    for plat_rect in platform_rects:
        # Est-ce qu'il y a collision ?
        if player_rect.colliderect(plat_rect):
            # Si le joueur est en train de tomber (vitesse vers le bas)
            if player_y_velocity > 0:
                # On replace le joueur sur le dessus de la plateforme
                player_rect.bottom = plat_rect.top
                player_y_velocity = 0
                is_on_ground = True
                break # On ne traite qu'une seule collision à la fois

    # --- Saut ---
    if keys[pygame.K_SPACE] and is_on_ground:
        player_y_velocity = jump_strength

    # --- DESSIN ---

    # Remplissage de l'écran
    screen.fill((0, 0, 0)) # Noir

    # Dessiner les plateformes
    for plat_rect in platform_rects:
        pygame.draw.rect(screen, platform_color, plat_rect)

    # Dessiner le joueur
    pygame.draw.rect(screen, player_color, player_rect)

    # Mise à jour de l'affichage
    pygame.display.flip()

# Quitter Pygame
pygame.quit()
