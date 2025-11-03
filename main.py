import pygame

# Initialisation de Pygame
pygame.init()

# Définition des dimensions de la fenêtre
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Titre de la fenêtre
pygame.display.set_caption("Jeu de Plateforme")

# Définition du joueur
player_width = 40
player_height = 50
player_x = (screen_width - player_width) / 2
player_y = 0 # Commence en haut pour tomber sur les plateformes
player_color = (255, 0, 0) # Rouge
player_speed = 5
# On utilise un Rect pour faciliter la détection de collision
player_rect = pygame.Rect(player_x, player_y, player_width, player_height)

# Physique du joueur
gravity = 1
jump_strength = -20
player_y_velocity = 0

# Plateformes
# Le sol est maintenant juste une autre plateforme
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
    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- LOGIQUE DU JEU ---

    # Gestion du clavier
    keys = pygame.key.get_pressed()

    # Mouvement horizontal
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed

    # Empêcher le joueur de sortir de l'écran (horizontalement)
    if player_x < 0:
        player_x = 0
    if player_x > screen_width - player_width:
        player_x = screen_width - player_width

    # Appliquer la gravité
    player_y_velocity += gravity
    player_y += player_y_velocity

    # Mettre à jour le rect du joueur pour la collision
    player_rect.topleft = (player_x, player_y)

    # Gestion des collisions avec les plateformes
    is_on_ground = False
    for plat_rect in platform_rects:
        # Est-ce que le joueur touche la plateforme ET est-il en train de tomber?
        if player_rect.colliderect(plat_rect) and player_y_velocity > 0:
            # On vérifie que le bas du joueur est bien au-dessus du haut de la plateforme avant la collision
            # pour s'assurer qu'on atterrit bien DESSUS.
            if player_rect.bottom - player_y_velocity <= plat_rect.top:
                player_rect.bottom = plat_rect.top
                player_y = player_rect.y # On met à jour la variable y
                player_y_velocity = 0
                is_on_ground = True
                break # Une seule plateforme à la fois

    # Gestion du saut (uniquement si le joueur est au sol)
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
