import pygame
from .player import Player
from .platform import Platform
from .hazard import Hazard

# Game Engine

WHITE = (255, 255, 255)
BROWN = (150, 100, 60)
RED = (220, 60, 60)
GREEN = (0, 200, 0)
GREY = (200, 200, 200)

# NEW: difficulty name -> (gravity, jump_strength)
# Medium keeps the original game's values (gravity 0.6, jump -12).
DIFFICULTIES = {
    "Easy": (0.45, -13),
    "Medium": (0.60, -12),
    "Hard": (0.70, -12),
}

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.font = pygame.font.SysFont("Arial", 30)
        self.font_big = pygame.font.SysFont("Arial", 72, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 22)

        # CHANGED: level/player/score setup moved into reset() so the game
        # can be restarted after Game Over.
        self.reset("Medium")

    # NEW
    def reset(self, difficulty):
        """(Re)start the game with the chosen difficulty."""
        self.difficulty = difficulty
        self.gravity, jump_strength = DIFFICULTIES[difficulty]

        self.start_x, self.start_y = 40, self.height - 120
        self.player = Player(self.start_x, self.start_y)
        self.player.jump_strength = jump_strength

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
        self.hazards = [Hazard(240, ground_y - 14, 100)]
        self.goal_x = 740

        self.score = 0
        self.game_over = False

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        # CHANGED: on the Game Over screen, 1/2/3 restart on Easy/Medium/Hard
        # and Q or Esc exits (a normal QUIT event, handled by main.py).
        if self.game_over:
            if event.key in (pygame.K_1, pygame.K_KP1):
                self.reset("Easy")
            elif event.key in (pygame.K_2, pygame.K_KP2):
                self.reset("Medium")
            elif event.key in (pygame.K_3, pygame.K_KP3):
                self.reset("Hard")
            elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            return

        if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
            self.player.jump()

    def handle_input(self):
        if self.game_over:
            return
        keys = pygame.key.get_pressed()
        self.player.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.vx = -self.player.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.vx = self.player.speed

    def update(self):
        if self.game_over:
            return

        self.player.vy += self.gravity
        self.player.x = max(0, self.player.x + self.player.vx)

        # (collision block unchanged from your original - Task 1 replaces it)
        self.player.y += self.player.vy
        self.player.on_ground = False
        for platform in self.platforms:
            if self.player.rect().colliderect(platform.rect()) and self.player.vy >= 0:
                self.player.y = platform.y - self.player.height
                self.player.vy = 0
                self.player.on_ground = True

        for hazard in self.hazards:
            if self.player.rect().colliderect(hazard.rect()):
                self.game_over = True
                return

        if self.player.y > self.height:
            self.game_over = True
            return

        if self.player.x >= self.goal_x:
            self.score += 1
            self.player.x, self.player.y = self.start_x, self.start_y
            self.player.vy = 0

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
        # NEW: show the current difficulty under the score
        diff_text = self.font_small.render(self.difficulty, True, WHITE)
        screen.blit(diff_text, (12, 46))

        if self.game_over:
            self.render_game_over(screen)

    def render_game_over(self, screen):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        # CHANGED: the prompt now offers replay options instead of "exit"
        cy = self.height // 2
        lines = [
            (self.font_big, "GAME OVER", RED, cy - 110),
            (self.font, f"Final Score: {self.score}", WHITE, cy - 40),
            (self.font_small, "Play again - choose a difficulty:", GREY, cy + 20),
            (self.font, "1 - Easy     2 - Medium     3 - Hard", WHITE, cy + 60),
            (self.font_small, "Press Q or Esc to exit", GREY, cy + 115),
        ]
        for font, text, colour, y in lines:
            surf = font.render(text, True, colour)
            screen.blit(surf, surf.get_rect(center=(self.width // 2, y)))