import math
from array import array

import pygame


class SoundManager:
    """Generates simple sound effects in code (no asset files needed).
    If no audio device is available the game silently runs without sound."""

    def __init__(self):
        self.enabled = False
        self.sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.rate, fmt, self.channels = pygame.mixer.get_init()
            if fmt != -16:
                return
            self.sounds = {
                "jump": self._make([(300, 650, 0.15, "sine")]),
                "goal": self._make([(523, 523, 0.12, "square"),
                                    (659, 659, 0.12, "square"),
                                    (784, 784, 0.12, "square"),
                                    (1047, 1047, 0.30, "square")]),
                "die": self._make([(420, 70, 0.55, "square")]),
            }
            self.enabled = True
        except (pygame.error, NotImplementedError):
            self.enabled = False

    def _make(self, segments, volume=0.25):
        samples = array("h")
        for f0, f1, dur, wave in segments:
            n = int(self.rate * dur)
            phase = 0.0
            for i in range(n):
                t = i / n
                freq = f0 + (f1 - f0) * t
                phase += 2 * math.pi * freq / self.rate
                s = math.sin(phase)
                if wave == "square":
                    s = 1.0 if s >= 0 else -1.0
                # short fade-in / fade-out to avoid clicks
                edge = min(1.0, i / 100, (n - i) / 300)
                v = int(s * edge * volume * 32767)
                for _ in range(self.channels):
                    samples.append(v)
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def play(self, name):
        if self.enabled and name in self.sounds:
            self.sounds[name].play()
