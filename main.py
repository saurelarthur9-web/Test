import pygame

# Initialisation de Pygame
pygame.init()

# Définition des dimensions de la fenêtre
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Titre de la fenêtre
pygame.display.set_caption("Jeu de Plateforme")

# Boucle principale du jeu
running = True
while running:
    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Remplissage de l'écran avec une couleur (noir)
    screen.fill((0, 0, 0))

    # Mise à jour de l'affichage
    pygame.display.flip()

# Quitter Pygame
pygame.quit()
