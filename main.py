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
player_width = 50
player_height = 50
player_x = (screen_width - player_width) / 2
player_y = screen_height - player_height # Commence au sol
player_color = (255, 0, 0) # Rouge
player_speed = 5

# Physique du joueur
gravity = 1
jump_strength = -20
player_y_velocity = 0
is_on_ground = True

# Boucle principale du jeu
running = True
while running:
    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Gestion du saut (sur un événement pour éviter les répétitions)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and is_on_ground:
                player_y_velocity = jump_strength
                is_on_ground = False

    # Gestion des touches maintenues enfoncées pour le mouvement horizontal
    keys = pygame.key.get_pressed()
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

    # Simuler le sol
    if player_y >= screen_height - player_height:
        player_y = screen_height - player_height
        player_y_velocity = 0
        is_on_ground = True

    # Remplissage de l'écran avec une couleur (noir)
    screen.fill((0, 0, 0))

    # Dessiner le joueur
    pygame.draw.rect(screen, player_color, (player_x, player_y, player_width, player_height))

    # Mise à jour de l'affichage
    pygame.display.flip()

# Quitter Pygame
pygame.quit()
