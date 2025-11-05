import pygame
from settings import *
from sprites import Player, Enemy, MovingPlatform, JumpingEnemy, Button, draw_text_with_outline
from levels import LEVELS

class Game:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except pygame.error as e:
            print(f"Avertissement: Impossible d'initialiser le mixer audio : {e}")

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Loris L'Astronaute")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = "start_screen"
        self.load_assets()

    def load_assets(self):
        # Images
        self.player_image = self.load_image("player.png", (40, 50), RED)
        self.platform_image = self.load_image("platform.png", (40, 40), (0, 255, 0))
        self.coin_image = self.load_image("coin.png", (30, 30), (255, 223, 0))
        self.enemy_image = self.load_image("enemy.png", (40, 40), (150, 0, 255))
        background = self.load_image("background.png", (SCREEN_WIDTH, SCREEN_HEIGHT), BLACK, is_background=True)
        self.background_image = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Sons
        self.jump_sound = self.load_sound("jump.ogg")
        self.coin_sound = self.load_sound("coin.ogg")
        self.enemy_stomp_sound = self.load_sound("stomp.ogg")
        try:
            pygame.mixer.music.load(os.path.join(SOUNDS_PATH, "music.mp3"))
            pygame.mixer.music.play(-1)
        except pygame.error:
            print("Avertissement: La musique 'music.mp3' n'a pas été trouvée.")

        # Polices
        self.font = pygame.font.Font(None, 74)
        self.big_font = pygame.font.Font(None, 80)
        self.small_font = pygame.font.Font(None, 36)
        self.score_font = pygame.font.Font(None, 40)
        self.button_font = pygame.font.Font(None, 50)

    def load_image(self, filename, size, color, is_background=False):
        filepath = os.path.join(ASSETS_PATH, filename)
        try:
            image = pygame.image.load(filepath)
            return image.convert_alpha() if not is_background else image.convert()
        except (pygame.error, FileNotFoundError):
            print(f"Avertissement: L'image '{filename}' n'a pas été trouvée. Placeholder utilisé.")
            surface = pygame.Surface(size)
            surface.fill(color)
            return surface

    def load_sound(self, filename):
        filepath = os.path.join(SOUNDS_PATH, filename)
        try:
            return pygame.mixer.Sound(filepath)
        except (pygame.error, FileNotFoundError):
            print(f"Avertissement: Le son '{filename}' n'a pas été trouvé.")
            class DummySound:
                def play(self): pass
            return DummySound()

    def reset_game(self):
        self.score = 0
        self.player_lives = 3
        # self.unlocked_levels = 1 # This is now handled by load_progress
        self.infinite_lives = False
        self.current_level_index = 0
        self.load_level(self.current_level_index)
        self.game_state = "playing"
        self.start_time = pygame.time.get_ticks()

    def load_level(self, level_index):
        self.platform_rects = []
        self.moving_platforms = []
        self.coin_rects = []
        self.enemies = []
        self.jumping_enemies = []
        self.powerups = []

        level_data = LEVELS[level_index]

        self.platform_rects = [pygame.Rect(p[0], p[1], p[2], p[3]) for p in level_data.get("platforms", [])]

        for p in level_data.get("moving_platforms", []):
            self.moving_platforms.append(MovingPlatform(p[0], p[1], p[2], p[3], p[4], p[5], p[6], self.platform_image))

        self.coin_rects = [self.coin_image.get_rect(topleft=pos) for pos in level_data.get("coins", [])]

        for e in level_data.get("enemies", []):
            self.enemies.append(Enemy(e[0], e[1], e[2], e[3], self.enemy_image, self.moving_platforms))

        for e in level_data.get("jumping_enemies", []):
            self.jumping_enemies.append(JumpingEnemy(e[0], e[1], e[2], e[3], self.enemy_image, self.moving_platforms))

        for p in level_data.get("powerups", []):
            self.powerups.append(PowerUp(p[0], p[1]))

        self.player = Player(380, 0, self.player_image, self.jump_sound)


    def handle_player_death(self):
        if not self.infinite_lives:
            self.player_lives -= 1
        if self.player_lives > 0 or self.infinite_lives:
            self.load_level(self.current_level_index)
        else:
            self.game_state = "game_over"

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def events(self):
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.game_state == "start_screen":
                if self.play_button.check_click(event): self.game_state = "level_select"
                if self.credits_button.check_click(event): self.game_state = "credits_screen"
            elif self.game_state == "level_select":
                if self.back_button.check_click(event): self.game_state = "start_screen"
                for i, button in enumerate(self.level_buttons):
                    if i < self.unlocked_levels and button.check_click(event):
                        self.current_level_index = i
                        self.load_level(self.current_level_index)
                        self.game_state = "playing"
                        self.start_time = pygame.time.get_ticks()
            elif self.game_state == "credits_screen":
                if self.back_button.check_click(event): self.game_state = "start_screen"
            elif self.game_state == "game_over":
                if self.restart_button.check_click(event): self.reset_game()
                if self.main_menu_button.check_click(event): self.game_state = "start_screen"

            if self.game_state == "playing":
                self.player.handle_input(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i: self.infinite_lives = not self.infinite_lives
                if self.game_state == "won" and event.key == pygame.K_r: self.reset_game()

    def update(self):
        if self.game_state == "playing":
            keys = pygame.key.get_pressed()
            all_platforms = self.platform_rects + [p.rect for p in self.moving_platforms]

            # Update all sprites
            self.player.update(keys, all_platforms, self.moving_platforms)
            for p in self.moving_platforms: p.update()
            for enemy in self.enemies: enemy.update(all_platforms)
            for enemy in self.jumping_enemies: enemy.update(all_platforms)

            # Check collisions
            for i, enemy in reversed(list(enumerate(self.enemies))):
                if self.player.rect.colliderect(enemy.rect):
                    # Condition plus généreuse : le joueur doit être en train de tomber et ses pieds doivent être au-dessus du haut de l'ennemi
                    if self.player.y_velocity > 0 and self.player.rect.bottom <= enemy.rect.top + 10:
                        self.enemies.pop(i)
                        self.enemy_stomp_sound.play()
                        self.player.y_velocity = BOUNCE_STRENGTH
                    else:
                        self.handle_player_death()

            for i, enemy in reversed(list(enumerate(self.jumping_enemies))):
                if self.player.rect.colliderect(enemy.rect):
                    # Condition plus généreuse : le joueur doit être en train de tomber et ses pieds doivent être au-dessus du haut de l'ennemi
                    if self.player.y_velocity > 0 and self.player.rect.bottom <= enemy.rect.top + 10:
                        self.jumping_enemies.pop(i)
                        self.enemy_stomp_sound.play()
                        self.player.y_velocity = BOUNCE_STRENGTH
                    else:
                        self.handle_player_death()

            coin_index = self.player.rect.collidelist(self.coin_rects)
            if coin_index != -1:
                self.coin_rects.pop(coin_index)
                self.score += 1
                self.coin_sound.play()

            # Check for power-up collision
            for i, powerup in reversed(list(enumerate(self.powerups))):
                if self.player.rect.colliderect(powerup.rect):
                    self.powerups.pop(i)
                    self.player.has_double_jump = True

            # Check for death or level completion
            if self.player.rect.top > SCREEN_HEIGHT:
                self.handle_player_death()

            if not self.coin_rects:
                self.current_level_index += 1
                if self.current_level_index < len(LEVELS):
                    if self.current_level_index >= self.unlocked_levels:
                        self.unlocked_levels = self.current_level_index + 1
                        self.save_progress()
                    self.load_level(self.current_level_index)
                else:
                    self.game_state = "won"

    def save_progress(self):
        with open(SAVE_FILE, "w") as f:
            f.write(str(self.unlocked_levels))

    def load_progress(self):
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r") as f:
                try:
                    self.unlocked_levels = int(f.read())
                except ValueError:
                    self.unlocked_levels = 1 # Fallback in case of corrupted file
        else:
            self.unlocked_levels = 1

    def draw(self):
        self.screen.blit(self.background_image, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        if self.game_state == "start_screen":
            self.draw_start_screen(mouse_pos)
        elif self.game_state == "level_select":
            self.draw_level_select_screen(mouse_pos)
        elif self.game_state == "credits_screen":
            self.draw_credits_screen(mouse_pos)
        elif self.game_state == "playing" or self.game_state == "won":
             self.draw_playing_screen()
        elif self.game_state == "game_over":
            self.draw_game_over_screen(mouse_pos)

        pygame.display.flip()

    def setup_buttons(self):
        self.play_button = Button(300, 250, 200, 50, "Jouer", self.button_font, BUTTON_BASE_COLOR, BUTTON_HOVER_COLOR)
        self.credits_button = Button(300, 320, 200, 50, "Crédits", self.button_font, BUTTON_BASE_COLOR, BUTTON_HOVER_COLOR)
        self.back_button = Button(300, 500, 200, 50, "Retour", self.button_font, BUTTON_BASE_COLOR, BUTTON_HOVER_COLOR)
        self.restart_button = Button(300, 250, 200, 50, "Recommencer", self.button_font, BUTTON_BASE_COLOR, BUTTON_HOVER_COLOR)
        self.main_menu_button = Button(300, 320, 200, 50, "Menu Principal", self.button_font, BUTTON_BASE_COLOR, BUTTON_HOVER_COLOR)

        self.level_buttons = []
        for i in range(len(LEVELS)):
            x = 150 + (i % 4) * 150
            y = 200 + (i // 4) * 100
            self.level_buttons.append(Button(x, y, 100, 50, f"Niv {i+1}", self.button_font, BUTTON_BASE_COLOR, BUTTON_HOVER_COLOR))

    def draw_start_screen(self, mouse_pos):
        title_rect = self.big_font.render("Loris L'Astronaute", True, BLACK).get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 100))
        draw_text_with_outline(self.screen, "Loris L'Astronaute", self.big_font, title_rect.topleft, WHITE, BLACK)
        self.play_button.check_hover(mouse_pos); self.play_button.draw(self.screen)
        self.credits_button.check_hover(mouse_pos); self.credits_button.draw(self.screen)

    def draw_level_select_screen(self, mouse_pos):
        title_rect = self.big_font.render("Sélection du Niveau", True, BLACK).get_rect(center=(SCREEN_WIDTH / 2, 100))
        draw_text_with_outline(self.screen, "Sélection du Niveau", self.big_font, title_rect.topleft, WHITE, BLACK)
        for i, button in enumerate(self.level_buttons):
            if i < self.unlocked_levels:
                button.check_hover(mouse_pos)
                button.base_color, button.hover_color = BUTTON_BASE_COLOR, BUTTON_HOVER_COLOR
            else:
                button.base_color, button.hover_color = BUTTON_LOCKED_COLOR, BUTTON_LOCKED_COLOR
            button.draw(self.screen)
        self.back_button.check_hover(mouse_pos); self.back_button.draw(self.screen)

    def draw_credits_screen(self, mouse_pos):
        credits_title_rect = self.big_font.render("Crédits", True, BLACK).get_rect(center=(SCREEN_WIDTH / 2, 100))
        draw_text_with_outline(self.screen, "Crédits", self.big_font, credits_title_rect.topleft, WHITE, BLACK)
        credits_text = ["Jeu développé par : Vous !", "Idée originale : Loris", "Moteur de jeu : Pygame"]
        for i, line in enumerate(credits_text):
            line_rect = self.small_font.render(line, True, BLACK).get_rect(center=(SCREEN_WIDTH / 2, 250 + i * 40))
            draw_text_with_outline(self.screen, line, self.small_font, line_rect.topleft, WHITE, BLACK)
        self.back_button.check_hover(mouse_pos); self.back_button.draw(self.screen)

    def draw_playing_screen(self):
        # Draw platforms, coins, and enemies
        for plat_rect in self.platform_rects:
            for x in range(plat_rect.left, plat_rect.right, self.platform_image.get_width()):
                self.screen.blit(self.platform_image, (x, plat_rect.top))
        for p in self.moving_platforms: p.draw(self.screen)
        for coin in self.coin_rects: self.screen.blit(self.coin_image, coin)
        for enemy in self.enemies: enemy.draw(self.screen)
        for enemy in self.jumping_enemies: enemy.draw(self.screen)
        for powerup in self.powerups: powerup.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw HUD
        elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
        draw_text_with_outline(self.screen, f"Score: {self.score}", self.score_font, (10, 10), WHITE, BLACK)
        lives_text = "Vies: ∞" if self.infinite_lives else f"Vies: {self.player_lives}"
        draw_text_with_outline(self.screen, lives_text, self.score_font, (10, 50), WHITE, BLACK)
        draw_text_with_outline(self.screen, f"Niveau: {self.current_level_index + 1}", self.score_font, (SCREEN_WIDTH - 150, 10), WHITE, BLACK)
        timer_text = f"Temps: {elapsed_time}"
        timer_rect = self.score_font.render(timer_text, True, BLACK).get_rect(centerx=SCREEN_WIDTH/2); timer_rect.top = 10
        draw_text_with_outline(self.screen, timer_text, self.score_font, timer_rect.topleft, WHITE, BLACK)

        if self.game_state == "won":
            win_rect = self.font.render("Gagné !", True, BLACK).get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 20))
            draw_text_with_outline(self.screen, "Gagné !", self.font, win_rect.topleft, WHITE, BLACK)
            final_time_text = f"Votre temps: {elapsed_time}s"
            final_time_rect = self.small_font.render(final_time_text, True, BLACK).get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 30))
            draw_text_with_outline(self.screen, final_time_text, self.small_font, final_time_rect.topleft, WHITE, BLACK)
            restart_rect = self.small_font.render("Appuyez sur R pour recommencer", True, BLACK).get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 70))
            draw_text_with_outline(self.screen, "Appuyez sur R pour recommencer", self.small_font, restart_rect.topleft, WHITE, BLACK)

    def draw_game_over_screen(self, mouse_pos):
        game_over_rect = self.big_font.render("Game Over", True, BLACK).get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 100))
        draw_text_with_outline(self.screen, "Game Over", self.big_font, game_over_rect.topleft, RED, BLACK)
        self.restart_button.check_hover(mouse_pos); self.restart_button.draw(self.screen)
        self.main_menu_button.check_hover(mouse_pos); self.main_menu_button.draw(self.screen)

if __name__ == '__main__':
    game = Game()
    game.setup_buttons()
    game.load_progress()
    game.reset_game()
    game.run()
    pygame.quit()
