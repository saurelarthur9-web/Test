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
# Position initiale au centre de l'écran
player_x = (screen_width - player_width) / 2
player_y = screen_height - player_height - 50 # Un peu au-dessus du bas
player_color = (255, 0, 0) # Rouge
player_speed = 5

# Boucle principale du jeu
running = True
while running:
    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Gestion des touches maintenues enfoncées pour un mouvement continu
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed

    # Empêcher le joueur de sortir de l'écran
    if player_x < 0:
        player_x = 0
    if player_x > screen_width - player_width:
        player_x = screen_width - player_width

    # Remplissage de l'écran avec une couleur (noir)
    screen.fill((0, 0, 0))

    # Dessiner le joueur
    pygame.draw.rect(screen, player_color, (player_x, player_y, player_width, player_height))

    # Mise à jour de l'affichage
    pygame.display.flip()

# Quitter Pygame
pygame.quit()
