import pygame
from settings import *

class Player:
    def __init__(self, x, y, player_image, jump_sound):
        self.image = player_image
        # La hitbox est légèrement plus petite que l'image pour des collisions plus justes
        self.rect = pygame.Rect(x, y, 20, 42)
        self.y_velocity = 0
        self.is_on_ground = False
        self.jump_sound = jump_sound
        self.has_double_jump = False
        self.jumps_left = 0

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.jump()

    def jump(self):
        if self.is_on_ground:
            self.y_velocity = JUMP_STRENGTH
            self.jump_sound.play()
            if self.has_double_jump:
                self.jumps_left = 1
        elif self.has_double_jump and self.jumps_left > 0:
            self.y_velocity = JUMP_STRENGTH
            self.jump_sound.play()
            self.jumps_left = 0

    def update(self, keys, all_platforms, moving_platforms):
        # 1. Apply platform movement first if player is on a moving platform
        if self.is_on_ground:
            ground_platform = None
            for plat_rect in all_platforms:
                if self.rect.colliderect(plat_rect) and self.rect.bottom == plat_rect.top:
                    ground_platform = plat_rect
                    break

            if ground_platform:
                for p in moving_platforms:
                    if p.rect == ground_platform:
                        if p.move_direction == 'horizontal':
                            self.rect.x += p.speed * p.direction
                        else: # Gère le mouvement vertical de la plateforme
                            self.rect.y += p.speed * p.direction
                        break

        # 2. Handle horizontal movement from input
        move_x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * PLAYER_SPEED
        self.rect.x += move_x
        for plat_rect in all_platforms:
            if self.rect.colliderect(plat_rect):
                if move_x > 0: # Moving right
                    self.rect.right = plat_rect.left
                elif move_x < 0: # Moving left
                    self.rect.left = plat_rect.right

        # 3. Handle vertical movement (gravity)
        self.y_velocity += GRAVITY
        self.rect.y += self.y_velocity

        self.is_on_ground = False
        for plat_rect in all_platforms:
            if self.rect.colliderect(plat_rect):
                if self.y_velocity > 0:
                    self.rect.bottom = plat_rect.top
                    self.is_on_ground = True
                    self.y_velocity = 0
                    # Reset jumps when landing
                    if self.has_double_jump:
                        self.jumps_left = 1
                elif self.y_velocity < 0:
                    self.rect.top = plat_rect.bottom
                    self.y_velocity = 0

    def draw(self, surface):
        # Centre l'image sur la hitbox pour que le visuel corresponde à la physique
        image_rect = self.image.get_rect(midbottom=self.rect.midbottom)
        surface.blit(self.image, image_rect)

class Enemy:
    def __init__(self, x, y, speed, patrol_range, enemy_image, moving_platforms):
        self.image = enemy_image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed
        self.direction = 1
        self.patrol_range = patrol_range
        self.start_x = x
        self.y_velocity = 0
        self.is_on_ground = False
        self.moving_platforms = moving_platforms

    def update(self, platforms):
        # --- 1. Vertical Physics (Apply gravity and check for ground) ---
        self.y_velocity += GRAVITY
        self.rect.y += self.y_velocity
        self.is_on_ground = False

        for plat_rect in platforms:
            if self.rect.colliderect(plat_rect):
                if self.y_velocity > 0: # Moving down
                    self.rect.bottom = plat_rect.top
                    self.is_on_ground = True
                    self.y_velocity = 0
                elif self.y_velocity < 0: # Moving up
                    self.rect.top = plat_rect.bottom
                    self.y_velocity = 0

        # --- 2. Horizontal Logic (Only run if on a platform) ---
        if self.is_on_ground:
            # First, check for edges BEFORE moving.
            # Create a probe just in front of the enemy's feet to see if there's ground to walk on.
            probe_x = self.rect.right if self.direction > 0 else self.rect.left - 1
            ground_probe = pygame.Rect(probe_x, self.rect.bottom, 1, 1)

            found_ground_ahead = False
            current_platform = None # The platform the enemy is currently on

            for plat_rect in platforms:
                if ground_probe.colliderect(plat_rect):
                    found_ground_ahead = True

                # Also check what platform we are currently on for moving platform logic
                probe_under = pygame.Rect(self.rect.centerx, self.rect.bottom, 1, 5)
                if probe_under.colliderect(plat_rect):
                    current_platform = plat_rect

            # If there's no ground ahead, turn around.
            if not found_ground_ahead:
                self.direction *= -1

            # Now, move the enemy horizontally.
            move_x = self.speed * self.direction
            self.rect.x += move_x

            # Handle sticking to a moving platform we might be on
            if current_platform:
                 for p in self.moving_platforms:
                    if p.rect == current_platform:
                        if p.move_direction == 'horizontal':
                            self.rect.x += p.speed * p.direction
                        else: # Gère le mouvement vertical de la plateforme
                            self.rect.y += p.speed * p.direction
                        break

            # Finally, check for collisions with walls after moving.
            for plat_rect in platforms:
                if self.rect.colliderect(plat_rect):
                    if move_x > 0: # Hit a wall while moving right
                        self.rect.right = plat_rect.left
                        self.direction = -1
                    elif move_x < 0: # Hit a wall while moving left
                        self.rect.left = plat_rect.right
                        self.direction = 1

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class MovingPlatform:
    def __init__(self, x, y, width, height, speed, move_range, direction, platform_image):
        self.image = platform_image
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.start_pos = x if direction == 'horizontal' else y
        self.move_range = move_range
        self.direction = 1
        self.move_direction = direction

    def update(self):
        if self.move_direction == 'horizontal':
            self.rect.x += self.speed * self.direction
            if self.rect.x <= self.start_pos or self.rect.x >= self.start_pos + self.move_range:
                self.direction *= -1
        else: # vertical
            self.rect.y += self.speed * self.direction
            if self.rect.y <= self.start_pos or self.rect.y >= self.start_pos + self.move_range:
                self.direction *= -1

    def draw(self, surface):
        for x in range(self.rect.left, self.rect.right, self.image.get_width()):
            surface.blit(self.image, (x, self.rect.top))

class JumpingEnemy:
    def __init__(self, x, y, jump_strength, jump_delay, enemy_image, moving_platforms):
        self.image = enemy_image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.start_y = y
        self.y_velocity = 0
        self.jump_strength = -jump_strength
        self.jump_delay = jump_delay # in milliseconds
        self.last_jump_time = pygame.time.get_ticks()
        self.is_on_ground = False
        self.moving_platforms = moving_platforms

    def update(self, platforms):
        # Apply gravity
        self.y_velocity += GRAVITY
        self.rect.y += self.y_velocity
        self.is_on_ground = False

        # Collision with platforms
        for plat_rect in platforms:
            if self.rect.colliderect(plat_rect):
                if self.y_velocity > 0:
                    self.rect.bottom = plat_rect.top
                    self.is_on_ground = True
                    self.y_velocity = 0
                elif self.y_velocity < 0:
                    self.rect.top = plat_rect.bottom
                    self.y_velocity = 0

        # Move with platform only when on ground
        if self.is_on_ground:
            for p in self.moving_platforms:
                if self.rect.colliderect(p.rect):
                    if p.move_direction == 'horizontal':
                        self.rect.x += p.speed * p.direction
                    else: # Gère le mouvement vertical de la plateforme
                        self.rect.y += p.speed * p.direction
                    break

        # Jumping logic
        now = pygame.time.get_ticks()
        if self.is_on_ground and now - self.last_jump_time > self.jump_delay:
            self.y_velocity = self.jump_strength
            self.last_jump_time = now

    def draw(self, surface):
        surface.blit(self.image, self.rect)

def draw_text_with_outline(surface, text, font, pos, text_color, outline_color):
    x, y = pos; outline_thickness = 2
    outline_surface = font.render(text, True, outline_color)
    for dx in range(-outline_thickness, outline_thickness + 1):
        for dy in range(-outline_thickness, outline_thickness + 1):
            if dx != 0 or dy != 0: surface.blit(outline_surface, (x + dx, y + dy))
    text_surface = font.render(text, True, text_color); surface.blit(text_surface, pos)

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

class PowerUp:
    def __init__(self, x, y):
        self.image = pygame.Surface((30, 30))
        self.image.fill((0, 255, 255)) # Couleur Cyan pour être visible
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, surface):
        surface.blit(self.image, self.rect)
