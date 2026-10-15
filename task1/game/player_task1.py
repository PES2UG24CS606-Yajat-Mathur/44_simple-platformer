import pygame

EPS = 1e-6


def _h_overlap(ax, aw, bx, bw):
    """True if two horizontal spans overlap (touching edges don't count)."""
    return ax < bx + bw and ax + aw > bx


def _v_overlap(ay, ah, by, bh):
    """True if two vertical spans overlap (touching edges don't count)."""
    return ay < by + bh and ay + ah > by


class Player:
    def __init__(self, x, y, width=24, height=32):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vx = 0
        self.vy = 0
        self.speed = 4
        self.jump_strength = -12
        self.max_fall_speed = 20   # NEW: terminal velocity
        self.on_ground = False

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def jump(self):
        if self.on_ground:
            self.vy = self.jump_strength
            self.on_ground = False

    # ------------------------------------------------------------------ NEW
    def move_horizontal(self, platforms):
        """Move along x and stop at the side of any platform we run into."""
        self.x = max(0, self.x + self.vx)
        for p in platforms:
            if (_h_overlap(self.x, self.width, p.x, p.width)
                    and _v_overlap(self.y, self.height, p.y, p.height)):
                if self.vx > 0:
                    self.x = p.x - self.width
                elif self.vx < 0:
                    self.x = p.x + p.width

    def move_vertical(self, platforms):
        """Swept vertical collision: compare the position BEFORE and AFTER the
        move and land on any platform top that was crossed on the way."""
        self.vy = min(self.vy, self.max_fall_speed)

        prev_top = self.y
        prev_bottom = self.y + self.height
        self.y += self.vy
        new_top = self.y
        new_bottom = self.y + self.height
        self.on_ground = False

        if self.vy >= 0:
            # Falling (or standing): land on the highest top we crossed.
            landed = None
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
            # Rising: bump the head on the lowest underside we crossed.
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