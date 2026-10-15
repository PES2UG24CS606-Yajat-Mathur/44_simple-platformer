import pygame


class Hazard:
    def __init__(self, x, y, width, height=14):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def hitbox(self):
        """Slightly smaller than the drawn spikes so deaths feel fair."""
        return self.rect().inflate(-4, -2)
