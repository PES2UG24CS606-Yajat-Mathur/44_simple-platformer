import pygame
from .player import Player
from .platform import Platform
from .hazard import Hazard
from .sound import SoundManager

# Game Engine

WHITE = (255, 255, 255)
BROWN = (150, 100, 60)
RED = (220, 60, 60)
GREEN = (0, 200, 0)
GOLD = (255, 215, 60)
GREY = (200, 200, 200)

# name -> (gravity, jump_strength)
DIFFICULTIES = {
    "Easy": (0.45, -13),
    "Medium": (0.60, -12),   # same gravity as the original game
    "Hard": (0.80, -11),
}


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.sounds = SoundManager()
        self.font = pygame.font.SysFont("Arial", 30)
        self.font_big = pygame.font.SysFont("Arial", 72, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 22)

        self.quit_requested = False
        self.reset("Medium")

    # ------------------------------------------------------------ setup/reset
    def reset(self, difficulty):
        """Start (or restart) a run at the chosen difficulty."""
        self.difficulty = difficulty
        self.gravity, jump_strength = DIFFICULTIES[difficulty]

        self.start_x, self.start_y = 40, self.height - 120
        self.player = Player(self.start_x, self.start_y)
        self.player.apply_difficulty(self.gravity, jump_strength)

        # A simple hand-built level: platforms with gaps between them
        # (falling into a gap means falling off the bottom of the
        # screen), one hazard, and a goal near the right edge.
        ground_y = self.height - 40
        self.platforms = [
            Platform(0, ground_y, 160),
            Platform(220, ground_y, 140),
            Platform(420, ground_y - 60, 120),
            Platform(600, ground_y, 180),
        ]
        # Narrowed from 100px to 60px so it can be jumped on every
        # difficulty (see README).
        self.hazards = [Hazard(260, ground_y - 14, 60)]
        self.goal_x = 740

        self.score = 0
        self.game_over = False

    # ----------------------------------------------------------------- input
    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_ESCAPE:
            self.quit_requested = True
            return

        if not self.game_over:
            if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                self.player.queue_jump()
        else:
            if event.key in (pygame.K_1, pygame.K_KP1):
                self.reset("Easy")
            elif event.key in (pygame.K_2, pygame.K_KP2):
                self.reset("Medium")
            elif event.key in (pygame.K_3, pygame.K_KP3):
                self.reset("Hard")
            elif event.key == pygame.K_q:
                self.quit_requested = True

    def handle_input(self):
        if self.game_over:
            return
        keys = pygame.key.get_pressed()
        self.player.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.vx = -self.player.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.vx = self.player.speed

    # ---------------------------------------------------------------- update
    def update(self):
        if self.game_over:
            return

        # Swept collision lives in Player.update(): it tests the whole path
        # travelled this frame, so a fast fall can't skip a platform.
        _landed, jumped = self.player.update(self.platforms, self.width)
        if jumped:
            self.sounds.play("jump")

        player_rect = self.player.rect()

        for hazard in self.hazards:
            if player_rect.colliderect(hazard.hitbox()):
                self._die()
                return

        if self.player.y > self.height:
            self._die()
            return

        if self.player.x >= self.goal_x:
            self.score += 1
            self.sounds.play("goal")
            self.player.x, self.player.y = float(self.start_x), float(self.start_y)
            self.player.vx = 0
            self.player.vy = 0

    def _die(self):
        self.game_over = True
        self.player.vx = 0
        self.sounds.play("die")

    # ---------------------------------------------------------------- render
    def render(self, screen):
        for platform in self.platforms:
            pygame.draw.rect(screen, BROWN, platform.rect())
        for hazard in self.hazards:
            pygame.draw.rect(screen, RED, hazard.rect())

        goal_rect = pygame.Rect(self.goal_x, 0, 6, self.height)
        pygame.draw.rect(screen, GREEN, goal_rect)

        pygame.draw.rect(screen, WHITE, self.player.rect())

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        diff_text = self.font_small.render(self.difficulty, True, WHITE)
        screen.blit(diff_text, (12, 46))

        if self.game_over:
            self._render_game_over(screen)

    def _render_game_over(self, screen):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        lines = [
            (self.font_big, "GAME OVER", RED, 110),
            (self.font, f"Final Score: {self.score}", WHITE, 190),
            (self.font_small, "Play again - choose a difficulty:", GREY, 260),
            (self.font, "1 - Easy     2 - Medium     3 - Hard", WHITE, 300),
            (self.font_small, "Press Q or Esc to exit", GREY, 360),
        ]
        for font, text, colour, y in lines:
            surf = font.render(text, True, colour)
            screen.blit(surf, surf.get_rect(center=(self.width // 2, y)))
