import pygame

EPS = 1e-6


def _h_overlap(ax, aw, bx, bw):
    """Strict horizontal overlap (touching edges do not count)."""
    return ax < bx + bw and ax + aw > bx


def _v_overlap(ay, ah, by, bh):
    return ay < by + bh and ay + ah > by


class Player:
    def __init__(self, x, y, width=24, height=32):
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height
        self.vx = 0
        self.vy = 0
        self.speed = 4
        self.gravity = 0.5
        self.jump_strength = -12
        self.max_fall_speed = 20      # terminal velocity
        self.on_ground = False
        self.jump_buffer = 0          # frames a jump press stays "remembered"
        self.JUMP_BUFFER_FRAMES = 6

    # ---------------------------------------------------------------- helpers
    def rect(self):
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def apply_difficulty(self, gravity, jump_strength):
        self.gravity = gravity
        self.jump_strength = jump_strength

    def queue_jump(self):
        """Called on a jump key press; it fires as soon as the player can jump."""
        self.jump_buffer = self.JUMP_BUFFER_FRAMES

    def jump(self):
        if self.on_ground:
            self.vy = self.jump_strength
            self.on_ground = False
            return True
        return False

    # ----------------------------------------------------------------- update
    def update(self, platforms, screen_width):
        """Advance one frame. Returns (landed_platform_or_None, jumped_bool)."""
        jumped = False
        if self.jump_buffer > 0:
            self.jump_buffer -= 1
            if self.jump():
                jumped = True
                self.jump_buffer = 0

        self.vy = min(self.vy + self.gravity, self.max_fall_speed)

        self._move_horizontal(platforms, screen_width)
        landed = self._move_vertical(platforms)
        return landed, jumped

    def _move_horizontal(self, platforms, screen_width):
        self.x += self.vx
        for p in platforms:
            if (_h_overlap(self.x, self.width, p.x, p.width)
                    and _v_overlap(self.y, self.height, p.y, p.height)):
                if self.vx > 0:
                    self.x = p.x - self.width
                elif self.vx < 0:
                    self.x = p.x + p.width
        self.x = max(0, min(self.x, screen_width - self.width))

    def _move_vertical(self, platforms):
        """Swept collision: tests the whole path travelled this frame, not just
        the end position, so a fast fall can never skip over a thin platform."""
        prev_top = self.y
        prev_bottom = self.y + self.height
        self.y += self.vy
        new_top = self.y
        new_bottom = self.y + self.height
        self.on_ground = False
        landed = None

        if self.vy >= 0:
            # Falling / standing: find the highest platform top we crossed.
            for p in platforms:
                if not _h_overlap(self.x, self.width, p.x, p.width):
                    continue
                if prev_bottom <= p.y + EPS and new_bottom >= p.y - EPS:
                    if landed is None or p.y < landed.y:
                        landed = p
            if landed is not None:
                self.y = landed.y - self.height
                self.vy = 0
                self.on_ground = True
        else:
            # Rising: bump head on the lowest platform underside we crossed.
            ceiling = None
            for p in platforms:
                if not _h_overlap(self.x, self.width, p.x, p.width):
                    continue
                p_bottom = p.y + p.height
                if prev_top >= p_bottom - EPS and new_top <= p_bottom + EPS:
                    if ceiling is None or p_bottom > ceiling.y + ceiling.height:
                        ceiling = p
            if ceiling is not None:
                self.y = ceiling.y + ceiling.height
                self.vy = 0
        return landed
